# copy three dirs

### help

```
usage: test_cp.py [-h] [-V] [--work WORK] --input1 INPUT1 --input2 INPUT2 [--output OUTPUT] [--found FOUND] [--notfound1 NOTFOUND1] [--notfound2 NOTFOUND2] [--joined JOINED]
                  [--join] [--join_only] [--verbose]

options:
  -h, --help            show this help message and exit
  -V, --version         show version of app
  --work WORK           Directory for work. Is prefix for all other directories that is not absolute, default ''
  --input1 INPUT1       Directory for input1 (source list)
  --input2 INPUT2       Directory for input2 (compare list)
  --output OUTPUT       Directory for output, default 'Output'
  --found FOUND         Directory for found, default 'Found'
  --notfound1 NOTFOUND1
                        Directory for notfound 1 (input1 diff from input2), default 'NotFound_1'
  --notfound2 NOTFOUND2
                        Directory for notfound 2 (input2 diff from input1), default 'NotFound_2'
  --joined JOINED       Directory for joined images of 'output' and 'found' directories, default 'Joined'
  --join                to join images of 'output' and 'found' directories
  --join_only           to join images of 'output' and 'found' directories, without all other operations
  --verbose             verbose output

```



### result 

```
python copy_three_dirs\main.py --work tests --input1 INPUT_1 --input2 INPUT_2 
The Input1 folder 'INPUT_1' consist of files: 39
The Input2 folder 'INPUT_2' consist of files: 40
2023-09-11 19:54:14,920 [ MainThread ]  Copy only common files by name to 'tests\Output' folder
2023-09-11 19:54:14,920 [ MainThread ]  Thread Copy files : 38.
Copy to Output   : 100%|██████████| 38/38 [00:00<00:00, 145.39it/s]
2023-09-11 19:54:15,195 [ MainThread ]  Copy found files to 'tests\Found' folder
2023-09-11 19:54:15,196 [ MainThread ]  Thread Copy files : 38.
Copy to Found    : 100%|██████████| 38/38 [00:00<00:00, 172.65it/s]
2023-09-11 19:54:15,422 [ MainThread ]  Copy notfound files to 'tests\NotFound_1' folder
2023-09-11 19:54:15,422 [ MainThread ]  Thread Copy files : 1.
Copy to NotFound_1: 100%|██████████| 1/1 [00:00<00:00, 117.46it/s]
2023-09-11 19:54:15,433 [ MainThread ]  Copy notfound files to 'tests\NotFound_2' folder
2023-09-11 19:54:15,433 [ MainThread ]  Thread Copy files : 2.
Copy to NotFound_2: 100%|██████████| 2/2 [00:00<00:00, 142.90it/s]

```
### --join
image1: A

image2: B

result: AB, (width: A.width * 2, height: A.height)

```
python copy_three_dirs\main.py --work tests --input1 INPUT_1 --input2 INPUT_2 --join 
2023-09-11 18:44:06,006 [ MainThread ]  Copy only common files by name to 'tests\Output' folder
2023-09-11 18:44:06,006 [ MainThread ]  Thread Copy files : 38.
The Input1 folder 'INPUT_1' consist of files: 39
The Input2 folder 'INPUT_2' consist of files: 39
Copy to Output   : 100%|██████████| 38/38 [00:00<00:00, 79.32it/s] 
2023-09-11 18:44:06,500 [ MainThread ]  Copy found files to 'tests\Found' folder
2023-09-11 18:44:06,500 [ MainThread ]  Thread Copy files : 38.
Copy to Found    : 100%|██████████| 38/38 [00:00<00:00, 152.75it/s]
2023-09-11 18:44:06,757 [ MainThread ]  Copy notfound files to 'tests\Notfound' folder
2023-09-11 18:44:06,757 [ MainThread ]  Thread Copy files : 1.
Copy to Notfound : 100%|██████████| 1/1 [00:00<00:00, 100.04it/s]
2023-09-11 18:44:06,775 [ MainThread ]  Processes (4) of Join files : 38.
Join to Joined   : 100%|██████████| 38/38 [00:02<00:00, 13.28it/s]

```


### --join_only 
```
python copy_three_dirs\main.py  --work tests --input1 INPUT_1 --input2 INPUT_2 --join_only 
2023-09-11 18:32:13,785 [ MainThread ]  Processes (4) of Join files : 38.
Join to joined   : 100%|██████████| 38/38 [00:01<00:00, 19.42it/s]
```

### join mode CPU
``` [--join_mode {one_core,future_core,future_thread,future_core_async}]```

#### future_thread
```
 --input1 INPUT_1 --input2 INPUT_2 --join_only --join_mode future_thread
2023-09-12 00:01:50,040 [ MainThread ]  Threads (10) of Join files : 38.
Join to Joined   : 100%|██████████| 38/38 [00:01<00:00, 31.16it/s]
```

#### future_core
```
--input1 INPUT_1 --input2 INPUT_2 --join_only --join_mode future_core  
2023-09-12 00:06:06,790 [ MainThread ]  Processes (4) of Join files : 38.
Join to Joined   : 100%|██████████| 38/38 [00:01<00:00, 23.15it/s]

```

#### future_core_async
```
 --input1 INPUT_1 --input2 INPUT_2 --join_only --join_mode future_core_async
2023-09-12 00:25:28,425 [ MainThread ]  Processes (4) of Join files : 38.
Join to Joined   : 100%|██████████| 38/38 [00:01<00:00, 23.25it/s]
```

#### one_core
```
--input1 INPUT_1 --input2 INPUT_2 --join_only --join_mode one_core    
2023-09-12 00:10:06,096 [ MainThread ]  One core process of Join files : 38.         
Join to Joined   : 100%|██████████| 38/38 [00:01<00:00, 19.40it/s]
```
