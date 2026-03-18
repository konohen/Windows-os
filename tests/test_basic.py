"""
基本功能测试
用于验证核心模块的正确性
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.process import Process, ProcessManager
from src.core.memory import MemoryManager
from src.core.sync import Semaphore
from src.constants import ProcessState


def test_process_creation():
    """测试进程创建"""
    print("测试进程创建...")

    # 重置PID计数器
    Process.reset_pid_counter()

    # 创建进程
    p1 = Process("测试进程1", burst_time=10, priority=3, memory_needed=64)
    p2 = Process("测试进程2", burst_time=5, priority=5, memory_needed=32)

    # 验证
    assert p1.pid == 1, f"PID错误: {p1.pid}"
    assert p2.pid == 2, f"PID错误: {p2.pid}"
    assert p1.name == "测试进程1"
    assert p2.name == "测试进程2"
    assert p1.state == ProcessState.NEW
    assert p1.priority == 3
    assert p1.burst_time == 10
    assert p1.remaining_time == 10
    assert p1.memory_needed == 64

    print("   进程创建测试通过")


def test_process_execution():
    """测试进程执行"""
    print("测试进程执行...")

    Process.reset_pid_counter()
    process = Process("测试进程", burst_time=5, priority=3)
    process.state = ProcessState.RUNNING

    # 执行时间片
    completed = process.execute(3)
    assert not completed, "不应完成"
    assert process.remaining_time == 2

    # 继续执行
    completed = process.execute(2)
    assert completed, "应完成"
    assert process.remaining_time == 0
    assert process.state == ProcessState.TERMINATED

    print("   进程执行测试通过")


def test_process_manager():
    """测试进程管理器"""
    print("测试进程管理器...")

    Process.reset_pid_counter()
    manager = ProcessManager()

    # 创建进程
    p1 = manager.create_process("进程1", 5, 3, 64)
    p2 = manager.create_process("进程2", 3, 5, 32)

    # 验证
    assert p1.pid == 1
    assert p2.pid == 2
    assert len(manager.processes) == 2
    assert manager.get_process(1) == p1
    assert manager.get_process(999) is None

    # 获取按状态的进程
    new_processes = manager.get_processes_by_state(ProcessState.NEW)
    assert len(new_processes) == 2

    # 终止进程
    assert manager.terminate_process(1) is True
    assert p1.state == ProcessState.TERMINATED
    assert manager.terminate_process(999) is False

    print("   进程管理器测试通过")


def test_memory_manager():
    """测试内存管理器"""
    print("测试内存管理器...")

    memory = MemoryManager(total_memory=256)

    # 分配内存
    addr1 = memory.allocate(64, 1)
    assert addr1 is not None
    assert memory.free_memory == 256 - 64

    addr2 = memory.allocate(128, 2)
    assert addr2 is not None
    assert memory.free_memory == 256 - 64 - 128

    # 内存不足
    addr3 = memory.allocate(100, 3)
    assert addr3 is None  # 应该失败

    # 释放内存
    assert memory.free(1) is True
    assert memory.free_memory == 256 - 128

    # 释放不存在的进程
    assert memory.free(999) is False

    print("   内存管理器测试通过")


def test_semaphore():
    """测试信号量"""
    print("测试信号量...")

    # 创建信号量
    semaphore = Semaphore("测试信号量", value=2)

    # 模拟进程
    class MockProcess:
        def __init__(self, pid):
            self.pid = pid
            self.state = None

    # 测试P操作

    p1 = MockProcess(1)
    p2 = MockProcess(2)
    p3 = MockProcess(3)

    assert semaphore.wait(p1) is True  # value=1
    assert semaphore.wait(p2) is True  # value=0
    assert semaphore.wait(p3) is False  # value=-1, 应该阻塞

    assert p3.state == ProcessState.WAITING
    assert len(semaphore.waiting_queue) == 1

    # 测试V操作
    woke_process = semaphore.signal()  # value=0, 无等待进程
    assert woke_process is p3

    woke_process = semaphore.signal()  # value=1, 唤醒p3
    assert woke_process is None
    assert p3.state == ProcessState.READY

    print("   信号量测试通过")

def run_all_tests():
    """运行所有测试"""
    print("开始运行测试...")
    print("->><<-")

    try:
        test_process_creation()
        test_process_execution()
        test_process_manager()
        test_memory_manager()
        test_semaphore()

        print("->><<-")
        print("所有测试通过！")

    except AssertionError as e:
        print(f"测试失败: {e}")
        return False

    return True


if __name__ == "__main__":
    run_all_tests()