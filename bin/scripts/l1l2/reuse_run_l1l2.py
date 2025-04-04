import re
import subprocess
import csv
import argparse
import shlex
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures import ProcessPoolExecutor

# 定义匹配时间、帧大小和重用次数的正则表达式
pattern_ic3_total_time = re.compile(r'Final statistics:[\s\S]*?\[IC3\][\s\S]*?Total time\s+:\s+([\d.]+)')
pattern_ic3_k = re.compile(r'Final statistics:[\s\S]*?\[IC3\][\s\S]*?k\s+:\s+([\d.]+)')
pattern_ic3_solver = re.compile(r'Final statistics:[\s\S]*?\[IC3\][\s\S]*?Solver\s+:\s+(\d+(?:\s+\d+)*)')
pattern_ic3_neg_state_solver = re.compile(r'Final statistics:[\s\S]*?\[IC3\][\s\S]*?Neg_state\s+:\s+(\d+(?:\s+\d+)*)')
pattern_ic3_frame_sizes = re.compile(r'Final statistics:[\s\S]*?\[IC3\][\s\S]*?Frame sizes\s+:\s+(\d+(?:\s+\d+)*)')
pattern_ic3_reuse_num_s = re.compile(r'Final statistics:[\s\S]*?\[IC3\][\s\S]*?Reuse_num_s\s+:\s+(\d+)')
pattern_ic3_reuse_num_t = re.compile(r'Final statistics:[\s\S]*?\[IC3\][\s\S]*?Reuse_num_t\s+:\s+(\d+)')
pattern_ic3_reuse_num_gen = re.compile(r'Final statistics:[\s\S]*?\[IC3\][\s\S]*?Reuse_num_gen\s+:\s+(\d+)')

# 读取输入文件中的路径
def read_file_paths(input_file):
    with open(input_file, 'r') as f:
        return [line.strip() for line in f]

# 执行kind2命令并提取数据
def execute_command_and_get_data(file_path):
    
    kind2_command = f"/home/ubuntu/Lustre-exp/bin/exe/R-IC3_l1l2 --enable IC3QE -vv --timeout 290 --color false  {file_path}"
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
        reuse_num_s_match = pattern_ic3_reuse_num_s.search(output)
        reuse_num_t_match = pattern_ic3_reuse_num_t.search(output)
        reuse_num_gen_match = pattern_ic3_reuse_num_gen.search(output)  # 添加此行


        valid_match = re.search(r'<Success> Property .* is valid .*', output)
        invalid_match = re.search(r'<Failure> Property .* is invalid .*', output)

        total_time = total_time_match.group(1) if total_time_match else "Not Found"
        k = k_match.group(1) if k_match else "Not Found"
        solver = solver_match.group(1) if solver_match else "Not Found"
        neg_state_solver = neg_state_solver_match.group(1) if neg_state_solver_match else "Not Found"
        frame_sizes = frame_sizes_match.group(1) if frame_sizes_match else "Not Found"
        reuse_num_s = reuse_num_s_match.group(1) if reuse_num_s_match else "Not Found"
        reuse_num_t = reuse_num_t_match.group(1) if reuse_num_t_match else "Not Found"
        reuse_num_gen = reuse_num_gen_match.group(1) if reuse_num_gen_match else "Not Found"  # 添加此行
        
        if valid_match:
            status = "safe"
        elif invalid_match:
            status = "unsafe"
        else:
            status = "timeout"
        return total_time, k, solver, neg_state_solver, reuse_num_s, reuse_num_t, reuse_num_gen,status, frame_sizes
    except subprocess.TimeoutExpired:
        return "timeout", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A","N/A","N/A","N/A"

# 写入输出文件
def append_result_to_csv(file_path, total_time, k, solver, neg_state_solver, 
                         reuse_num_s, reuse_num_t, reuse_num_gen, status, frame_sizes, elapsed_time, output_file):
    with open(output_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([file_path, total_time, k, solver, neg_state_solver, 
                         reuse_num_s, reuse_num_t, reuse_num_gen, status, frame_sizes,
                         f"{elapsed_time:.3f}"])

def process_file(file_path, output_file):
    elapsed_start_time = time.time()  # 记录每个文件处理的开始时间
    
    result = execute_command_and_get_data(file_path)
    if result[0] == "timeout":
        elapsed_time = time.time() - elapsed_start_time
        append_result_to_csv(file_path, *result, elapsed_time, output_file)
        return elapsed_time

    # 计算执行时间
    elapsed_time = time.time() - elapsed_start_time

    # 写入 CSV 文件
    append_result_to_csv(file_path, *result, elapsed_time, output_file)

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
    # parser.add_argument('--input_file', type=str, required=True, help='Path to the input file containing file paths')
    # parser.add_argument('--output_file', type=str, required=True, help='Path to the output CSV file')

    # args = parser.parse_args()
    # input_file = args.input_file
    # output_file = args.output_file

    input_file = '/home/ubuntu/Lustre-exp/bin/path/l1l2_513_path.txt'  # lus_path
    output_file = '/home/ubuntu/Lustre-exp/bin/result/l1l2/R-IC3_l1l2.csv'  # csv_file
    
    file_paths = read_file_paths(input_file)
    
    # 初始化输出文件，写入标题
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Reuse_file_path", "Reuse_time", "Reuse_k", "Reuse_solver", "Reuse_neg_state", "Reuse_num_s", "Reuse_num_t", "Reuse_num_gen", "Reuse_status", "Reuse_frame_sizes", "Reuse_elapsed_time"])
    
    # 使用 ThreadPoolExecutor 进行并行处理
    with ProcessPoolExecutor(max_workers=24) as executor:
        futures = {executor.submit(process_file, file_path, output_file): file_path for file_path in file_paths}

        for future in as_completed(futures):
            file_path = futures[future]
            try:
                elapsed_time = future.result()  # 获取每个文件处理的耗时
            except Exception as exc:
                print(f"File {file_path} generated an exception: {exc}")

    # 处理完成后对CSV文件进行排序
    # sort_csv_file(output_file)

if __name__ == "__main__":
    main()