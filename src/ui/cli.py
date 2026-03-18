"""
命令行界面模块
提供用户交互界面
"""

import cmd
import sys
import time
from ..constants import ProcessState, ScheduleAlgorithm, MemoryAlgorithm, print_separator
from ..core.os_simulator import OSSimulator


class OSSimulatorCLI(cmd.Cmd):
    """操作系统模拟器命令行界面"""

    intro = """
->      操作系统模拟程序 - 交互式命令行      <-            
                                                  

输入 'help' 查看可用命令，输入 'exit' 退出。
输入 'demo' 运行演示，输入 'guide' 查看指南。
"""
    prompt = "OS> "

    def __init__(self):
        super().__init__()
        self.simulator = None
        self._init_simulator()

    def _init_simulator(self):
        """初始化模拟器"""
        self.simulator = OSSimulator(
            memory_size=512,
            scheduler_algo=ScheduleAlgorithm.FCFS,
            memory_algo=MemoryAlgorithm.FIRST_FIT,
            time_slice=1.0
        )
        print(" os初始化完成")
        print(f"  内存: 512MB")
        print(f"  调度算法: 先来先服务(FCFS)")
        print(f"  时间片: 1.0秒")

    def do_help(self, arg):
        """显示帮助信息"""
        print_separator("帮助信息")

        commands = [
            ("help, ?", "显示此帮助信息"),
            ("create", "创建进程（无参数则随机）"),
            ("create [名称] [时间] [优先级] [内存]", "创建指定参数的进程"),
            ("random [数量]", "创建多个随机进程"),
            ("run [步数]", "运行模拟（无参数则持续运行）"),
            ("step", "执行一个时间片"),
            ("stop", "停止模拟"),
            ("schedule [算法]", "设置调度算法"),
            ("semcreate [名称] [值]", "创建信号量"),
            ("semwait [名称] [PID]", "进程等待信号量"),
            ("semsignal [名称]", "释放信号量"),
            ("mutex [名称]", "创建互斥锁"),
            ("terminate [PID]", "终止进程"),
            ("status", "显示系统状态"),
            ("memory", "显示内存状态"),
            ("sync", "显示同步原语状态"),
            ("summary", "显示系统总结"),
            ("reset", "重置模拟器"),
            ("demo", "运行演示"),
            ("guide", "显示初学者指南"),
            ("exit, quit", "退出程序"),
        ]

        for cmd, desc in commands:
            print(f"  {cmd:<40} - {desc}")

    def do_create(self, arg):
        """
        创建进程
        用法: create [名称] [执行时间] [优先级] [内存大小]
        示例: create 浏览器 10 3 64
              创建名为"浏览器"的进程，执行10秒，优先级3，需要64MB内存
        """
        args = arg.split()

        if len(args) == 0:
            # 创建随机进程
            process = self.simulator.create_process()
            if process:
                print(f"随机进程创建成功: {process}")
        elif len(args) >= 4:
            # 创建指定参数的进程
            try:
                name = args[0]
                burst_time = float(args[1])
                priority = int(args[2])
                memory_needed = int(args[3])

                process = self.simulator.create_process(name, burst_time, priority, memory_needed)
                if process:
                    print(f"进程创建成功: {process}")
            except ValueError as e:
                print(f"参数错误: {e}")
                print("正确格式: create [名称] [执行时间] [优先级] [内存大小]")
        else:
            print("用法:")
            print("  create                         - 创建随机进程")
            print("  create [名称] [时间] [优先级] [内存] - 创建指定进程")
            print("示例: create 浏览器 10 3 64")

    def do_random(self, arg):
        """创建随机进程"""
        try:
            count = int(arg) if arg else 3
            self.simulator.create_random_process(count)
            print(f"已创建 {count} 个随机进程")
        except ValueError:
            print("参数必须是数字，例如: random 5")

    def do_run(self, arg):
        """运行模拟"""
        try:
            if arg:
                steps = int(arg)
                print(f"开始运行 {steps} 个时间片...")
                self.simulator.start_simulation(steps)
            else:
                print("开始持续运行...")
                print("输入 'stop' 停止")
                self.simulator.start_simulation()
        except ValueError:
            print("步数必须是数字，例如: run 10")

    def do_step(self, arg):
        """执行一个时间片"""
        self.simulator.execute_time_slice()

    def do_stop(self, arg):
        """停止模拟"""
        self.simulator.stop_simulation()

    def do_schedule(self, arg):
        """设置调度算法"""
        if not arg:
            print("可用调度算法:")
            print("  FCFS     - 先来先服务")
            print("  SJF      - 短作业优先")
            print("  PRIORITY - 优先级调度")
            print("  RR       - 时间片轮转")
            return

        algorithm_map = {
            "FCFS": ScheduleAlgorithm.FCFS,
            "SJF": ScheduleAlgorithm.SJF,
            "PRIORITY": ScheduleAlgorithm.PRIORITY,
            "RR": ScheduleAlgorithm.RR,
        }

        algo = arg.upper()
        if algo in algorithm_map:
            self.simulator.set_scheduler(algorithm_map[algo])
        else:
            print(f"未知算法: {arg}")
            print("可用算法: FCFS, SJF, PRIORITY, RR")

    def do_semcreate(self, arg):
        """创建信号量"""
        args = arg.split()
        if len(args) >= 1:
            name = args[0]
            value = int(args[1]) if len(args) > 1 else 1
            self.simulator.create_semaphore(name, value)
        else:
            print("用法: semcreate [名称] [初始值(可选，默认1)]")

    def do_semwait(self, arg):
        """进程等待信号量"""
        args = arg.split()
        if len(args) >= 2:
            name = args[0]
            pid = int(args[1])
            self.simulator.semaphore_wait(name, pid)
        else:
            print("用法: semwait [信号量名] [进程PID]")

    def do_semsignal(self, arg):
        """释放信号量"""
        if arg:
            self.simulator.semaphore_signal(arg)
        else:
            print("用法: semsignal [信号量名]")

    def do_mutex(self, arg):
        """创建互斥锁"""
        if arg:
            self.simulator.create_mutex(arg)
        else:
            print("用法: mutex [名称]")

    def do_terminate(self, arg):
        """终止进程"""
        if arg:
            try:
                pid = int(arg)
                self.simulator.terminate_process(pid)
            except ValueError:
                print("PID必须是数字")
        else:
            print("用法: terminate [进程PID]")

    def do_status(self, arg):
        """显示系统状态"""
        self.simulator.display_current_status()

    def do_memory(self, arg):
        """显示内存状态"""
        self.simulator.memory_manager.display()

    def do_sync(self, arg):
        """显示同步原语状态"""
        self.simulator.sync_manager.display_semaphores()
        self.simulator.sync_manager.display_mutexes()

    def do_summary(self, arg):
        """显示系统总结"""
        self.simulator.display_summary()

    def do_reset(self, arg):
        """重置模拟器"""
        print("重置模拟器...")
        self._init_simulator()
        print("模拟器已重置")

    def do_demo(self, arg):
        """运行演示"""
        self._run_demo()

    def do_guide(self, arg):
        """显示初学者指南"""
        self._show_beginner_guide()

    def do_exit(self, arg):
        """退出程序"""
        print("感谢使用！")
        return True

    def do_quit(self, arg):
        """退出程序"""
        return self.do_exit(arg)

    def do_EOF(self, arg):
        """处理Ctrl+D"""
        print()
        return self.do_exit(arg)

    def default(self, line):
        """处理未知命令"""
        print(f"未知命令: {line}")
        print("输入 'help' 查看可用命令")

    def _run_demo(self):
        """运行演示"""
        print_separator("开始演示")

        print("1. 创建3个随机进程...")
        self.simulator.create_random_process(3)
        time.sleep(1)

        print("\n2. 运行3个时间片...")
        for i in range(3):
            self.simulator.execute_time_slice()
            time.sleep(1)

        print("\n3. 创建信号量演示同步...")
        self.simulator.create_semaphore("打印机", 1)
        time.sleep(1)

        print("\n4. 创建新进程并使用信号量...")
        process = self.simulator.create_process("打印任务", 3, 2, 32)
        if process:
            self.simulator.semaphore_wait("打印机", process.pid)
        time.sleep(1)

        print("\n5. 再创建几个进程...")
        self.simulator.create_process("计算任务", 4, 3, 64)
        self.simulator.create_process("网络任务", 2, 1, 32)
        time.sleep(1)

        print("\n6. 运行2个时间片...")
        for i in range(2):
            self.simulator.execute_time_slice()
            time.sleep(1)

        print("\n7. 释放信号量...")
        self.simulator.semaphore_signal("打印机")
        time.sleep(1)

        print("\n8. 再运行2个时间片...")
        for i in range(2):
            self.simulator.execute_time_slice()
            time.sleep(1)

        print("\n9. 显示系统总结...")
        self.simulator.display_summary()

        print("\n演示完成！")

    def _show_beginner_guide(self):
        """显示初学者指南"""
        print_separator("指南")

        concepts = [
            ("1. 进程", "程序的一次执行实例，有独立的内存空间"),
            ("2. 进程状态", "新建 → 就绪 → 运行 → 阻塞 → 终止"),
            ("3. 调度算法", "决定哪个进程获得CPU使用权"),
            ("   - FCFS", "先来先服务，最简单"),
            ("   - SJF", "短作业优先，执行时间短的先运行"),
            ("   - 优先级", "优先级高的先运行（数字小的优先）"),
            ("   - 时间片轮转", "每个进程轮流执行一个固定时间"),
            ("4. 内存管理", "为进程分配和回收内存"),
            ("5. 信号量", "用于进程同步，防止资源冲突"),
            ("6. 互斥锁", "特殊的信号量，值为1，用于互斥访问"),
        ]

        for concept in concepts:
            if concept[0].startswith("   -"):
                print(f"   {concept[0]:<15} {concept[1]}")
            else:
                print(f"{concept[0]:<15} {concept[1]}")

        print("\n小tip:")
        print("  1. 先运行 'demo' 了解系统功能")
        print("  2. 使用 'create' 和 'random' 创建进程")
        print("  3. 使用 'run' 运行模拟，观察进程状态变化")
        print("  4. 尝试不同调度算法，比较差异")
        print("  5. 使用信号量和互斥锁实现进程同步")
        print("  6. 查看代码，理解实现原理")


def main():
    """CLI主函数"""
    cli = OSSimulatorCLI()

    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)


if __name__ == "__main__":
    main()