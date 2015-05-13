import boto
import datetime
import time
import os
import errno
import sys
from pprint import pprint

logs = boto.connect_logs()


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def get_with_next(func, key, next_token_field,  **kwargs):
    tries = tries_left = 10
    while (tries_left):
        try:
            tmp = func(**kwargs)
            sys.stdout.write(".")
            sys.stdout.flush()
            break
        except boto.exception.JSONResponseError as e:
            if e.error_code == 'ThrottlingException':
                tries_left -= 1
                # ref: http://en.wikipedia.org/wiki/Exponential_backoff#Binary_exponential_backoff_.2F_truncated_exponential_backoff
                s = int((pow(2, tries - tries_left) - 1) / 2)
                print "Throttled :( -- sleeping for %s, %s tries left" % (s, tries_left)
                time.sleep(s)

    ret = tmp[key]
    if next_token_field and next_token_field in tmp and ret:
        kwargs['next_token'] = tmp[next_token_field]
        #print "subcall %s" % kwargs
        ret += get_with_next(func, key, next_token_field, **kwargs)
    return ret

print "starting"
groups = logs.describe_log_groups()['logGroups']
print "Got groups list"
for group in groups:
    print "Getting streams for %s" % group['logGroupName']
    streams = get_with_next(
        logs.describe_log_streams,
        'logStreams',
        'nextToken',
        log_group_name=group['logGroupName']
    )
    print "%s %s" % (group['logGroupName'], len(streams))
    for stream in streams:
        filename = "%s/%s" % (group['logGroupName'], stream['logStreamName'])
        mkdir_p("/".join(filename[1:].split("/")[:-1]))
        with open(filename[1:], 'w') as fh:
            print filename[1:]
            # here we save the logs to the fs
            lines = get_with_next(
                logs.get_log_events,
                'events',
                'nextForwardToken',
                log_group_name=group['logGroupName'],
                log_stream_name=stream['logStreamName']
            )
            for line in lines:
                ts = datetime.datetime.fromtimestamp(int(line['timestamp']/1000))
                fh.write("%s %s" % (ts.strftime('%Y-%m-%d %H:%M:%S'), line['message'].strip()))
