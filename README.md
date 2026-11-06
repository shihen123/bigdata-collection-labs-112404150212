# 大数据采集与处理实验

- 姓名：洪英杰
- 学号：112404150212
- 班级：软件工程1242班
- GitHub 用户名：shihen123
- 仓库地址：https://github.com/shihen123/bigdata-collection-labs-112404150212

## 实验目录

| 实验 | 主题 | 入口 |
| --- | --- | --- |
| lab01 | 静态网页爬取（QQ 表情包下载 + 手机归属地查询） | [lab01/REPORT.md](lab01/REPORT.md) |

## 目录说明

```text
lab01/
├── lab1_html_api.ipynb    实验主程序（Restart Kernel → Run All 即可复现）
├── REPORT.md              实验报告（含 4 张证据截图）
├── config.py              路径、站点、超时等集中配置
├── spider_utils.py        可复用爬虫内核（请求 / 落盘 / 日志 / 脱敏）
├── run_lab01.py           命令行入口，等价于 Run All
├── data/                  devices.json（下载清单）、companies.json（归属地记录）
├── images/                4 张报告截图
├── output/                运行产物：表情包图片、mobile_query.html（不入库）
└── logs/                  运行日志（不入库）
```

## 运行方式

```bash
# 1. 安装依赖（使用仓库所在项目的虚拟环境）
python -m pip install requests jupyterlab nbconvert ipykernel
python -m ipykernel install --user --name lab01 --display-name "Python (lab01)"

# 2. 配置被测手机号（不入库，二选一）
#    方式 A：环境变量  LAB01_PHONE
#    方式 B：把号码写入 lab01/.phone.local

# 3. 运行
python lab01/run_lab01.py --task all
```

也可直接用 PyCharm / JupyterLab 打开 `lab01/lab1_html_api.ipynb`，选择内核 `Python (lab01)` 后
`Restart Kernel and Run All`。
