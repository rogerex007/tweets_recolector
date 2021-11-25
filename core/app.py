import json
import boto3
import os
import tweepy
import csv


# import requests


def lambda_handler(event, context):

    consumerKey = 'SAnKuRMTOXRmhbcKlZgCVScjv'

    consumerSecret = 'kBHgmInxzKZN0gtT7ih68EwnaXA4F47vlrHJbwqO0dy6eepA2o'
    accessToken = '1453483019826868234-fUUxZzXUOLejxKDR0idPTbRV1bBulu'
    accessTokenSecret = 'JOlUWcMP8xAukOxhx4aTeSiQZ5mkgR4ElFvgW690zVtpz'
    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessTokenSecret) 
    api = tweepy.API(auth)

    keyword = "Biden"
    noOfTweet = 18000

    #tweets = tweepy.Cursor(api.search, q=keyword).items(noOfTweet)

    table_name = os.environ.get('TWEETS_TABLE_NAME')
    print(table_name)
    tweetsTable = boto3.resource('dynamodb')
    table = tweetsTable.Table(table_name)
    count = 0
    while count <= 3000:
        tweets = api.search_tweets(q=keyword, lang="en", count=noOfTweet)
        if count <= 3000:
            for tweet in tweets:
                params = {
                    'id': str(tweet.id),
                    'text': str(tweet.text),
                    'created_at': str(tweet.created_at),
                    'userLocation': str(tweet.user.location),
                    'userFollowersCount': tweet.user.followers_count,
                    'userFriendsCount': tweet.user.friends_count
                }
                response = table.put_item(
                    TableName=table_name,
                    Item=params
                )
                print(response)
        else:
            print("Scanning...")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": event,
            # "location": ip.text.replace("\n", "")
        }),
    }

def listAllTweets(event, context):
    table_name = os.environ.get('TWEETS_TABLE_NAME')
    print(table_name)
    tweetsTable = boto3.resource('dynamodb')
    table = tweetsTable.Table(table_name)
    response = table.scan()
    response = response['Items']
    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }


def exportTweetsToCSV(event, context):
    table_name = os.environ.get('TWEETS_TABLE_NAME')
    bucket_name = os.environ.get('FILES_BUCKET_NAME')
    print(table_name)
    tweetsTable = boto3.resource('dynamodb')
    table = tweetsTable.Table(table_name)
    response = table.scan(Limit=100000)
    data = response['Items']
    print('REGISTROS: ', len(data))
    temp_csv_file = csv.writer(open("/tmp/csv_file.csv", "w+"))
    temp_csv_file.writerow(["id", "text", "created_at", "userLocation", "userFollowersCount", "userFriendsCount"])
    for tweet in data:
        temp_csv_file.writerow([tweet['id'], tweet['text'], tweet['created_at'], tweet['userLocation'], tweet['userFollowersCount'], tweet['userFriendsCount']])
    s3 = boto3.client('s3')
    s3.upload_file('/tmp/csv_file.csv', bucket_name, 'tweets.csv')
    
    return {
        "statusCode": 200,
        "body": json.dumps(event),
    }
