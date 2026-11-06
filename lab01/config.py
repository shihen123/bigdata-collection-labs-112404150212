"""实验一 全局配置。

所有路径均以本文件所在目录（lab01/）为锚点派生，仓库整体搬到其他机器后无需改代码。

隐私约定：被测手机号的完整值不写入本文件，也不入库。
优先读环境变量 LAB01_PHONE，其次读同目录下被 .gitignore 忽略的 .phone.local。
"""

from __future__ import annotations

import os
from pathlib import Path

# ---------- 路径 ----------
BASE_DIR = Path(__file__).resolve().parent      # lab01/
DATA_DIR = BASE_DIR / "data"
IMAGE_DIR = BASE_DIR / "images"
OUTPUT_DIR = BASE_DIR / "output"
EMOJI_DIR = OUTPUT_DIR / "qq_emojis"
LOG_DIR = BASE_DIR / "logs"

# ---------- 目标站点 ----------
# 任务1：课程镜像站“表情党”列表页（教材 3.4.1）
LIST_URL = "http://www.bspider.top/yh31/"
# 任务2：真正返回查询结果的地址（教材 3.5.2 / 3.5.3）
# 注意：镜像站 http://www.bspider.top/ip138/ 只是表单页副本，带参数请求仍返回表单，不能用于取结果
IP138_URL = "https://www.ip138.com/mobile.asp"
MIRROR_IP138 = "http://www.bspider.top/ip138/"   # 仅作接口变更时的手工核对入口

# ---------- 请求参数 ----------
DOWNLOAD_LIMIT = 20            # 下载图片数量
TIMEOUT = (5, 15)              # (连接超时, 读取超时) 秒
RETRIES = 3                    # 单个请求最大尝试次数
POLITE_DELAY = 0.3             # 每张图片之间的间隔，避免对站点造成压力

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

HEADERS_TASK1 = {**DEFAULT_HEADERS, "Referer": LIST_URL}
HEADERS_TASK2 = {**DEFAULT_HEADERS, "Referer": "https://www.ip138.com/"}


def target_phone() -> str:
    """返回被测手机号（完整值）。

    读取顺序：环境变量 LAB01_PHONE → lab01/.phone.local → 报错。
    """
    env = os.getenv("LAB01_PHONE", "").strip()
    if env:
        return env

    local_file = BASE_DIR / ".phone.local"
    if local_file.exists():
        value = local_file.read_text(encoding="utf-8").strip()
        if value:
            return value

    raise RuntimeError(
        "未配置被测手机号：请设置环境变量 LAB01_PHONE，"
        f"或在 {local_file} 中写入手机号（该文件已被 .gitignore 忽略，不会入库）。"
    )


if __name__ == "__main__":  # 便于在 PyCharm 里单独运行本文件做自检
    from spider_utils import mask_phone

    print(f"BASE_DIR   = {BASE_DIR}")
    print(f"LIST_URL   = {LIST_URL}")
    print(f"IP138_URL  = {IP138_URL}")
    try:
        print(f"手机号（脱敏） = {mask_phone(target_phone())}")
    except RuntimeError as err:
        print(f"手机号未配置：{err}")
