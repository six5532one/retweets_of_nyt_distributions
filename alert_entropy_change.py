import requests
import json
import time
import redis
import tweepy
import os
import numpy as np

from tweepy.error import TweepError

conn = redis.Redis()
# alert if entropy is less than this many standard deviations below the mean
zscore_threshold = -1.5
# API base url
url = "http://{}:5000".format(os.environ["API_BASE_URL"])

def zscore(entropy):
    '''
    Given an entropy value, returns its distance from the mean entropy as
    the number of standard deviations.
    '''
    keys = conn.keys("entropy:*")
    entropy_vals = np.array([float(val) for val in conn.mget(keys)])
    mean_entropy = np.mean(entropy_vals)
    std_dev = np.std(entropy_vals)
    return (entropy - mean_entropy)/std_dev

def below_entropy_threshold(entropy):
    '''
    Given an entropy value, returns whether it is less than the threshold
    number of standard deviations away from the mean entropy.
    '''
    return zscore(entropy) < zscore_threshold 

def get_most_retweeted():
    '''
    Returns the original @nytimes status, published within 
    2 to 6 hours ago, that has been retweeted the most up to this point.
    '''
    r = requests.get("{}/distribution".format(url))
    dist = json.loads(r.text)
    max_mass = -1
    most_retweeted = None
    for status_text, num_retweets in dist.iteritems():
        if num_retweets > max_mass:
            max_mass = num_retweets
            most_retweeted = status_text
    return most_retweeted

if __name__ == "__main__":
    CONSUMER_KEY = os.environ["BOT_CONSUMER_KEY"]
    CONSUMER_SECRET = os.environ["BOT_CONSUMER_SECRET"]
    ACCESS_TOKEN = os.environ["BOT_ACCESS_TOKEN"]
    ACCESS_TOKEN_SECRET = os.environ["BOT_ACCESS_TOKEN_SECRET"]
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    twitter_api_wrapper = tweepy.API(auth)
  
    while True:
        # make call to entropy API endpoint
        r = requests.get("{}/entropy".format(url))
        entropy = json.loads(r.text)["entropy"]
        # save entropy observation in redis
        conn.set("entropy:{}".format(time.time()), entropy)
        if below_entropy_threshold(entropy):
            most_retweeted_text = get_most_retweeted()
            tweet_text = "Entropy < {thres} stddev. Most likely RT: {text}".format(thres=zscore_threshold, text=most_retweeted_text)
            while True:
                try:
                    twitter_api_wrapper.update_status(tweet_text)
                    break
                except TweepError as e:
                    err_code = e[0][0]['code']
                    # duplicate msg
                    if err_code == 187:
                        modified_tweet_text = "t={curtime}: Entropy < {thres} stddev. Most likely RT same as previous.".format(curtime=time.time(), thres=zscore_threshold)
                    # status exceeds 140
                    elif err_code == 186:
                        nyt_url = None
                        for token in most_retweeted_text.split(" "):
                            if token.find("http://") > -1 or token.find("https://") > -1:
                                nyt_url = token
                        if nyt_url:
                            modified_tweet_text = "Entropy < {thres} stddev. Most likely RT: {nyt_url}".format(thres=zscore_threshold, nyt_url=nyt_url)
                        else:
                            modified_tweet_text = tweet_text[:120]
                    tweet_text = modified_tweet_text
        time.sleep(30 * 60)
