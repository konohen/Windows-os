"""
操作系统模拟器主类
整合所有模块
"""

import time
import threading
from ..constants import ProcessState, ScheduleAlgorithm, MemoryAlgorithm, print_separator
from .process import ProcessManager, Process
from .memory import MemoryManager
from .scheduler import SchedulerFactory
from .sync import SyncManager

class OSSimulator:
    """操作系统模拟器"""

    def __init__(self,
                 memory_size=512,
                 scheduler_algo=ScheduleAlgorithm.FCFS,
                 memory_algo=MemoryAlgorithm.FIRST_FIT,
                 time_slice=1.0):

        # 初始化各个组件
        self.process_manager = ProcessManager()
        self.memory_manager = MemoryManager(memory_size, memory_algo)
        self.scheduler = SchedulerFactory.create_scheduler(scheduler_algo, time_slice=time_slice)
        self.sync_manager = SyncManager()

        # 系统状态
        self.running_process = None
        self.system_time = 0.0
        self.time_slice = time_slice
        self.is_running = False
        self.simulation_thread = None

        # 性能统计
        self.total_processes = 0
        self.completed_processes = 0
        self.total_waiting_time = 0.0
        self.total_turnaround_time = 0.0
        self.context_switches = 0

        print_separator("操作系统初始化完成")
        print(f"内存大小: {memory_size}MB")
        print(f"调度算法: {scheduler_algo.value}")
        print(f"内存算法: {memory_algo.value}")
        print(f"时间片大小: {time_slice}秒")

    def create_process(self, name=None, burst_time=5, priority=5, memory_needed=50):
        """创建新进程"""
        print_separator("创建进程")
        # 检查内存是否足够
        if memory_needed > self.memory_manager.free_memory:
            print(f"内存不足！需要{memory_needed}MB，但只剩{self.memory_manager.free_memory}MB")
            return None

        # 创建进程
        process = self.process_manager.create_process(name, burst_time, priority, memory_needed)

        # 分配内存
        start_addr = self.memory_manager.allocate(memory_needed, process.pid)
        if start_addr is None:
            print("内存分配失败")
            return None

        process.memory_start = start_addr

        # 添加到就绪队列
        if self.scheduler.add_process(process):
            self.total_processes += 1
            print(f"✓ 进程创建成功: {process.name} (PID:{process.pid})")
            print(f"  所需时间: {burst_time}秒, 优先级: {priority}, 内存: {memory_needed}MB")
            return process
        else:
            print("✗ 进程创建失败")
            return None

    def create_random_process(self, count=1):
        """创建随机进程"""
        import random

        for i in range(count):
            name = f"随机进程{i+1}"
            burst_time = random.randint(2, 10)
            priority = random.randint(1, 10)
            memory_needed = random.choice([32, 64, 128, 256])

            self.create_process(name, burst_time, priority, memory_needed)
            time.sleep(0.1)  # 模拟不同到达时间

    def terminate_process(self, pid):
        """终止进程"""
        print_separator(f"终止进程 PID:{pid}")

        process = self.process_manager.get_process(pid)
        if not process:
            print(f"✗ 进程 PID:{pid} 不存在")
            return False

        # 更新统计信息
        if process.state == ProcessState.RUNNING:
            if process.start_time:
                turnaround = self.system_time - process.arrival_time
                self.total_turnaround_time += turnaround

            self.completed_processes += 1

        # 终止进程
        success = self.process_manager.terminate_process(pid)

        if success:
            # 释放内存
            self.memory_manager.free(pid)

            # 如果是当前运行进程，清空
            if self.running_process and self.running_process.pid == pid:
                self.running_process = None

            # 从就绪队列移除
            self.scheduler.remove_process(pid)

            print(f"✓ 进程 {process.name} 已终止")

            # 更新等待时间统计
            if process.start_time:
                waiting_time = process.start_time - process.arrival_time
                self.total_waiting_time += waiting_time

        return success

    def create_semaphore(self, name, value=1):
        """创建信号量"""
        print_separator(f"创建信号量: {name}")

        try:
            semaphore = self.sync_manager.create_semaphore(name, value)
            print(f"✓ 信号量 '{name}' 创建成功，初始值={value}")
            return semaphore
        except ValueError as e:
            print(f"✗ {e}")
            return None

    def create_mutex(self, name):
        """创建互斥锁"""
        print_separator(f"创建互斥锁: {name}")

        try:
            mutex = self.sync_manager.create_mutex(name)
            print(f"✓ 互斥锁 '{name}' 创建成功")
            return mutex
        except ValueError as e:
            print(f"✗ {e}")
            return None

    def semaphore_wait(self, name, pid):
        """进程等待信号量"""
        print_separator(f"进程等待信号量")

        process = self.process_manager.get_process(pid)
        if not process:
            print(f"✗ 进程 PID:{pid} 不存在")
            return False

        try:
            success = self.sync_manager.semaphore_wait(name, process)

            if not success:
                # 进程进入等待状态
                print(f"  {process.name} 等待信号量 '{name}'")

                # 如果进程正在运行，需要让它离开CPU
                if self.running_process and self.running_process.pid == pid:
                    self.running_process = None
                    self.context_switches += 1

            return True
        except ValueError as e:
            print(f"✗ {e}")
            return False

    def semaphore_signal(self, name):
        """释放信号量"""
        print_separator(f"释放信号量: {name}")

        try:
            process = self.sync_manager.semaphore_signal(name)

            if process:
                print(f"✓ 信号量 '{name}' 释放，{process.name} 被唤醒")

                # 唤醒的进程加入就绪队列
                self.scheduler.add_process(process)
                return process
            else:
                print(f"✓ 信号量 '{name}' 释放，无等待进程")
                return None
        except ValueError as e:
            print(f"✗ {e}")
            return None

    def set_scheduler(self, algorithm):
        """设置调度算法"""
        print_separator(f"切换调度算法: {algorithm.value}")

        # 保存当前就绪队列
        old_queue = self.scheduler.ready_queue.copy()

        # 创建新调度器
        self.scheduler = SchedulerFactory.create_scheduler(algorithm, time_slice=self.time_slice)

        # 恢复进程到新调度器
        for process in old_queue:
            self.scheduler.add_process(process)

        print(f"✓ 调度算法已切换为: {algorithm.value}")

    def execute_time_slice(self):
        """执行一个时间片"""
        self.system_time += self.time_slice

        print(f"\n[时间片 {int(self.system_time)}]")
        print("-" * 40)

        # 1. 如果有进程正在运行，让它执行
        if self.running_process and self.running_process.state == ProcessState.RUNNING:
            completed = self.running_process.execute(self.time_slice)

            if completed:
                # 进程完成
                print(f"  {self.running_process.name} 执行完成！")
                self.terminate_process(self.running_process.pid)
                self.running_process = None

        # 2. 调度新进程
        if not self.running_process:
            next_process = self.scheduler.get_next_process(self.running_process)

            if next_process:
                # 检查是否上下文切换
                if (self.running_process and
                    self.running_process.pid != next_process.pid):
                    self.context_switches += 1

                # 设置新进程为运行状态
                self.running_process = next_process
                self.running_process.state = ProcessState.RUNNING

                # 记录开始时间
                if self.running_process.start_time is None:
                    self.running_process.start_time = self.system_time

                print(f"  {self.running_process.name} 开始运行")
            else:
                print("  CPU空闲")

        # 3. 如果是RR调度器，更新时间片使用
        if hasattr(self.scheduler, 'update_time_used'):
            self.scheduler.update_time_used(self.time_slice)

        # 4. 显示当前状态
        self.display_current_status()

    def _simulation_loop(self):
        """模拟循环"""
        while self.is_running:
            self.execute_time_slice()
            time.sleep(1)  # 等待1秒，方便观察

    def start_simulation(self, steps=None):
        """开始模拟"""
        print_separator("开始模拟")

        self.is_running = True

        if steps:
            # 执行指定步数
            for i in range(steps):
                if not self.is_running:
                    break
                self.execute_time_slice()
                time.sleep(1)
            self.is_running = False
        else:
            # 在后台线程中持续运行
            self.simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
            self.simulation_thread.start()

    def stop_simulation(self):
        """停止模拟"""
        self.is_running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=2)

        print_separator("模拟停止")

    def display_current_status(self):
        """显示当前状态"""
        print(f"\n当前状态:")
        print(f"  系统时间: {self.system_time:.1f}秒")
        print(f"  运行中: {self.running_process.name if self.running_process else '无'}")

        # 就绪队列 - 安全处理
        try:
            ready_count = len(self.scheduler.ready_queue)
        except:
            ready_count = 0

        if ready_count > 0:
            print(f"  就绪队列: {ready_count} 个进程")

            # 安全地显示前3个进程
            displayed = 0
            try:
                for i, process in enumerate(self.scheduler.ready_queue):
                    if i >= 3:  # 只显示前3个
                        break
                    print(f"    {i + 1}. {process}")
                    displayed += 1

                if ready_count > displayed:
                    print(f"    ... 还有 {ready_count - displayed} 个")
            except Exception as e:
                print(f"    无法显示队列详情: {e}")
        else:
            print("  就绪队列: 空")

        # 阻塞进程
        waiting_processes = self.process_manager.get_processes_by_state(ProcessState.WAITING)
        if waiting_processes:
            print(f"  阻塞进程: {len(waiting_processes)} 个")
        else:
            print("  阻塞进程: 无")

    def display_summary(self):
        """显示系统总结"""
        print_separator("系统总结")

        # 内存状态
        self.memory_manager.display()

        # 进程统计
        print(f"\n进程统计:")
        print(f"  总进程数: {self.total_processes}")
        print(f"  已完成: {self.completed_processes}")
        print(f"  就绪中: {len(self.scheduler.ready_queue)}")

        waiting = len(self.process_manager.get_processes_by_state(ProcessState.WAITING))
        print(f"  阻塞中: {waiting}")
        print(f"  运行中: {1 if self.running_process else 0}")

        # 性能指标
        print(f"\n性能指标:")
        if self.completed_processes > 0:
            avg_waiting = self.total_waiting_time / self.completed_processes
            avg_turnaround = self.total_turnaround_time / self.completed_processes
            print(f"  平均等待时间: {avg_waiting:.2f}秒")
            print(f"  平均周转时间: {avg_turnaround:.2f}秒")
        else:
            print("  尚无完成进程，无法计算性能指标")

        print(f"  上下文切换次数: {self.context_switches}")

        # 同步原语状态
        self.sync_manager.display_semaphores()
        self.sync_manager.display_mutexes()