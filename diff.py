import json
import sys

if __name__ == "__main__":
    last_unix_time = 0
    while 1:
        line = sys.stdin.readline()
        timestamp = json.loads(line)["t"]
        if last_unix_time == 0:
            last_unix_time = timestamp
            continue
        delta = timestamp - last_unix_time
        print json.dumps({"delta": delta, "unix_time": timestamp})
        sys.stdout.flush()
        last_unix_time = timestamp
