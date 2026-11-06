"""命令行入口：在 PyCharm 里右键运行本文件，等价于 notebook 的 Restart Kernel → Run All。

用法：
    python run_lab01.py              # 全量执行（默认）
    python run_lab01.py --task 1     # 只跑任务一（表情包下载）
    python run_lab01.py --task 2     # 只跑任务二（归属地查询）

实现说明：不重复实现爬取逻辑，而是调用 nbclient 执行 lab1_html_api.ipynb，
执行结果（输出、执行计数）回写到同一个 notebook，保证「屏幕结果」与「文件内容」一致。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

BASE_DIR = Path(__file__).resolve().parent
NB_PATH = BASE_DIR / "lab1_html_api.ipynb"

# notebook 内的 cell 分组（按生成顺序固定）
GROUPS = {
    "setup": [0, 1],
    "task1": [2, 3, 4, 5],
    "task2": [6, 7, 8, 9],
    "check": [10, 11],
}
PLAN = {
    "1": ["setup", "task1"],
    "2": ["setup", "task2"],
    "all": ["setup", "task1", "task2", "check"],
}


def main() -> int:
    parser = argparse.ArgumentParser(description="运行实验一 notebook")
    parser.add_argument("--task", choices=["1", "2", "all"], default="all",
                        help="1=表情包下载，2=归属地查询，all=全部（默认）")
    parser.add_argument("--timeout", type=int, default=600, help="单 cell 超时秒数")
    args = parser.parse_args()

    nb = nbformat.read(NB_PATH, as_version=4)
    indices = sorted({i for g in PLAN[args.task] for i in GROUPS[g]})

    sub = nbformat.v4.new_notebook(metadata=nb.metadata)
    sub.cells = [nb.cells[i] for i in indices]

    print(f"执行 {NB_PATH.name}，任务={args.task}，共 {len(sub.cells)} 个 cell")
    client = NotebookClient(sub, timeout=args.timeout, kernel_name="lab01",
                            resources={"metadata": {"path": str(BASE_DIR)}})
    try:
        client.execute()
    except CellExecutionError as err:
        print(f"\n执行失败：\n{err}", file=sys.stderr)
        return 1
    finally:
        # 无论成败，把已执行 cell 的输出回写主 notebook，便于在 IDE 中直接看到结果
        for pos, idx in enumerate(indices):
            nb.cells[idx]["outputs"] = sub.cells[pos].get("outputs", [])
            nb.cells[idx]["execution_count"] = sub.cells[pos].get("execution_count")
        nbformat.write(nb, NB_PATH)

    print("执行完成，产物位于：", BASE_DIR / "output")
    return 0


if __name__ == "__main__":
    sys.exit(main())
