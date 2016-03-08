import redis
import time
import datetime as dt
import calendar
import json
import os
import sys

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

nyt_user_id = '807095'
redis_creation_time_key = "statusCreationTime"
# 6 hours
ttl = 6 * 60 * 60 
consumer_key = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_token_secret = os.environ['ACCESS_TOKEN_SECRET']

def get_unix_time(twitter_timestring):
    '''
    Convert Twitter's text-formatted timestamp to unix time (UTC).
    '''
    time_tuple = time.strptime(twitter_timestring,"%a %b %d %H:%M:%S +0000 %Y")
    unix_time = calendar.timegm(time_tuple)
    return unix_time


class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    """
    def on_data(self, data):
        status = json.loads(data) 
        tstring = status['created_at']
        unix_time = get_unix_time(tstring)

        try:
            retweeted_status = status["retweeted_status"]
            if retweeted_status['user']['id_str'] == nyt_user_id:
                nyt_status_id = retweeted_status['id']
                metadata_key = "statusMetadata:{}".format(nyt_status_id)
                conn.hincrby(metadata_key, 'num_retweets')
                # print time of retweet event to stdout
                # to enable other process to compute rate of 
                # retweets of NYT statuses
                print json.dumps({"t": unix_time})
                sys.stdout.flush()
        except KeyError:
            # New status created by the NYT
            if status['user']['id_str'] == nyt_user_id:
                conn.zadd(redis_creation_time_key, status['id_str'], unix_time)
                metadata_key = "statusMetadata:{}".format(status['id_str'])
                metadata = {"num_retweets": 0, "text": status['text']}
                conn.hmset(metadata_key, metadata)
                conn.expire(metadata_key, ttl)
                '''
                print metadata_key
                print metadata
                '''
    
    def on_error(self, status):
        print status

if __name__ == '__main__': 
    conn = redis.Redis()
    listener = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, listener)
    stream.filter(follow=[nyt_user_id])
