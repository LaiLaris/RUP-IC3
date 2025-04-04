import subprocess
import threading

# 定义脚本的基础路径
script_base_path = "/home/ubuntu/Lustre-exp/bin/scripts"

# 定义单线程执行的脚本
sequential_scripts = [
    # f"{script_base_path}/l1l2/base_run_l1l2.py",
    # f"{script_base_path}/l1l2/reuse_run_l1l2.py",
    # f"{script_base_path}/l1l2/unsatcore_run_l1l2.py",
    # f"{script_base_path}/l1l2/reuse_and_unsatcore_run_l1l2.py",
    
    #最后和base比较
    # f"{script_base_path}/base_run_1719.py",
]
# 定义并行执行的脚本
parallel_scripts = [
    # f"{script_base_path}/3thread_run_1719.py",
    f"{script_base_path}/3in1_run_1719.py"
]

# 定义清理脚本路径
shutdown_script = f"{script_base_path}/utils/batch_shutdown.sh"

# 定义 Python 解释器路径
python_path = "/usr/bin/python3"

# 顺序执行脚本
def run_sequential_scripts(scripts):
    for script in scripts:
        print(f"Running {script}...")
        try:
            result = subprocess.run([python_path, script], check=True, text=True, capture_output=True)
            print(f"Output from {script}:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")
        except subprocess.CalledProcessError as e:
            print(f"Error running {script}:\nstdout:\n{e.stdout}\nstderr:\n{e.stderr}")
        print(f"Finished running {script}\n")

        # 运行清理脚本
        print(f"Running cleanup script: {shutdown_script}...")
        subprocess.run([shutdown_script], check=True, text=True, shell=True)
        print(f"Cleanup script executed successfully.\n")

# 并行执行脚本
def run_parallel_script(script):
    print(f"Running {script} in parallel...")
    try:
        result = subprocess.run([python_path, script], check=True, text=True, capture_output=True)
        print(f"Output from {script}:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script}:\nstdout:\n{e.stdout}\nstderr:\n{e.stderr}")
    print(f"Finished running {script}\n")

    # 运行清理脚本
    print(f"Running cleanup script: {shutdown_script}...")
    subprocess.run([shutdown_script], check=True, text=True, shell=True)
    print(f"Cleanup script executed successfully.\n")

# 主程序
if __name__ == "__main__":
    # 顺序执行非并行脚本
    print("Running sequential scripts...")
    run_sequential_scripts(sequential_scripts)
    print("All sequential scripts executed successfully.\n")

    # 并行执行脚本
    print("Running parallel scripts...")
    threads = []
    for script in parallel_scripts:
        thread = threading.Thread(target=run_parallel_script, args=(script,))
        threads.append(thread)
        thread.start()

    # 等待所有并行脚本完成
    for thread in threads:
        thread.join()

    print("All parallel scripts executed successfully.\n")

    print("All scripts executed successfully.")