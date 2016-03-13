What is the distribution of recently published statuses on the New York Times Twitter timeline (@nytimes), that are retweeted by the public?
===================================================================================================

Stream and Distribution
------------------------
Of the statuses published recently on the New York Times Twitter timeline, which ones are retweeted the most? Do each of these published Twitter statuses have roughly equal probability of being retweeted?

To answer these questions and others, I build a categorical distribution of statuses published on the New York Times Twitter timeline in the past 2-6 hours. The stream consumed by this system is the stream of retweets of Twitter statuses published by the New York Times. In the categorical distribution, the event categories are each of the published statuses with the probability of an event category being the probability that an incoming event corresponds to a retweet of that published status. For example, suppose @nytimes published the following Twitter statuses in the past 2-6 hours:
- "Donald Trump foo"
- "ISIS bar"
- "Superbowl baz"
- "awards show foobar"

Suppose at the moment a user requests the categorical distribution from our system, each of these four statuses have been retweeted the same number of times. In this case, this system returns a categorical distribution with four categories ("Donald Trump foo"; "ISIS bar"; "Superbowl baz"; "awards show foobar"), each with a probability density of 0.25.

Let us consider a different case where the New York Times has published the same four statuses as above, but almost all retweet events were retweets of "awards show foobar". In this scenario, the categorical distribution returned has the same four categories, but category "awards show foobar" has a probability density of nearly 1.0 and the other three categories each have a probability density close to 0.

Entropy Alerts
---------------
The Shannon entropy of a probability distribution can be thought of as the amount of information each new message conveys. When a probability distribution heavily favors one category, a new event belonging to that category conveys little information because that event had a high probability of occurring and was expected. The more heavily a distribution favors certain categories, the lower the information entropy that characterizes it. In contrast, Shannon entropy is maximized when the probability of an event type is the same across all event categories (uniform distribution). A uniform distribution has the most "randomness", so the amount of information conveyed by each new event (i.e. the information entropy) is maximal for such a probability distribution.<sup>1</sup> <sup>2</sup>

I want to know when Twitter users are retweeting one or more New York Times statuses far more than other statuses published by @nytimes. If a particular New York Times status becomes very popular or controversial, the probability that a retweet of a @nytimes status is a retweet of this status, is high. When a large percentage of retweets in the stream are retweets of one or a few categories, the categorical distribution favors those categories and is characterized by lower information entropy. I am interested in finding out when the entropy of the categorical distribution drops much lower than its statistical mean because that implies unusually high interactions with a few @nytimes statuses. Thus, every 30 minutes, the system requests the entropy of the current distribution, stores that entropy measurement externally, and queries the external data store for all historical entropy measurements to determine whether the current entropy is less than 1.5 standard deviations below the mean. If it is, a Twitter bot (**@EntropyPatrol** <sup>3</sup>) alerts me by updating its timeline with a status telling me which @nytimes status is receiving the most interaction at that given moment.

Implementation
--------------
* `compute_distrib_and_rate.sh`: Stores the text of each published @nytimes status and the number of times it's retweeted, and computes the rate (time between messages) of the stream of retweets of @nytimes Twitter statuses. This pipeline includes the components: `event.py`, `diff.py`, `insert.py`
* `event.py`: Consumes the Twitter Streaming API and externally stores the text of new statuses published by the New York Times. On each retweet of a @nytimes status, updates the count of retweets of that status and prints the timestamp of the retweet event to stdout
* `diff.py`: Computes the time difference between consecutive retweet events
* `insert.py`: Stores time deltas externally, expiring each record after 120 seconds to implement a sliding window
* `api.py`: Endpoints /distribution, /entropy, /rate can be requested for the current categorical distributon of retweeted @nytimes statuses, the information entropy of the current distribution, and the stream rate of @nytimes status retweets, respectively.
* `alert_entropy_change.py`: Requests the entropy of the current distribution every 30 minutes and publishes a status on @EntropyPatrol's Twitter account if the entropy is less than 1.5 standard deviations below the mean
* `index.html`: HTML document that displays the categories and probability densities of the current distribution
* `getDistrib.js`: Requests the API's /distribution endpoint and sorts the response in order to display the categories in order of decreasing probability density
* `http.min.js`: A Javascript library for making HTTP requests

<sup>1</sup> https://www.quora.com/What-is-an-intuitive-explanation-of-the-concept-of-entropy-in-information-theory

<sup>2</sup> http://stats.stackexchange.com/questions/66108/why-is-entropy-maximised-when-the-probability-distribution-is-uniform

<sup>3</sup> https://twitter.com/EntropyPatrol
