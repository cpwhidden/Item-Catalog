#
# Database access functions for the web forum.
# 

import time
import psycopg2

## Database connection
DB = []

## Get posts from database.
def GetAllPosts():
    '''Get all the posts from the database, sorted with the newest first.

    Returns:
      A list of dictionaries, where each dictionary has a 'content' key
      pointing to the post content, and 'time' key pointing to the time
      it was posted.
    '''
    db = psycopg2.connect("dbname=forum")
    cursor = db.cursor()
    cursor.execute("select content, time, id from posts order by time desc")
    posts = cursor.fetchall()
    db.close()
    posts = [{'content': str(row[1]), 'time': str(row[0])} for row in posts]
    # posts.sort(key=lambda row: row['time'], reverse=True)
    return posts

## Add a post to the database.
def AddPost(content):
    '''Add a new post to the database.

    Args:
      content: The text content of the new post.
    '''
    db = psycopg2.connect("dbname=forum")
    cursor = db.cursor()
    t = time.strftime('%c', time.localtime())
    cursor.execute("insert into posts (content) values (%s)", (content,))
    db.commit()
    db.close()
