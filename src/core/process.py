"""
进程管理模块
定义进程类和相关操作
"""

import time
from ..constants import ProcessState


class Process:
    """进程类 - 最简单的进程控制块"""

    # 类变量，用于自动生成PID
    _next_pid = 1

    def __init__(self, name=None, burst_time=5, priority=5, memory_needed=50):
        """
        初始化一个进程

        参数:
        name: 进程名称
        burst_time: 需要的执行时间
        priority: 优先级（1最高，10最低）
        memory_needed: 需要的内存大小(MB)
        """
        # 进程标识
        self.pid = Process._next_pid
        Process._next_pid += 1
        self.name = name or f"进程{self.pid}"

        # 状态信息
        self.state = ProcessState.NEW

        # 调度信息
        self.priority = max(1, min(10, priority))  # 确保在1-10范围内
        self.burst_time = burst_time
        self.remaining_time = burst_time

        # 资源需求
        self.memory_needed = memory_needed
        self.memory_start = None  # 分配的内存起始地址

        # 时间统计
        self.arrival_time = time.time()  # 到达时间
        self.start_time = None  # 开始执行时间
        self.finish_time = None  # 完成时间
        self.waiting_time = 0  # 等待时间

        # 进程关系
        self.parent_pid = None
        self.children = []

    def __str__(self):
        """返回进程的字符串表示"""
        return f"{self.name}(PID:{self.pid}, 状态:{self.state.value}, 剩余:{self.remaining_time:.1f}s)"

    def to_dict(self):
        """转换为字典，便于显示"""
        return {
            "PID": self.pid,
            "名称": self.name,
            "状态": self.state.value,
            "优先级": self.priority,
            "所需时间": self.burst_time,
            "剩余时间": round(self.remaining_time, 1),
            "需要内存": self.memory_needed,
            "等待时间": round(self.waiting_time, 1)
        }

    def execute(self, time_slice=1.0):
        """
        执行一个时间片

        参数:
        time_slice: 时间片大小

        返回:
        bool: 进程是否完成
        """
        # 记录开始时间
        if self.start_time is None:
            self.start_time = time.time()

        # 执行时间片
        if self.remaining_time > time_slice:
            self.remaining_time -= time_slice
            return False  # 未完成
        else:
            self.remaining_time = 0
            self.state = ProcessState.TERMINATED
            self.finish_time = time.time()
            return True  # 已完成

    def update_waiting_time(self, current_time):
        """更新等待时间"""
        if self.state == ProcessState.READY or self.state == ProcessState.WAITING:
            elapsed = current_time - self.arrival_time
            self.waiting_time = max(self.waiting_time, elapsed)

    @classmethod
    def reset_pid_counter(cls):
        """重置PID计数器（用于测试）"""
        cls._next_pid = 1


class ProcessManager:
    """进程管理器"""

    def __init__(self):
        self.processes = {}  # 所有进程字典，pid -> Process
        self.running_pid = None  # 当前运行的进程PID

    def create_process(self, name=None, burst_time=5, priority=5, memory_needed=50):
        """创建新进程"""
        process = Process(name, burst_time, priority, memory_needed)
        self.processes[process.pid] = process
        return process

    def get_process(self, pid):
        """获取指定PID的进程"""
        return self.processes.get(pid)

    def get_all_processes(self):
        """获取所有进程"""
        return list(self.processes.values())

    def get_processes_by_state(self, state):
        """按状态获取进程"""
        return [p for p in self.processes.values() if p.state == state]

    def terminate_process(self, pid):
        """终止进程"""
        if pid in self.processes:
            process = self.processes[pid]
            process.state = ProcessState.TERMINATED
            process.finish_time = time.time()

            # 如果是运行中的进程
            if self.running_pid == pid:
                self.running_pid = None

            return True
        return False

    def display_all_processes(self):
        """显示所有进程信息"""
        if not self.processes:
            print("当前没有进程")
            return

        print(f"{'PID':<6} {'名称':<10} {'状态':<8} {'优先级':<6} {'剩余时间':<8} {'等待时间':<8}")
        print("-" * 46)

        for process in self.processes.values():
            print(f"{process.pid:<6} {process.name:<10} {process.state.value:<8} "
                  f"{process.priority:<6} {process.remaining_time:<8.1f} "
                  f"{process.waiting_time:<8.1f}")

