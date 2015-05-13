# cloudwatchlogs-downloader
Very simple python script that downloads all the logs from cloudwatch logs

The usage right now is very simple (and stupid). Run the .py and it will download whatever is present in your cloudwatch account. 

Steps:
```
pip install boto aws-cli
python get_logs.py
```

This will save a new file from each strean in your cloudwatch logs account. 


Requirements: Python 2.7

This is very very alpha, a couple of hours of hacking. Patches welcome!
