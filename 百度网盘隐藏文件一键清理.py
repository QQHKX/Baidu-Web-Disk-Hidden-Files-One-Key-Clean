import sys
import os
import win32file
from tqdm import tqdm
import time
import threading

# ANSI 转义序列定义
RED = "\033[91m"  # 红色
YELLOW = "\033[93m"  # 黄色
RESET = "\033[0m"  # 重置颜色

# 定义旋转指示器动画函数
def spinning_animation(stop_event):
    spinner = ['|', '/', '-', '\\']
    while not stop_event.is_set():
        for symbol in spinner:
            sys.stdout.write(f'\r{symbol} 正在索引中...')
            sys.stdout.flush()
            time.sleep(0.1)

# 检查文件是否为隐藏文件
def is_hidden(filepath):
    try:
        file_attrs = win32file.GetFileAttributes(filepath)
        return file_attrs & (win32file.FILE_ATTRIBUTE_HIDDEN | win32file.FILE_ATTRIBUTE_SYSTEM)
    except Exception as e:
        print(f"无法获取文件属性: {filepath}，错误: {e}")
        return False

def confirm_and_delete_files(directory, search_str):
    # 遍历目录，寻找文件名中包含特定字符串的文件
    files_to_delete = []

    # 启动旋转指示器线程
    stop_event = threading.Event()
    animation_thread = threading.Thread(target=spinning_animation, args=(stop_event,))
    animation_thread.start()

    # 用于统计文件总数，以便初始化进度条的总长度
    total_files = sum([len(files) for _, _, files in os.walk(directory)])
    

    # 处理完毕，停止动画
    stop_event.set()
    animation_thread.join()  # 等待动画线程结束
    print(f"已索引: {total_files}个文件")
    with tqdm(total=total_files, desc="遍历文件", unit="file") as pbar:
        for root, _, files in os.walk(directory):
            for file in files:
                full_path = os.path.join(root, file)
                # 仅当文件名包含特定字符串时，才将其加入删除列表
                if search_str in file:
                    files_to_delete.append(full_path)
                # 更新进度条
                pbar.update(1)

    if not files_to_delete:
        print("没有找到符合条件的文件。")
        return

    # 显示即将删除的文件
    print("以下文件将被删除：")
    for file in files_to_delete:
        print(file)

    # 要求用户确认
    print(f"需要删除的文件共有{len(files_to_delete)} 个")
    print(f"{RED}警告！{YELLOW}你正在删除【{directory}】中所有文件名包含【{search_str}】字段的文件！{RESET}")

    #请冷静5秒,请仔细检查这些文件，确保它们不是你需要的文件。
    for i in range(10, 0, -1):
        print(f"请再冷静{YELLOW}{i}{RESET}秒,请仔细检查这些文件，确保它们不是你需要的文件。")
        time.sleep(1)

    confirmation = input("最后一次确认,你确认删除这些文件吗？(y/n): ").strip().lower()

    if confirmation == 'y':
        # 删除文件时的进度条
        print("正在删除文件...")
        with tqdm(total=len(files_to_delete), desc="删除文件", unit="file") as pbar:
            for file in files_to_delete:
                try:
                    os.remove(file)
                except OSError as e:
                    print(f"删除文件 {file} 时出错: {e}")
                pbar.update(1)
    else:
        print("取消删除操作。")


if __name__ == "__main__":
    print("欢迎使用百度网盘自动备份修复工具！")

    search_str = input("请输入要扫描的文件名中包含的字符串(默认为.baiduyun.uploading.cfg)：").strip()
    if not search_str:
        search_str = '.baiduyun.uploading.cfg'

    directory = input("请输入要扫描的文件所在的目录(默认为系统盘)：").strip()
    if not directory:
        directory = os.path.abspath(os.sep)
        


    # 让用户确认
    confirmation = input(f"你是否扫描【{directory}】中所有文件名包含【{search_str}】字段的文件？(y/n):").strip().lower()
    if confirmation == 'y':
        confirm_and_delete_files(directory, search_str)
    else:
        print("已取消操作。")

    input("按任意键退出...") 