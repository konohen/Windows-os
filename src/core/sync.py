"""
进程同步模块
实现信号量和互斥锁
"""

from ..constants import ProcessState


class Semaphore:
    """信号量"""

    def __init__(self, name, value=1):
        """
        初始化信号量

        name: 信号量名称
        value: 初始值
        """
        self.name = name
        self.value = value
        self.waiting_queue = []  # 等待队列

    def wait(self, process):
        """
        P操作 - 申请资源
        process: 请求资源的进程
        bool: 是否成功获取资源
        """
        self.value -= 1

        if self.value < 0:
            # 资源不足，进程进入等待状态
            process.state = ProcessState.WAITING
            self.waiting_queue.append(process)
            return False  # 未成功获取

        return True  # 成功获取

    def signal(self):
        """
        V操作 - 释放资源

        Process or None: 如果有被唤醒的进程则返回，否则返回None
        """
        self.value += 1

        if self.waiting_queue:
            # 唤醒一个等待的进程
            process = self.waiting_queue.pop(0)
            process.state = ProcessState.READY
            return process

        return None

    def get_info(self):
        """获取信号量信息"""
        return {
            "名称": self.name,
            "当前值": self.value,
            "等待进程数": len(self.waiting_queue)
        }


class Mutex:
    """互斥锁（基于信号量实现）"""

    def __init__(self, name):
        """初始化互斥锁"""
        self.name = name
        self.semaphore = Semaphore(name, 1)  # 互斥锁就是值为1的信号量
        self.owner = None  # 当前持有锁的进程ID

    def acquire(self, process):
        """获取锁"""
        success = self.semaphore.wait(process)
        if success:
            self.owner = process.pid
        return success

    def release(self):
        """释放锁"""
        self.owner = None
        return self.semaphore.signal()

    def is_locked(self):
        """检查是否被锁定"""
        return self.owner is not None

    def get_info(self):
        """获取互斥锁信息"""
        info = self.semaphore.get_info()
        info["持有者"] = f"PID:{self.owner}" if self.owner else "无"
        return info


class SyncManager:
    """同步管理器"""

    def __init__(self):
        self.semaphores = {}  # 信号量字典
        self.mutexes = {}  # 互斥锁字典

    def create_semaphore(self, name, value=1):
        """创建信号量"""
        if name in self.semaphores:
            raise ValueError(f"信号量 '{name}' 已存在")

        semaphore = Semaphore(name, value)
        self.semaphores[name] = semaphore
        return semaphore

    def create_mutex(self, name):
        """创建互斥锁"""
        if name in self.mutexes:
            raise ValueError(f"互斥锁 '{name}' 已存在")

        mutex = Mutex(name)
        self.mutexes[name] = mutex
        return mutex

    def semaphore_wait(self, name, process):
        """进程等待信号量"""
        if name not in self.semaphores:
            raise ValueError(f"信号量 '{name}' 不存在")

        return self.semaphores[name].wait(process)

    def semaphore_signal(self, name):
        """释放信号量"""
        if name not in self.semaphores:
            raise ValueError(f"信号量 '{name}' 不存在")

        return self.semaphores[name].signal()

    def display_semaphores(self):
        """显示所有信号量状态"""
        if not self.semaphores:
            print("没有信号量")
            return

        print("\n信号量状态:")

        for name, semaphore in self.semaphores.items():
            info = semaphore.get_info()
            print(f"{name}: 值={info['当前值']}, 等待进程={info['等待进程数']}")

    def display_mutexes(self):
        """显示所有互斥锁状态"""
        if not self.mutexes:
            print("没有互斥锁")
            return

        print("\n互斥锁状态:")

        for name, mutex in self.mutexes.items():
            info = mutex.get_info()
            print(f"{name}: {info['持有者']}, 等待进程={info['等待进程数']}")