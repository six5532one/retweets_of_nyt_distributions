import redis
import time
import datetime as dt
import calendar
import json
import os

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

nyt_user_id = '807095'
redis_creation_time_key = "statusCreationTime"
consumer_key = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_token_secret = os.environ['ACCESS_TOKEN_SECRET']

class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    """
    def on_data(self, data):
        status = json.loads(data) 
        try:
            retweeted_status = status["retweeted_status"]
            if retweeted_status['user']['id_str'] == nyt_user_id:
                nyt_status_id = retweeted_status['id']
                '''
                urls = None
                entities = retweeted_status.get('entities', None)
                if entities:
                    urls = entities.get('urls', None)
                print urls
                '''
        except KeyError:
            # convert timestamp to unix time (UTC)
            if status['user']['id_str'] == nyt_user_id:
                tstring = status['created_at']
                time_tuple = time.strptime(tstring,"%a %b %d %H:%M:%S +0000 %Y")
                unix_time = calendar.timegm(time_tuple)
                conn.zadd(redis_creation_time_key, nyt_status_id=unix_time)
                metadata_key = "statusMetadata:{}".format(status['id'])
                metadata = {"num_retweets": 0, "text": status['text']}
                conn.hmset(metadata_key, metadata)
                print metadata_key
                print metadata
    
    def on_error(self, status):
        print status

if __name__ == '__main__': 
    conn = redis.Redis()
    listener = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, listener)
    stream.filter(follow=[nyt_user_id])
