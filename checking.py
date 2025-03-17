with open('input1.txt', 'r') as file1, open('input2.txt', 'r') as file2:
    contents1 = file1.readlines()
    contents2 = file2.readlines()

differences = False

# Compare line by line
for i, (line1, line2) in enumerate(zip(contents1, contents2), start=1):
    if line1 != line2:
        print(f"Difference at line {i}:\nFile1: {line1.strip()}\nFile2: {line2.strip()}\n")
        differences = True

# Check for extra lines in file1
if len(contents1) > len(contents2):
    print(f"Extra lines in input1.txt starting from line {len(contents2) + 1}:")
    for i in range(len(contents2), len(contents1)):
        print(f"Line {i+1} (File1): {contents1[i].strip()}")
    differences = True

# Check for extra lines in file2
elif len(contents2) > len(contents1):
    print(f"Extra lines in input2.txt starting from line {len(contents1) + 1}:")
    for i in range(len(contents1), len(contents2)):
        print(f"Line {i+1} (File2): {contents2[i].strip()}")
    differences = True

if not differences:
    print("The contents of input1.txt and input2.txt are the same.")
