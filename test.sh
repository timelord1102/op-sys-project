#!/bin/bash


# python3 main.py 3 1 32 0.001 1024 4 .75 256 > test.txt
# diff -w test.txt 02_fcfs.txt

# python3 main.py 8 6 768 0.001 1024 6 .95 128 > test.txt
# diff -w test.txt 03_fcfs.txt

# python3 main.py 16 2 256 0.001 2048 4 .45 32 > test.txt
# diff -w test.txt 04_fcfs.txt

# python3 main.py 20 16 128 0.01 4096 4 0.99 64 > test.txt
# diff -w test.txt 05_fcfs.txt

# ---------------------------SJF------------------------------
# python3 main.py 3 1 32 0.001 1024 4 .75 256 > test.txt
# diff -w test.txt 02_sjf.txt

# python3 main.py 8 6 768 0.001 1024 6 .95 128 > test.txt
# diff -w test.txt 03_sjf.txt

# python3 main.py 16 2 256 0.001 2048 4 .45 32 > test.txt
# diff -w test.txt 04_sjf.txt

# python3 main.py 20 16 128 0.01 4096 4 0.99 64 > test.txt
# diff -w test.txt 05_sjf.txt

# ---------------------------SRT------------------------------
# python3 main.py 3 1 32 0.001 1024 4 .75 256 > test.txt

python3 main.py 8 6 768 0.001 1024 6 .95 128 > test.txt



# ----------------------------RR------------------------------
# python3 main.py 3 1 32 0.001 1024 4 .75 256 > test.txt
# diff -w test.txt 02_rr.txt

# python3 main.py 8 6 768 0.001 1024 6 .95 128 > test.txt
# diff -w test.txt 03_rr.txt

# python3 main.py 16 2 256 0.001 2048 4 .45 32 > test.txt
# diff -w test.txt 04_rr.txt

# python3 main.py 20 16 128 0.01 4096 4 0.99 64 > test.txt
# diff -w test.txt 05_rr.txt

# ----------------------------------------------------------------------------------------
# rr vs fcfs
# ----------------------------------------------------------------------------------------
# python3 main.py 3 1 32 0.001 1024 4 .75 256 > test.txt
# python3 main_test.py 3 1 32 0.001 1024 4 .75 256 > test1.txt
# diff -w test.txt test1.txt

# python3 main.py 8 6 768 0.001 1024 6 .95 128 > test.txt
# python3 main_test.py 8 6 768 0.001 1024 6 .95 128 > test1.txt
# diff -w test.txt test1.txt

# python3 main.py 16 2 256 0.001 2048 4 .45 32 > test.txt
# python3 main_test.py 16 2 256 0.001 2048 4 .45 32 > test1.txt
# diff -w test.txt test1.txt

# python3 main.py 20 16 128 0.01 4096 4 0.99 64 > test.txt
# python3 main_test.py 20 16 128 0.01 4096 4 0.99 64 > test1.txt
# diff -w test.txt test1.txt

# python3 main.py 20 16 64 0.01 4096 4 0.99 64 > test.txt
# python3 main_test.py 20 16 64 0.01 4096 4 0.99 64 > test1.txt
# diff -w test.txt test1.txt

# python3 main.py 16 10 64 0.01 4096 4 0.99 64 > test.txt
# python3 main_test.py 16 10 64 0.01 4096 4 0.99 64 > test1.txt
# diff -w test.txt test1.txt

# python3 main.py 16 10 512 0.01 4096 4 0.99 64 > test.txt
# python3 main_test.py 16 10 512 0.01 4096 4 0.99 64 > test1.txt
# diff -w test.txt test1.txt

# python3 main.py 20 16 8 0.01 4096 4 0.99 64