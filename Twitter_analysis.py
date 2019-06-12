import re 
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
import sqlalchemy as sa
from sqlalchemy import create_engine
import pandas as pd 
import sqlite3 


class TwitterAnalysis(object): 
	''' 
	Twitter Analysis class  for opinion analysis. 
	
	'''
	def __init__(self): 
		''' 
		Class constructor . 
		'''
		# keys and tokens from twitter developer app  
		ConsumerKey = 'EPYwoHApbXCpHqQyNwMVsupwD'
		ConsumerSecret = 'iuiicOIdEFmOabVzmNnmWivIsiOCZcTwuQ4ZBiFPd6r5xOYFXY'
		AccessToken = '91970791-6vjG36wfvdxFakqp2grBcdlomfwVqAbppmTXzsJvE'
		AccessTokenSecret = 'RuB4riUCNYXJAGTAXDIXW6DWcMjDUS0a1WTEtoRnydzYO'

		#  authentication twitter using API keys 
		try: 
			
			self.authenticate = OAuthHandler(ConsumerKey, ConsumerSecret) 
			
			self.authenticate.set_access_token(AccessToken, AccessTokenSecret) 
			
			self.api_object = tweepy.API(self.authenticate) 
		except Exception as e: 
			print("Error: Authentication Failed",e) 


	def ParseTweet(self, tweet): 
		''' 
		function that make tweets cleaner by removing links, special characters 
		using simple regex statements. 
		'''
		return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w+:\/\/\S+)", " ", tweet).split()) 

	def GeTweetOpinionTextblob(self, tweet): 
		''' 
		classifies opinions of passed tweet 
		using textblob's sentiment method 
		'''
		tweet_analysis = TextBlob(self.ParseTweet(tweet)) 
		# set sentiment 
		if tweet_analysis.sentiment.polarity > 0: 
			return 'pos'
		elif tweet_analysis.sentiment.polarity == 0: 
			return 'neut'
		else: 
			return 'neg'
	def GeTweetOpinionVader(self,tweet): 
		analyser = SentimentIntensityAnalyzer() 
		# polarity_scores method of SentimentIntensityAnalyzer 
		analyser_data = analyser.polarity_scores(tweet) 
		  
		# print("Overall sentiment dictionary is : ", analyser_data) 
		# print("sentence was rated as ", analyser_data['neg']*100, "% Negative") 
		# print("sentence was rated as ", analyser_data['neu']*100, "% Neutral") 
		# print("sentence was rated as ", analyser_data['pos']*100, "% Positive") 

		# print("Sentence Overall Rated As", end = " ") 

		# decide sentiment as positive, negative and neutral 
		if analyser_data['compound'] >= 0.05 : 
		    return "pos" 

		elif analyser_data['compound'] <= - 0.05 : 
		    return "neg" 
		else : 
		    return "neut" 


	def GeTweets(self, query, count = 10): 
		''' 
		Main function to fetch tweets and parse them. 
		'''
		# empty list to store parsed tweets 
		list_tweets = [] 

		try: 
			# call twitter api to fetch tweets 
			tweets_api = self.api_object.search(q = query, count = count)
			# print(fetched_tweets) 

			# parsing tweets one by one 
			for tweet in tweets_api: 
				# empty dictionary to store required params of a tweet 
				tweet_parsed = {} 

				tweet_parsed['text'] = tweet.text 
				#  textblob sentiment result
				tweet_parsed['sentiment_textblob'] = self.GeTweetOpinionTextblob(tweet.text) 
				#  Vader sentimental Results 
				tweet_parsed['sentiment_vader'] = self.GeTweetOpinionVader(tweet.text) 
				if tweet.retweet_count > 0: 
					# if retweets 
					if tweet_parsed not in list_tweets: 
						list_tweets.append(tweet_parsed) 
				else: 
					list_tweets.append(tweet_parsed) 

			return list_tweets

		except tweepy.TweepError as e: 
			# print error (if any) 
			print("Error : " + str(e)) 
def AnalysisResults():
	# class object 
	api = TwitterAnalysis() 
	# fetch tweets for the given query 
	tweets = api.GeTweets(query = 'Donald Trump', count = 200) 

	# Textblob analysis 

	Positive_textblob_tweets = [tweet for tweet in tweets if tweet['sentiment_textblob'] == 'pos'] 
	Negative_textblob_tweets = [tweet for tweet in tweets if tweet['sentiment_textblob'] == 'neg']
	length_tweets=len(tweets)
	length_positive=len(Positive_textblob_tweets)
	length_negative=len(Negative_textblob_tweets)
	print("TEXTBLOB STATS \n")
	print("Positive Textblob tweets percentage: {} \n".format(100*length_positive/length_tweets)) 
	print("Negative Textblob tweets percentage: {} \n".format(100*length_negative/length_tweets)) 
	print("Neutral  Textblob tweets percentage: {} \n".format(100*(length_tweets- length_negative - length_positive)/length_tweets)) 


	#  vader analysis 
	print("VADER STATS \n")

	Positive_vader_tweets = [tweet for tweet in tweets if tweet['sentiment_vader'] == 'pos'] 
	Negative_vader_tweets = [tweet for tweet in tweets if tweet['sentiment_vader'] == 'neg']
	length_tweets=len(tweets)
	length_positive=len(Positive_vader_tweets)
	length_negative=len(Negative_vader_tweets)
	print("Positive Vader  tweets percentage: {} \n".format(100*length_positive/length_tweets)) 
	print("Negative Vader  tweets percentage: {} \n".format(100*length_negative/length_tweets)) 
	print("Neutral Vader tweets percentage: {} \n".format(100*(length_tweets- length_negative - length_positive)/length_tweets)) 

	return tweets 




def Tweets_to_database(tweets):
	#  writing tweets to database 
	# print(tweets)
	df=pd.DataFrame(tweets)
	try:
		conn = sqlite3.connect('Twitter.sqlite')
		Db=df.to_sql(name='table', con=conn)
	except Exception as e:
		print("table Already present")

	




if __name__ == "__main__": 
	# calling main function 
	tweets=AnalysisResults()
	Tweets_to_database(tweets)