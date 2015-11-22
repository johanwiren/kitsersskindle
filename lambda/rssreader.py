#!/usr/bin/env python

import feedparser
import boto.dynamodb2
import boto.dynamodb2.table
import boto.ses
import os


SENDER_EMAIL = 'johan@johanwiren.se'
RECIPIENT_EMAIL = 'johan.wiren.se_65@pushtokindle.com'

TABLE = boto.dynamodb2.table.Table('rssfeedkindle-dynamoDbTable-IWHWI0I2NY0K',
        connection=boto.dynamodb2.connect_to_region(
            'eu-west-1',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
            security_token=os.environ.get('AWS_SESSION_TOKEN',None)))

def filter_item(feed_item):
    NOT_WANTED = [
            'Hobbies and Interests',
            'Makeup',
            'Home and Garden',
            'Food and Drink',
            'Recipes',
            ]
    for tag in feed_item['tags']:
        if tag in NOT_WANTED:
            return False
    return True


def get_feed_links(url):
    feed = feedparser.parse(url)
    return [x.link for x in feed.entries if filter_item(x)]


def get_new_links(links):
    return [new_link for new_link in [
        link for link in links if not TABLE.has_item(itemId=link)]]

def handle_feed(url):
    ses = boto.ses.connect_to_region(
            'eu-west-1',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
            security_token=os.environ.get('AWS_SESSION_TOKEN',None))
    links = get_feed_links(url)
    new_links = get_new_links(links)
    result = []
    for link in new_links:
        ses.send_email(SENDER_EMAIL,
                'new item for my kindle',
                link,
                [RECIPIENT_EMAIL])
        TABLE.put_item(data={'itemId': link})
        result.append(link)
    return result


def lambda_handler(event, context):
    return handle_feed('https://kit.se/feed')


if __name__ == '__main__':
    import sys
    print handle_feed(sys.argv[1])
