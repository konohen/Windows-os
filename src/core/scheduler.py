"""
调度器模块
实现不同的CPU调度算法
"""

from collections import deque
from ..constants import ProcessState, ScheduleAlgorithm


class Scheduler:
    """调度器基类"""

    def __init__(self, algorithm=ScheduleAlgorithm.FCFS):
        self.algorithm = algorithm
        self.ready_queue = []  # 基类统一初始化，子类可以覆盖

    def add_process(self, process):
        """添加进程到就绪队列"""
        # 检查进程是否已经在队列中
        for p in self.ready_queue:
            if p.pid == process.pid:
                return False

        # 只有NEW或WAITING状态的进程可以加入就绪队列
        if process.state in (ProcessState.NEW, ProcessState.WAITING):
            process.state = ProcessState.READY
            self.ready_queue.append(process)
            return True
        return False

    def remove_process(self, pid):
        """从就绪队列中移除进程"""
        for i, p in enumerate(self.ready_queue):
            if p.pid == pid:
                del self.ready_queue[i]
                return True
        return False

    def get_next_process(self, current_process=None):
        """获取下一个要执行的进程"""
        raise NotImplementedError("子类必须实现此方法")

    def has_ready_processes(self):
        """检查是否有就绪进程"""
        return len(self.ready_queue) > 0

    def display_queue(self):
        """显示就绪队列"""
        if not self.ready_queue:
            print("就绪队列: 空")
        else:
            print("就绪队列:")
            count = 0
            for process in self.ready_queue:
                print(f"  {process}")
                count += 1
                if count >= 5:  # 最多显示5个
                    if len(self.ready_queue) > 5:
                        print(f"  ... 还有 {len(self.ready_queue) - 5} 个")
                    break


class FCFSScheduler(Scheduler):
    """先来先服务调度器"""

    def __init__(self):
        super().__init__(ScheduleAlgorithm.FCFS)
        # 覆盖基类的ready_queue，使用deque
        self.ready_queue = deque()

    def get_next_process(self, current_process=None):
        """从队列头部获取进程"""
        if self.ready_queue:
            return self.ready_queue.popleft()
        return None

    def remove_process(self, pid):
        """从deque队列中移除进程"""
        for i, p in enumerate(self.ready_queue):
            if p.pid == pid:
                del self.ready_queue[i]
                return True
        return False


class SJFScheduler(Scheduler):
    """短作业优先调度器"""

    def __init__(self):
        super().__init__(ScheduleAlgorithm.SJF)
        # 使用基类的list，不覆盖

    def add_process(self, process):
        """添加进程并排序"""
        if super().add_process(process):
            # 按剩余时间排序
            self.ready_queue.sort(key=lambda p: p.remaining_time)
            return True
        return False

    def get_next_process(self, current_process=None):
        """获取剩余时间最短的进程"""
        if self.ready_queue:
            return self.ready_queue.pop(0)
        return None


class PriorityScheduler(Scheduler):
    """优先级调度器（数字越小优先级越高）"""

    def __init__(self):
        super().__init__(ScheduleAlgorithm.PRIORITY)
        # 使用基类的list，不覆盖

    def add_process(self, process):
        """添加进程并排序"""
        if super().add_process(process):
            # 按优先级排序（数字小的优先）
            self.ready_queue.sort(key=lambda p: p.priority)
            return True
        return False

    def get_next_process(self, current_process=None):
        """获取优先级最高的进程"""
        if self.ready_queue:
            return self.ready_queue.pop(0)
        return None


class RoundRobinScheduler(Scheduler):
    """时间片轮转调度器"""

    def __init__(self, time_slice=1.0):
        super().__init__(ScheduleAlgorithm.RR)
        self.time_slice = time_slice
        # 覆盖基类的ready_queue，使用deque
        self.ready_queue = deque()
        self.current_time_used = 0.0

    def get_next_process(self, current_process=None):
        """
        获取下一个进程

        参数:
        current_process: 当前正在运行的进程
        """
        # 如果当前进程时间片用完，放回队列末尾
        if (current_process and
            current_process.state == ProcessState.RUNNING and
            self.current_time_used >= self.time_slice):

            current_process.state = ProcessState.READY
            # 将进程重新加入队列（add_process会检查重复）
            self.add_process(current_process)
            self.current_time_used = 0.0

        # 从队列头部获取新进程
        if self.ready_queue:
            process = self.ready_queue.popleft()
            self.current_time_used = 0.0
            return process

        return None

    def remove_process(self, pid):
        """从deque队列中移除进程"""
        for i, p in enumerate(self.ready_queue):
            if p.pid == pid:
                del self.ready_queue[i]
                return True
        return False

    def update_time_used(self, time_passed):
        """更新当前进程已使用的时间"""
        self.current_time_used += time_passed


class SchedulerFactory:
    """调度器工厂类"""

    @staticmethod
    def create_scheduler(algorithm, **kwargs):
        """创建调度器"""
        if algorithm == ScheduleAlgorithm.FCFS:
            return FCFSScheduler()
        elif algorithm == ScheduleAlgorithm.SJF:
            return SJFScheduler()
        elif algorithm == ScheduleAlgorithm.PRIORITY:
            return PriorityScheduler()
        elif algorithm == ScheduleAlgorithm.RR:
            time_slice = kwargs.get('time_slice', 1.0)
            return RoundRobinScheduler(time_slice)
        else:
            return FCFSScheduler()