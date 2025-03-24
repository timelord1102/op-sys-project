import subprocess


subprocesses = {2:"python3 project.py 3 1 32 0.001 1024 4 .75 256 > test.txt",
3:"python3 project.py 8 6 768 0.001 1024 6 .95 128 > test.txt",
4:"python3 project.py 16 2 256 0.001 2048 4 .45 32 > test.txt",
5:"python3 project.py 20 16 128 0.01 4096 4 0.99 64 > test.txt"}

import difflib

for idx, process in subprocesses.items():
    subprocess.run(process, shell=True)
    with open("test.txt", "r") as test_file:
        test_lines = test_file.readlines()
    with open(f"./expected_outputs/p{idx}output.txt", "r") as expected_file:
        expected_lines = expected_file.readlines()

    for i, (test_line, expected_line) in enumerate(zip(test_lines, expected_lines)):
        if test_line != expected_line:
            diff = difflib.ndiff([expected_line], [test_line])
            print(f"Difference in line {i+1} of process {idx}:")
            print('\n'.join(diff))

    with open("simout.txt", "r") as test_file:
        test_lines = test_file.readlines()
    with open(f"./expected_outputs/p{idx}simout.txt", "r") as expected_file:
        expected_lines = expected_file.readlines()

    for i, (test_line, expected_line) in enumerate(zip(test_lines, expected_lines)):
        if test_line != expected_line:
            diff = difflib.ndiff([expected_line], [test_line])
            print(f"Difference in line {i+1} of process {idx}:")
            print('\n'.join(diff))
