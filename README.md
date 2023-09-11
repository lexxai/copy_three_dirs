# copy three dirs

### help

```
usage: test_cp.py  [-h] [-V] [--work WORK] --input1 INPUT1 --input2 INPUT2 [--output OUTPUT] [--found FOUND] [--notfound NOTFOUND] [--joined JOINED] [--join] [--join_only]
                  [--verbose]

options:
  -h, --help           show this help message and exit
  -V, --version        show version of app
  --work WORK          Directory for work. Is prefix for all other directories that is not absolute, default ''
  --input1 INPUT1      Directory for input1 (source list)
  --input2 INPUT2      Directory for input2 (compare list)
  --output OUTPUT      Directory for output, default 'Output'
  --found FOUND        Directory for found, default 'Found'
  --notfound NOTFOUND  Directory for notfound, default 'Notfound'
  --joined JOINED      Directory for joined images of 'output' and 'found' directories, default 'Joined'
  --join               to join images of 'output' and 'found' directories
  --join_only          to join images of 'output' and 'found' directories, without all other operations
  --verbose            verbose output
```



### result 

```
python copy_three_dirs\main.py   --work tests --input1 INPUT_1 --input2 INPUT_2 
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