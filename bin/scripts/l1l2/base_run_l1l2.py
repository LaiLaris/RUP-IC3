import re
import subprocess
import csv
import argparse
import shlex
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures import ProcessPoolExecutor

# 定义匹配时间和帧大小的正则表达式
pattern_ic3_total_time = re.compile(r'Final statistics:[\s\S]*?\[IC3\][\s\S]*?Total time\s+:\s+([\d.]+)')
pattern_ic3_k = re.compile(r'Final statistics:[\s\S]*?\[IC3\][\s\S]*?k\s+:\s+([\d.]+)')
pattern_ic3_solver = re.compile(r'Final statistics:[\s\S]*?\[IC3\][\s\S]*?Solver\s+:\s+(\d+(?:\s+\d+)*)')
pattern_ic3_neg_state_solver = re.compile(r'Final statistics:[\s\S]*?\[IC3\][\s\S]*?Neg_state\s+:\s+(\d+(?:\s+\d+)*)')
pattern_ic3_frame_sizes = re.compile(r'Final statistics:[\s\S]*?\[IC3\][\s\S]*?Frame sizes\s+:\s+(\d+(?:\s+\d+)*)')

# 读取输入文件中的路径
def read_file_paths(input_file):
    with open(input_file, 'r') as f:
        return [line.strip() for line in f]

# 执行kind2命令并提取时间、k和帧大小
def execute_command_and_get_data(file_path):
    kind2_command = f"/home/ubuntu/Lustre-exp/bin/exe/O-IC3_l1l2 --enable IC3QE  -vv --timeout 290 --color false  {file_path}"
    print(kind2_command)
    args = shlex.split(kind2_command)
    
    try:
        result = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
        output = result.stdout

        total_time_match = pattern_ic3_total_time.search(output)
        k_match = pattern_ic3_k.search(output)
        solver_match = pattern_ic3_solver.search(output)
        neg_state_solver_match = pattern_ic3_neg_state_solver.search(output)
        frame_sizes_match = pattern_ic3_frame_sizes.search(output)

        valid_match = re.search(r'<Success> Property .* is valid .*', output)
        invalid_match = re.search(r'<Failure> Property .* is invalid .*', output)

        total_time = total_time_match.group(1) if total_time_match else "Not Found"
        k = k_match.group(1) if k_match else "Not Found"
        solver = solver_match.group(1) if solver_match else "Not Found"
        neg_state_solver = neg_state_solver_match.group(1) if neg_state_solver_match else "Not Found"
        frame_sizes = frame_sizes_match.group(1) if frame_sizes_match else "Not Found"
        
        if valid_match:
            status = "safe"
        elif invalid_match:
            status = "unsafe"
        else:
            status = "timeout"
        return total_time, k, solver, neg_state_solver, status, frame_sizes
    except subprocess.TimeoutExpired:
        return "timeout", "N/A", "N/A", "N/A", "N/A", "N/A"

# 写入输出文件
def append_result_to_csv(file_path, total_time, k, solver, neg_state_solver, status, 
                         frame_sizes, elapsed_time, output_file):
    with open(output_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([file_path, total_time, k, solver, neg_state_solver, status, 
                         frame_sizes, f"{elapsed_time:.3f}"])  # 移除total_elapsed_time

def process_file(file_path, output_file):
    elapsed_start_time = time.time()  # 记录每个文件处理的开始时间
    
    total_time, k, solver, neg_state_solver, status, frame_sizes = execute_command_and_get_data(file_path)

    # 计算执行时间
    elapsed_time = time.time() - elapsed_start_time  # 计算执行时间

    # 写入 CSV 文件
    append_result_to_csv(file_path, total_time, k, solver, neg_state_solver, status, 
                          frame_sizes, elapsed_time, output_file)

    return elapsed_time  # 返回当前文件处理的耗时

# def sort_csv_file(output_file):
#     # 读取CSV文件内容
#     with open(output_file, 'r', newline='') as csvfile:
#         reader = csv.reader(csvfile)
#         rows = list(reader)
#     # 保存标题行
#     header = rows[0]

#     # 按照第一列（文件路径）进行升序排序，不包括标题行
#     rows_sorted = sorted(rows[1:], key=lambda x: x[0])

#     # 将排序后的内容写回CSV文件
#     with open(output_file, 'w', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(header)  # 写入标题行
#         writer.writerows(rows_sorted)

def main():
    # parser = argparse.ArgumentParser(description='Process some files and output results to a CSV.')
    # parser.add_argument('--input_file', type=str, required=True, help='Path of the input file containing file paths')
    # parser.add_argument('--output_file', type=str, required=True, help='Path of the output CSV file')

    # args = parser.parse_args()
    # input_file = args.input_file
    # output_file = args.output_file

    input_file = '/home/ubuntu/Lustre-exp/bin/path/l1l2_513_path.txt'  # lus_path
    output_file = '/home/ubuntu/Lustre-exp/bin/result/l1l2/O-IC3_l1l2.csv'  # csv_file
    
    file_paths = read_file_paths(input_file)
    
    # 初始化输出文件，写入标题
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Base_file_path", "Base_time", "Base_k", "Base_solver", "Base_neg_state", "Base_status", 
                        "Base_frame_sizes", "Base_elapsed_time"])  # 修正了标题行的格式

    # 进行并行处理
    with ProcessPoolExecutor(max_workers=24) as executor:
        futures = [executor.submit(process_file, file_path, output_file) for file_path in file_paths]

        for future in as_completed(futures):
            try:
                elapsed_time = future.result()  # 获取每个文件处理的耗时
            except Exception as exc:
                print(f"File generated an exception: {exc}")

    # 处理完成后对CSV文件进行排序
    # sort_csv_file(output_file)

if __name__ == "__main__":
    main()