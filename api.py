import flask
import redis
import time

from flask import request

app = flask.Flask(__name__)
conn = redis.Redis()

def buildDist():
    current_time = time.time()
    start_hours_ago = 6
    #end_hours_ago = 2
    end_hours_ago = 0
    start_unix_time = current_time - start_hours_ago * 60 * 60
    end_unix_time = current_time - end_hours_ago * 60 * 60 
    dist = {}
    ids_of_timely_tweets = conn.zrangebyscore("statusCreationTime", start_unix_time, end_unix_time)
    total_retweet_count = 0
    for id_str in ids_of_timely_tweets:
        category = conn.hgetall("statusMetadata:{}".format(id_str))
        count = int(category['num_retweets'])
        if count == 0:
            continue
        dist[category['text']] = count
        total_retweet_count += count
    for category, count in dist.items():
        dist[category] = float(count)/total_retweet_count
    return dist

@app.route("/distribution")
def distribution():
    dist = buildDist()
    return flask.jsonify(**dist)

@app.route("/probability")
def probability():
    '''
    Returns the probability that a tweet created by 
    the NYT, that contains the specified phrase in its
    text, is retweeted.    
    '''
    phrase = request.args.get("phrase")
    prob = 0
    if phrase:
        dist = buildDist()
        for category, mass in dist.iteritems():
            # phrase exists in the text of this tweet
            if category.find(phrase) > -1:
                prob += mass
    payload = {"phrase": phrase,
               "probability": prob}
    return flask.jsonify(**payload)

#@app.route("/entropy")
def entropy():
    dist = buildDist()
    pass

#@app.route("rate")
def stream_rate():
    pass

if __name__ == "__main__":
    app.run()
