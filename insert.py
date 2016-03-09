import json
import sys
import redis

'''
Inserts time deltas between consecutive messages in the stream,
into Redis. Uses Redis' TTL feature when inserting keys
to enforce a 120 second time window for computing average 
time delta between messages.

'''

if __name__ == "__main__":
    conn = redis.Redis()
    while 1:
        line = sys.stdin.readline()
        data = json.loads(line)
        print conn.setex("delta:{}".format(data["unix_time"]), data["delta"], 120)
