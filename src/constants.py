"""
常量定义模块
用于定义程序中使用的枚举和常量
"""

from enum import Enum

class ProcessState(Enum):
    """进程状态枚举"""
    NEW = "新建"       # 进程刚刚创建
    READY = "就绪"     # 进程准备运行，等待CPU
    RUNNING = "运行"   # 进程正在CPU上执行
    WAITING = "阻塞"   # 进程等待资源（如I/O）
    TERMINATED = "终止"  # 进程执行完成

class ScheduleAlgorithm(Enum):
    """调度算法枚举"""
    FCFS = "先来先服务"
    SJF = "短作业优先"
    PRIORITY = "优先级调度"
    RR = "时间片轮转"

class MemoryAlgorithm(Enum):
    """内存分配算法枚举"""
    FIRST_FIT = "首次适应"
    BEST_FIT = "最佳适应"
    WORST_FIT = "最坏适应"

# 系统常量
DEFAULT_MEMORY_SIZE = 512  # 默认内存大小（MB）
DEFAULT_TIME_SLICE = 1.0   # 默认时间片大小（秒）
MAX_PRIORITY = 10          # 最大优先级值（1最高，10最低）

def print_separator(title=""):
    line = "->" + " " * 46 + "<-"
    if title:
        print(f"\n{line}")
        print(f">> {title:^44} <<")
        print(f"{line}")
    else:
        print(f"\n{line}")