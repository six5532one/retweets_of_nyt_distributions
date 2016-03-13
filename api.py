import math
import flask
import redis
import time

from flask import request

app = flask.Flask(__name__)
conn = redis.Redis()

@app.after_request
def after(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

def buildDist():
    current_time = time.time()
    # Only include statuses published 2 to 6 hours ago as categories.
    # Statuses created less than 2 hours ago will not have had 
    # enough time for users to interact with them, and will not serve as a 
    # meaningful category in the probability distribution. If statuses 
    # created more than 6 hours ago are included in the distribution, the
    # distribution will have too many categories.
    start_hours_ago = 6
    end_hours_ago = 2
    start_unix_time = current_time - start_hours_ago * 60 * 60
    end_unix_time = current_time - end_hours_ago * 60 * 60 
    dist = {}
    # Retrieve IDs of @nytimes statuses published within the past 2 to 6 hours
    ids_of_timely_tweets = conn.zrangebyscore("statusCreationTime", start_unix_time, end_unix_time)
    total_retweet_count = 0
    for id_str in ids_of_timely_tweets:
        # Retrieve text and retweet count of this original @nytimes status
        category = conn.hgetall("statusMetadata:{}".format(id_str))
        count = int(category['num_retweets'])
        if count == 0:
            continue
        # Add category to disttribution
        dist[category['text']] = count
        total_retweet_count += count
    # normalize the probability distribution
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

@app.route("/entropy")
def entropy():
    '''
    Returns the information (Shannon) entropy that characterizes
    the current categorical distribution.

    The Shannon entropy of a probability distribution can be 
    thought of as the amount of information each new message 
    conveys. When a probability distribution heavily favors 
    one category, a new event belonging to that category conveys
    little information because that event had a high probability
    of occurring and was expected. The more heavily a distribution
    favors certain categories, the lower the information entropy
    that characterizes it. In contrast, Shannon entropy is 
    maximized when the probability of an event type is the same 
    across all event categories (uniform distribution).
    A uniform distribution has the most "randomness", so 
    the amount of information conveyed by each new event
    (i.e. the information entropy) is maximal for such a
    probability distribution.
    
    References:

    https://www.quora.com/What-is-an-intuitive-explanation-of-the-concept-of-entropy-in-information-theory
    http://stats.stackexchange.com/questions/66108/why-is-entropy-maximised-when-the-probability-distribution-is-uniform

    '''
    dist = buildDist()
    entropy = -sum([p * math.log(p) for p in dist.itervalues()])
    payload = {"entropy": entropy}
    return flask.jsonify(**payload)

@app.route("/rate")
def stream_rate():
    '''
    Returns the stream rate of retweets of Twitter statuses published
    by @nytimes, measured as the average time delta between consecutive
    messages during a sliding window of 120 seconds.
    '''
    keys = conn.keys("delta:*")
    deltas = [float(delta) for delta in conn.mget(keys)]
    avg_rate = float('inf')
    if len(deltas):
        avg_rate = sum(deltas)/len(deltas)
    payload = {"rate": avg_rate}
    return flask.jsonify(**payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
