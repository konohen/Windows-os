"""
工具函数模块
提供各种辅助功能
"""

import random
import time
from typing import List, Dict, Any


def generate_random_name(prefix="进程"):
    """生成随机进程名称"""
    adjectives = ["快速", "强大", "智能", "高效", "稳定", "可靠", "灵活", "安全"]
    nouns = ["计算", "网络", "存储", "显示", "输入", "输出", "管理", "服务"]

    adj = random.choice(adjectives)
    noun = random.choice(nouns)
    return f"{prefix}{adj}{noun}"


def format_time(seconds):
    """格式化时间显示"""
    if seconds < 1:
        return f"{seconds * 1000:.0f}毫秒"
    elif seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:.0f}分{secs:.0f}秒"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours:.0f}小时{minutes:.0f}分"


def print_table(data: List[Dict[str, Any]], title=""):
    """打印表格"""
    if not data:
        print("没有数据")
        return

    # 获取表头
    headers = list(data[0].keys())

    # 计算每列的最大宽度
    col_widths = {}
    for header in headers:
        max_width = len(str(header))
        for row in data:
            width = len(str(row.get(header, "")))
            if width > max_width:
                max_width = width
        col_widths[header] = max_width

    # 打印标题
    if title:
        total_width = sum(col_widths.values()) + len(headers) * 3 + 1
        print(f"\n{title:^{total_width}}")

    # 打印表头
    header_line = " | ".join(f"{header:^{col_widths[header]}}" for header in headers)
    separator = "-+-".join("-" * col_widths[header] for header in headers)
    print(f"\n{header_line}")


    # 打印数据行
    for row in data:
        row_line = " | ".join(f"{str(row.get(header, '')):<{col_widths[header]}}" for header in headers)
        print(row_line)


def animate_loading(text="加载中", duration=2):
    """显示加载动画"""
    start_time = time.time()
    dots = 0

    while time.time() - start_time < duration:
        dots = (dots + 1) % 4
        loading_text = text + "." * dots + " " * (3 - dots)
        print(f"\r{loading_text}", end="", flush=True)
        time.sleep(0.3)

    print(f"\r{text}完成！{' ' * 10}")


def ask_yes_no(question, default=True):
    """询问是/否问题"""
    choices = "([Y]/n)" if default else "(y/[N])"

    while True:
        answer = input(f"{question} {choices}: ").strip().lower()

        if answer == "":
            return default
        elif answer in ["y", "yes", "是"]:
            return True
        elif answer in ["n", "no", "否"]:
            return False
        else:
            print("请输入 y/n 或 是/否")


def get_int_input(prompt, min_val=None, max_val=None, default=None):
    """获取整数输入"""
    while True:
        try:
            value = input(prompt)

            if default is not None and value == "":
                return default

            value = int(value)

            if min_val is not None and value < min_val:
                print(f"值不能小于 {min_val}")
                continue

            if max_val is not None and value > max_val:
                print(f"值不能大于 {max_val}")
                continue

            return value

        except ValueError:
            print("请输入一个有效的数字")


def get_float_input(prompt, min_val=None, max_val=None, default=None):
    """获取浮点数输入"""
    while True:
        try:
            value = input(prompt)

            if default is not None and value == "":
                return default

            value = float(value)

            if min_val is not None and value < min_val:
                print(f"值不能小于 {min_val}")
                continue

            if max_val is not None and value > max_val:
                print(f"值不能大于 {max_val}")
                continue

            return value

        except ValueError:
            print("请输入一个有效的数字")


def clear_screen():
    """清屏"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')