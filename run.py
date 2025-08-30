#!/usr/bin/env python3
import os
import subprocess
import sys
import time

def run_script(script_name):
    """运行指定的Python脚本并显示执行状态"""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'script', script_name)
    
    print("\n" + "="*50)
    print(f"开始执行: {script_name}")
    print(f"脚本路径: {script_path}")
    print("="*50)
    
    start_time = time.time()
    try:
        # 运行脚本并捕获输出
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        # 打印脚本的标准输出
        if result.stdout:
            print(f"\n{script_name} 输出:")
            print(result.stdout)
            
        end_time = time.time()
        print("\n" + "="*50)
        print(f"{script_name} 执行成功!")
        print(f"执行时间: {end_time - start_time:.2f} 秒")
        print("="*50)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n{script_name} 执行失败! 错误码: {e.returncode}")
        if e.stdout:
            print(f"标准输出: {e.stdout}")
        if e.stderr:
            print(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        print(f"\n{script_name} 执行时发生异常: {str(e)}")
        return False

def run_git_commands():
    """执行git命令：add、commit和push"""
    print("\n" + "="*50)
    print("开始执行Git命令...")
    
    # 询问用户是否要执行Git命令
    print("\n是否执行Git操作（git add . && git commit -m 'a' && git push）? (y/n)")
    choice = input().strip().lower()
    if choice != 'y':
        print("用户选择跳过Git操作!")
        print("="*50)
        return False
    
    # 定义要执行的Git命令列表
    git_commands = [
        ["git", "add", "."],
        ["git", "commit", "-m", "auto"],
        ["git", "push"]
    ]
    
    # 依次执行每个Git命令
    for cmd in git_commands:
        print(f"\n执行命令: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            if result.stdout:
                print(f"输出: {result.stdout}")
            print(f"{cmd[1]} 命令执行成功!")
        except subprocess.CalledProcessError as e:
            print(f"\n{cmd[1]} 命令执行失败! 错误码: {e.returncode}")
            if e.stdout:
                print(f"标准输出: {e.stdout}")
            if e.stderr:
                print(f"错误输出: {e.stderr}")
            print("Git操作中断!")
            print("="*50)
            return False
        except Exception as e:
            print(f"\n{cmd[1]} 命令执行时发生异常: {str(e)}")
            print("Git操作中断!")
            print("="*50)
            return False
    
    print("\n所有Git命令执行成功!")
    print("="*50)
    return True

def main():
    """主函数，按顺序执行所有脚本"""
    print("开始执行一键运行脚本集...")
    start_total_time = time.time()
    
    # 要执行的脚本列表，按顺序排列
    scripts_to_run = [
        "ExtractReadMe.py",
        "get_book_covers.py",
        "download_book_covers.py",
        "generate_tags.py",
        "generate_metadata.py"
    ]
    
    # 检查所有脚本文件是否存在
    all_scripts_exist = True
    for script in scripts_to_run:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'script', script)
        if not os.path.exists(script_path):
            print(f"错误: 找不到脚本文件 {script_path}")
            all_scripts_exist = False
    
    if not all_scripts_exist:
        print("请确保所有必需的脚本文件都存在于script目录中!")
        sys.exit(1)
    
    # 按顺序执行每个脚本
    success_count = 0
    for script in scripts_to_run:
        if run_script(script):
            success_count += 1
        else:
            # 如果某个脚本执行失败，可以选择继续或退出
            print(f"\n警告: {script} 执行失败，是否继续执行下一个脚本? (y/n)")
            choice = input().strip().lower()
            if choice != 'y':
                print("用户选择停止执行!")
                break
    
    # 总结执行结果
    end_total_time = time.time()
    print("\n" + "="*50)
    print("一键运行脚本集执行完成!")
    print(f"总执行时间: {end_total_time - start_total_time:.2f} 秒")
    print(f"成功执行: {success_count}/{len(scripts_to_run)} 个脚本")
    print("="*50)
    
    # 执行Git命令
    run_git_commands()

if __name__ == '__main__':
    main()