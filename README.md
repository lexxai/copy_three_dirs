# copy three dirs

### help

usage: test_cp.py [-h] [-V] [--work WORK] --input1 INPUT1 --input2 INPUT2 [--output OUTPUT] [--found FOUND] [--notfound NOTFOUND] [--verbose]

options:
  -h, --help           show this help message and exit
  -V, --version        show version of app
  --work WORK          Directory for work. Is prefix for all other directories, default ''
  --input1 INPUT1      Directory for input1 (source list)
  --input2 INPUT2      Directory for input2 (compare list)
  --output OUTPUT      Directory for output, default 'output'
  --found FOUND        Directory for found, default 'found'
  --notfound NOTFOUND  Directory for notfound, default 'notfound'
  --verbose            verbose output



### result 

```
test_cp.py  --work tests --input1 INPUT_1 --input2 INPUT_2 
The Input1 folder 'INPUT_1' consist of files: 39
The Input2 folder 'INPUT_2' consist of files: 39
2023-09-11 15:07:01,121 [ MainThread ]  Copy only common files by name to 'tests\output' folder
2023-09-11 15:07:01,121 [ MainThread ]  Thread Copy files : 38.
Copy to output   : 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 38/38 [00:00<00:00, 186.28it/s]
2023-09-11 15:07:01,356 [ MainThread ]  Copy found files to 'tests\found' folder
2023-09-11 15:07:01,356 [ MainThread ]  Thread Copy files : 38.
Copy to found    : 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 38/38 [00:00<00:00, 192.76it/s]
2023-09-11 15:07:01,569 [ MainThread ]  Copy notfound files to 'tests\notfound' folder
2023-09-11 15:07:01,569 [ MainThread ]  Thread Copy files : 1.
2023-09-11 15:07:01,569 [ ThreadPoolExecutor-2_0 ]  error copy: _00001.tif                                                                                                  
Copy to notfound : 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<?, ?it/s]

Error copy files (1): ['_00001.tif']

```