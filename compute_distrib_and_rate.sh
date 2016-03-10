#!/usr/bin/env bash

cd /home/ubuntu/Python-2.7.9/myPython2.7.9
source bin/activate
cd /home/ubuntu/entropy_in_retweets_of_NYT
python event.py | python diff.py | python insert.py &>distrib_rate.log
