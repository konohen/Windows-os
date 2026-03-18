#!/usr/bin/env python3
"""
操作系统模拟程序 - 主入口
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.cli import main as cli_main
from src.constants import print_separator


def main():
    """主函数"""
    print("操作系统模拟程序")
    print()

    print("功能简介:")
    print("  ✓ 进程创建和管理")
    print("  ✓ 多种CPU调度算法")
    print("  ✓ 内存分配和回收")
    print("  ✓ 进程同步（信号量和互斥锁）")
    print("  ✓ 交互式命令行界面")
    print()

    # 简单菜单
    while True:
        print("请选择模式:")
        print("  1. 交互式命令行 (核心)")
        print("  2. 快速演示")
        print("  3. 查看指南")
        print("  4. 退出程序")
        print()

        try:
            choice = input("请输入选项 (1-4): ").strip()

            if choice == "1":
                # 启动命令行界面
                cli_main()
                break

            elif choice == "2":
                # 快速演示
                print("\n开始快速演示...")
                print("=" * 50)

                # 导入模拟器并运行演示
                from src.core.os_simulator import OSSimulator
                simulator = OSSimulator()

                # 创建一些进程
                print("创建3个随机进程...")
                simulator.create_random_process(3)

                # 运行几个时间片
                print("\n运行5个时间片...")
                for i in range(5):
                    simulator.execute_time_slice()

                    # 暂停一下，方便观察
                    import time
                    time.sleep(1)

                # 显示总结
                simulator.display_summary()

                # 返回到主菜单
                input("\n按回车键返回主菜单...")

            elif choice == "3":
                # 显示初学者指南
                print("指南")

                print("操作系统基本概念:")
                print("-" * 50)

                concepts = [
                    ("1. 什么是进程?", "程序的一次执行实例"),
                    ("2. 进程的状态?", "新建→就绪→运行→阻塞→终止"),
                    ("3. 什么是调度?", "决定哪个进程使用CPU"),
                    ("4. 什么是内存管理?", "为进程分配和回收内存"),
                    ("5. 什么是进程同步?", "协调进程对共享资源的访问"),
                ]

                for title, desc in concepts:
                    print(f"{title:<20} {desc}")

                print("\n使用建议:")
                print("  1. 先从'快速演示'开始，了解基本功能")
                print("  2. 使用'交互式命令行'亲手操作")
                print("  3. 尝试创建不同参数的进程")
                print("  4. 比较不同调度算法的效果")
                print("  5. 使用信号量实现简单的同步")

                input("\n按回车键返回主菜单...")

            elif choice == "4":
                print("感谢使用！再见！")
                sys.exit(0)

            else:
                print("无效选项，请重新输入")
                print()

        except KeyboardInterrupt:
            print("\n程序被中断")
            sys.exit(0)
        except Exception as e:
            print(f"错误: {e}")
            print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)