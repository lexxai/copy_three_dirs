# copy three dirs

### help

usage: test_cp.py [-h] [-V] --input1 INPUT1 --input2 INPUT2 [--output OUTPUT] [--verbose]

options:
  -h, --help       show this help message and exit
  -V, --version    show version of app
  --input1 INPUT1  Directory for input1 (source list)
  --input2 INPUT2  Directory for input2 (compare list)
  --output OUTPUT  Directory for output, default 'output'
  --notfound NOTFOUND  Directory for notfound, default 'notfound'
  --verbose        verbose output


### result 

```
The Input1 folder 'INPUT_1' consist of files: 39
The Input2 folder 'INPUT_2' consist of files: 39
2023-09-11 02:28:14,591 [ MainThread ]  Thread Copy files : 38. Use copy with max threads: 10
100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 38/38 [00:00<00:00, 213.39it/s] 
2023-09-11 02:28:14,801 [ MainThread ]  Copy notfound files to 'notfound' folder
2023-09-11 02:28:14,801 [ MainThread ]  Thread Copy files : 1. Use copy with max threads: 10
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 45.16it/s] 

```