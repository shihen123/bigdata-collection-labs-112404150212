"""实验一 可复用爬虫内核。

把两个案例中重复的部分抽出来：请求、重试、编码、落盘、日志、脱敏。
业务解析规则不放在这里（那属于具体站点，写在 notebook 中）。
"""

from __future__ import annotations

import json
import logging
import re
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

import requests

from config import BASE_DIR, DEFAULT_HEADERS, LOG_DIR, RETRIES, TIMEOUT

CST = timezone(timedelta(hours=8))


class FetchError(RuntimeError):
    """请求层统一异常：重试耗尽后抛出，调用方据此区分“网络失败”与“业务失败”。"""


# ---------------------------------------------------------------- 日志


def setup_logger(name: str = "lab01", log_file: Path | None = None) -> logging.Logger:
    """控制台 + 文件双输出。重复调用不会重复添加 handler。"""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)

    log_file = log_file or (LOG_DIR / "lab01.log")
    ensure_dir(Path(log_file).parent)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    return logger


# ---------------------------------------------------------------- 路径与落盘


def ensure_dir(path: Path) -> Path:
    """幂等创建目录。"""
    Path(path).mkdir(parents=True, exist_ok=True)
    return Path(path)


def save_image(path: Path, content: bytes) -> Path:
    """写入图片二进制。对应教材的 save_image(path, content)。"""
    path = Path(path)
    ensure_dir(path.parent)
    path.write_bytes(content)
    return path


def save_text(text: str, path: Path, encoding: str = "utf-8") -> Path:
    """写入文本（html 源码），统一 UTF-8。"""
    path = Path(path)
    ensure_dir(path.parent)
    path.write_text(text, encoding=encoding)
    return path


def save_json(obj: Any, path: Path) -> Path:
    """UTF-8 落盘 JSON，保留中文可读。"""
    path = Path(path)
    ensure_dir(path.parent)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


# ---------------------------------------------------------------- 请求


def fetch(
    url: str,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: tuple[float, float] = TIMEOUT,
    retries: int = RETRIES,
    encoding: str | None = None,
) -> requests.Response:
    """统一请求入口：UA、超时、重试、状态码校验、编码修正。

    encoding="apparent" 时按响应字节自动推断编码（教材 3.5.3 的写法）。
    """
    hdrs = {**DEFAULT_HEADERS, **(headers or {})}
    last_err: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, params=params, headers=hdrs, timeout=timeout)
            resp.raise_for_status()          # 4xx / 5xx 主动抛 HTTPError
            if encoding == "apparent":
                resp.encoding = resp.apparent_encoding
            elif encoding:
                resp.encoding = encoding
            return resp
        except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as err:
            last_err = err
            if attempt < retries:
                time.sleep(1.5 * attempt)    # 1.5s → 3s 递增

    raise FetchError(f"请求失败（{retries} 次尝试后）：{url} → {last_err}") from last_err


def get_image(url: str, headers: dict | None = None) -> tuple[bytes, int]:
    """取单张图片的二进制数据。对应教材的 get_image(url)，额外回传字节数。"""
    resp = fetch(url, headers=headers)
    data = resp.content                    # 二进制用 content，不用 text
    if not data:
        raise FetchError(f"空响应：{url}")
    return data, len(data)


def get_html(url: str, headers: dict | None = None, params: dict | None = None) -> str:
    """取网页文本。对应教材的 get_html(url)，编码统一走 apparent_encoding。"""
    resp = fetch(url, params=params, headers=headers, encoding="apparent")
    return resp.text


# ---------------------------------------------------------------- 杂项


def sanitize(name: str, maxlen: int = 40) -> str:
    """清洗文件名中的非法字符。"""
    cleaned = re.sub(r'[\\/:*?"<>|\r\n\t]', "_", str(name)).strip(" .")
    cleaned = re.sub(r"_{2,}", "_", cleaned)
    return cleaned[:maxlen] or "unnamed"


def mask_phone(phone: str) -> str:
    """手机号脱敏：19352204881 → 193****4881。"""
    phone = str(phone).strip()
    return phone[:3] + "*" * (len(phone) - 7) + phone[-4:] if len(phone) >= 8 else phone


def now_iso() -> str:
    """带 +08:00 时区的 ISO 8601 时间戳。"""
    return datetime.now(CST).replace(microsecond=0).isoformat()


def rel(path: Path) -> str:
    """转成相对 lab01/ 的路径字符串（统一用 /），用于写入 JSON，保证跨平台可读。"""
    try:
        return Path(path).resolve().relative_to(BASE_DIR).as_posix()
    except ValueError:
        return str(path)
