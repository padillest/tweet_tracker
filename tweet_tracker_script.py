# Import packages
import tweepy 
import mysql.connector 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Global variables 
PASSWORD = "password"

API_KEY = "api_key"
API_KEY_SECRET = "api_key_secret"

BEARER_TOKEN = "bearer_token"

ACCESS_TOKEN = "access_token"
ACCESS_TOKEN_SECRET = "access_token_secret"

TOP_USER_LIST = []

# Search queries 
PROJ_AUTH = {
    '"sean kidd"', '"janice victor"', '"yale belanger"',
    '"cynthia puddu"', '"abe oudshoorn"', '"john graham"',
    '"tyler frederick"', '"maritt kirst"', '"alex wilson"',
    '"naomi nichols"', '"jacqueline kennelly"', '"carol kauppi"',
    '"joanna henderson"', '"sue-ann macdonald"', '"katrina milaney"',
    '"eric weissman"', '"cheryl forchuk"', '"jino distasio"',
    '"amanda noble"', '"alex abramovich"', '"rachel laforest"', 
    '"erin dej"', '"ron kneebone"', '"geoffrey messier"', 
    '"martin goyette"', '"michael ungar"'
}
TERM = '"homelessness"'
LANG = 'lang: en'

# Establish connection with mySQL server 
cnx = mysql.connector.connect(host = 'localhost', 
    user = 'root',
    password = PASSWORD,
    database = 'tweet_db')

# Create database cursor
mycursor = cnx.cursor()

# Create initial database
# mycursor.execute("CREATE DATABASE tweet_db")
# mycursor.execute("CREATE TABLE tweets (id INT AUTO_INCREMENT PRIMARY KEY, tweet_id VARCHAR(100), user VARCHAR(255), retweets INT, likes INT, text VARCHAR(300))")

# Connect to Twitter API
client = tweepy.Client(BEARER_TOKEN)

# Apply search queries through Twitter API
for author in PROJ_AUTH: 

    # Format the queries
    qry = '{} {} {}'.format(author, TERM, LANG)

    # Customize Tweet payload
    out = client.search_recent_tweets(query = qry, tweet_fields = ['public_metrics', 'created_at'], expansions = 'author_id')

    # Check for empty search
    if (out.meta['result_count'] == 0):
        continue

    # Store Tweet payload
    for tweet_data in out.data:

        # Collect user information
        user = tweet_data.author_id

        # Collect tweet ID
        tweet_id = tweet_data.id

        # Collect tweet text 
        tweet_text = tweet_data.text

        # Collect retweet count 
        retweet_count = tweet_data.public_metrics['retweet_count']

        # Collect like count 
        like_count = tweet_data.public_metrics['like_count']

        # Store the query search
        input_qry = qry

        # Pass Tweet payload into mySQL database
        sql = 'INSERT INTO tweets (tweet_id, user, retweets, likes, text) VALUES (%s, %s, %s, %s, %s)'
        val = (tweet_id, user, retweet_count, like_count, tweet_text)

        # Execute the storage
        mycursor.execute(sql, val)
        cnx.commit()


# Visualizing the users with the highest number of interactions with MtS Inc.

## Gauge most engaged accounts
mycursor.execute('SELECT user, COUNT(user) AS count FROM tweets GROUP BY user ORDER BY count DESC LIMIT 4')
user_out = mycursor.fetchall()

## Store data in pandas dataframe
data = pd.DataFrame(data = user_out, columns = ['user_id', 'count'])

## Convert user ID to Twitter account handle
for id in data.user_id: 
    user_out = client.get_user(id = id)
    TOP_USER_LIST.append(user_out.data['username']) 

## Create new column 
data['username'] = TOP_USER_LIST

## Visualize most engaged accounts
sns.barplot(x = 'count',
    y = 'username',
    data = data)
    
plt.show()