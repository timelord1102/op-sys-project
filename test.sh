#!/bin/bash

python3 project.py 3 1 32 0.001 1024 4 .75 256 > test.txt
diff -w test.txt outputs/p1output02.txt
diff -w simout.txt outputs/simout02.txt

python3 project.py 8 6 768 0.001 1024 6 .95 128 > test.txt
diff -w test.txt outputs/p1output03.txt
diff -w simout.txt outputs/simout03.txt

python3 project.py 16 2 256 0.001 2048 4 .45 32 > test.txt
diff -w test.txt outputs/p1output04.txt
diff -w simout.txt outputs/simout04.txt

python3 project.py 20 16 128 0.01 4096 4 0.99 64 > test.txt
diff -w test.txt outputs/p1output05.txt
diff -w simout.txt outputs/simout05.txt

python3 project.py 3 1 32 0.001 512 4 -1 512 > test.txt
diff -w test.txt outputs/p2output06.txt
diff -w simout.txt outputs/simout06.txt

python3 project.py 8 6 768 0.001 1024 6 -1 128 RR_ALT > test.txt
diff -w test.txt outputs/p2output07.txt
diff -w simout.txt outputs/simout07.txt