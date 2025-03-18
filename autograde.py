import os

if __name__ == "__main__":
    parameters = ["python3 main.py 3 1 32 0.001 1024 4 0.75 256",
        "python3 main.py 8 6 768 0.001 1024 6 .95 256",
        "python3 main.py 16 2 256 0.001 2048 4 .45 32",
        "python3 main.py 20 16 128 0.01 4096 4 0.99 64",
    ]
    for i in range(len(parameters)):
        print(parameters[i])
        print(f"Running test for q{i+2}")
        if os.path.exists("./autograding/output.txt"):
                    os.remove("./autograding/output.txt")
        os.system(f"{parameters[i]} >> ./autograding/output.txt")
        with open("./autograding/output.txt", "r") as output_file, open(f"./autograding/q{i+2}/expectedfcfs.txt", "r") as expected_file:
            output_lines = output_file.readlines()
            expected_lines = expected_file.readlines()
            for line_num, (output_line, expected_line) in enumerate(zip(output_lines, expected_lines)):
                if output_line != expected_line:
                    print(f"Difference found on line {line_num}:")
                    print(f"Output: {output_line.strip()}")
                    print(f"Expected: {expected_line.strip()}")
