"""
内存管理模块
实现内存分配和回收
"""

from ..constants import MemoryAlgorithm


class MemoryBlock:
    """内存块"""

    def __init__(self, start, size, is_free=True, process_id=None):
        """
        初始化内存块

        start: 起始地址
        size: 块大小
        is_free: 是否空闲
        process_id: 占用的进程ID
        """
        self.start = start
        self.size = size
        self.is_free = is_free
        self.process_id = process_id

    def __str__(self):
        """字符串表示"""
        status = "空闲" if self.is_free else f"占用(PID:{self.process_id})"
        return f"[{self.start:04d}-{self.start + self.size:04d}] {self.size:4d}MB {status}"


class MemoryManager:
    """内存管理器"""

    def __init__(self, total_memory=512, algorithm=MemoryAlgorithm.FIRST_FIT):
        """
        初始化内存管理器

        total_memory: 总内存大小(MB)
        algorithm: 分配算法
        """
        self.total_memory = total_memory
        self.free_memory = total_memory
        self.algorithm = algorithm

        # 初始化内存块列表，只有一个大的空闲块
        self.blocks = [MemoryBlock(0, total_memory, True)]

    def allocate(self, size, process_id):
        """
        分配内存

        size: 需要的内存大小
        process_id: 请求的进程ID

        返回:
        int or None: 成功返回起始地址，失败返回None
        """
        if size > self.free_memory:
            return None

        if self.algorithm == MemoryAlgorithm.FIRST_FIT:
            return self._first_fit(size, process_id)
        elif self.algorithm == MemoryAlgorithm.BEST_FIT:
            return self._best_fit(size, process_id)
        elif self.algorithm == MemoryAlgorithm.WORST_FIT:
            return self._worst_fit(size, process_id)
        else:
            return self._first_fit(size, process_id)

    def _first_fit(self, size, process_id):
        """首次适应算法"""
        for i, block in enumerate(self.blocks):
            if block.is_free and block.size >= size:
                return self._split_block(i, size, process_id)
        return None

    def _best_fit(self, size, process_id):
        """最佳适应算法"""
        best_index = -1
        best_size = float('inf')

        for i, block in enumerate(self.blocks):
            if block.is_free and block.size >= size:
                if block.size < best_size:
                    best_size = block.size
                    best_index = i

        if best_index != -1:
            return self._split_block(best_index, size, process_id)
        return None

    def _worst_fit(self, size, process_id):
        """最坏适应算法"""
        worst_index = -1
        worst_size = -1

        for i, block in enumerate(self.blocks):
            if block.is_free and block.size >= size:
                if block.size > worst_size:
                    worst_size = block.size
                    worst_index = i

        if worst_index != -1:
            return self._split_block(worst_index, size, process_id)
        return None

    def _split_block(self, index, size, process_id):
        """分割内存块"""
        block = self.blocks[index]

        if block.size == size:
            # 正好匹配，直接分配
            block.is_free = False
            block.process_id = process_id
            self.free_memory -= size
            return block.start
        else:
            # 需要分割
            new_block = MemoryBlock(
                block.start + size,
                block.size - size,
                True
            )

            # 修改原块
            block.size = size
            block.is_free = False
            block.process_id = process_id

            # 插入新块
            self.blocks.insert(index + 1, new_block)
            self.free_memory -= size

            return block.start

    def free(self, process_id):
        """释放进程占用的内存"""
        freed = False

        for block in self.blocks:
            if block.process_id == process_id:
                block.is_free = True
                block.process_id = None
                self.free_memory += block.size
                freed = True

        # 合并相邻的空闲块
        if freed:
            self._merge_blocks()

        return freed

    def _merge_blocks(self):
        """合并相邻的空闲块"""
        i = 0
        while i < len(self.blocks) - 1:
            current = self.blocks[i]
            next_block = self.blocks[i + 1]

            if current.is_free and next_block.is_free:
                # 合并两个空闲块
                current.size += next_block.size
                del self.blocks[i + 1]
            else:
                i += 1

    def get_memory_usage(self):
        """获取内存使用率"""
        used = self.total_memory - self.free_memory
        return used / self.total_memory if self.total_memory > 0 else 0

    def display(self):
        """显示内存状态"""
        print(f"\n内存状态:")
        print(f"总内存: {self.total_memory}MB")
        print(f"已使用: {self.total_memory - self.free_memory}MB")
        print(f"空闲: {self.free_memory}MB")
        print(f"使用率: {self.get_memory_usage() * 100:.1f}%")

        print(f"\n内存块详情:")

        for block in self.blocks:
            print(block)