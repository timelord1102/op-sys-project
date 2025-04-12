#!/bin/bash

python3 project.py 3 1 32 0.001 1024 4 -1 256
# python3 project.py 1 0 1 0.001 100 4 .75 256 > test.txt
# python3 project.py 20 12 2 0.001 100 4 .75 256 > test.txt
# python3 project.py 20 16 3 0.001 100 4 .75 256 > test.txt
# python3 project.py 20 11 4 0.001 100 4 .75 256 > test.txt
# python3 project.py 20 13 5 0.001 100 4 .75 256 > test.txt
# python3 project.py 20 14 6 0.001 100 4 .75 256 > test.txt
# python3 project.py 20 15 7 0.001 100 4 .75 256 > test.txt
# python3 project.py 10 0 8 0.001 1024 4 .75 256 > test.txt


# --------------------full outputs--------------------------
# python3 project.py 3 1 32 0.001 1024 4 .75 256 > test.txt
# diff -w test.txt outputs/p1output02.txt

# python3 project.py 8 6 768 0.001 1024 6 .95 128 > test.txt
# diff -w test.txt outputs/p1output03.txt

# python3 project.py 16 2 256 0.001 2048 4 .45 32 > test.txt
# diff -w test.txt outputs/p1output04.txt

# python3 project.py 20 16 128 0.01 4096 4 0.99 64 > test.txt
# diff test.txt outputs/p1output05.txt

# python3 project.py 1 1 512 0.01 4096 4 0.99 64 > test.txt

# python3 project.py 18 10 512 0.01 4096 4 0.99 64 > test.txt

# python3 project.py 12 4 64 0.01 4096 4 0.99 64 > test.txt


# ------------------------FCFS------------------------------
# python3 project.py 3 1 32 0.001 1024 4 .75 256 > test.txt
# diff -w test.txt 02_fcfs.txt

# python3 project.py 8 6 768 0.001 1024 6 .95 128 > test.txt
# diff -w test.txt 03_fcfs.txt

# python3 project.py 16 2 256 0.001 2048 4 .45 32 > test.txt
# diff -w test.txt 04_fcfs.txt

# python3 project.py 20 16 128 0.01 4096 4 0.99 64 > test.txt
# diff -w test.txt 05_fcfs.txt

# python3 project.py 1 1 128 0.01 4096 4 0.99 64 > test.txt

# python3 main_test.py 20 16 128 0.01 4096 4 0.99 64 > test.txt

# ---------------------------SJF------------------------------
# python3 project.py 3 1 32 0.001 1024 4 .75 256 > test.txt
# diff -w test.txt 02_sjf.txt

# python3 project.py 8 6 768 0.001 1024 6 .95 128 > test.txt
# diff -w test.txt 03_sjf.txt

# python3 project.py 16 2 256 0.001 2048 4 .45 32 > test.txt
# diff -w test.txt 04_sjf.txt

# python3 project.py 20 16 128 0.01 4096 4 0.99 64 > test.txt
# diff -w test.txt 05_sjf.txt

# ---------------------------SRT------------------------------
# python3 project.py 3 1 32 0.001 1024 4 .75 256 > test.txt
# diff -w test.txt 02_srt.txt

# python3 project.py 8 6 768 0.001 1024 6 .95 128 > test.txt
# diff -w test.txt 03_srt.txt

# python3 project.py 16 2 256 0.001 2048 4 .45 32 > test.txt
# diff -w test.txt 04_srt.txt

# python3 project.py 20 16 128 0.01 4096 4 0.99 64 > test.txt
# diff -w test.txt 05_srt.txt

# python3 project.py 1 1 128 0.01 4096 4 0.99 64 > test.txt

# python3 main_test.py 20 16 128 0.01 4096 4 0.99 64 > test.txt

# ----------------------------RR------------------------------
# python3 project.py 3 1 32 0.001 1024 4 .75 256 > test.txt
# diff -w test.txt 02_rr.txt

# python3 project.py 8 6 768 0.001 1024 6 .95 128 > test.txt
# diff -w test.txt 03_rr.txt

# python3 project.py 16 2 256 0.001 2048 4 .45 32 > test.txt
# diff -w test.txt 04_rr.txt

# python3 project.py 20 16 128 0.01 4096 4 0.99 64 > test.txt
# diff -w test.txt 05_rr.txt

# python3 project.py 1 1 128 0.01 4096 4 0.99 64 > test.txt

# python3 main_test.py 20 16 128 0.01 4096 4 0.99 8 > test.txt

# ----------------------------------------------------------------------------------------
# rr vs fcfs
# ----------------------------------------------------------------------------------------
# python3 project.py 3 1 32 0.001 1024 4 .75 256 > test.txt
# python3 main_test.py 3 1 32 0.001 1024 4 .75 256 > test1.txt
# diff -w test.txt test1.txt

# python3 project.py 8 6 768 0.001 1024 6 .95 128 > test.txt
# python3 main_test.py 8 6 768 0.001 1024 6 .95 128 > test1.txt
# diff -w test.txt test1.txt

# python3 project.py 16 2 256 0.001 2048 4 .45 32 > test.txt
# python3 main_test.py 16 2 256 0.001 2048 4 .45 32 > test1.txt
# diff -w test.txt test1.txt

# python3 project.py 20 16 128 0.01 4096 4 0.99 64 > test.txt
# python3 main_test.py 20 16 128 0.01 4096 4 0.99 64 > test1.txt
# diff -w test.txt test1.txt

# python3 project.py 20 16 64 0.01 4096 4 0.99 64 > test.txt
# python3 main_test.py 20 16 64 0.01 4096 4 0.99 64 > test1.txt
# diff -w test.txt test1.txt

# python3 project.py 16 10 64 0.01 4096 4 0.99 64 > test.txt
# python3 main_test.py 16 10 64 0.01 4096 4 0.99 64 > test1.txt
# diff -w test.txt test1.txt

# python3 project.py 16 10 512 0.01 4096 4 0.99 64 > test.txt
# python3 main_test.py 16 10 512 0.01 4096 4 0.99 64 > test1.txt
# diff -w test.txt test1.txt

# ------------------------simout checks------------------------------------------

# python3 project.py 3 1 32 0.001 1024 4 .75 256 > test.txt
# diff -w simout.txt outputs/simout02.txt

# python3 project.py 8 6 768 0.001 1024 6 .95 128 > test.txt
# diff -w simout.txt outputs/simout03.txt

# python3 project.py 16 2 256 0.001 2048 4 .45 32 > test.txt
# diff -w simout.txt outputs/simout04.txt

# python3 project.py 20 16 128 0.01 4096 4 0.99 64 > test.txt
# diff -w simout.txt outputs/simout05.txt