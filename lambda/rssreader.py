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


def entry_is_new(entry):
    if TABLE.has_item(itemId=entry.link):
        return False
    return True


def entry_is_wanted(entry):
    NOT_WANTED = [
            'Hobbies and Interests',
            'Makeup',
            'Home and Garden',
            'Food and Drink',
            'Recipes',
            ]
    for tag in entry.tags:
        if tag.term in NOT_WANTED:
            return False
    return True


def handle_feed(url):
    feed = feedparser.parse(url)
    ses = boto.ses.connect_to_region(
            'eu-west-1',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
            security_token=os.environ.get('AWS_SESSION_TOKEN',None))
    result = dict(sent=[], skipped=[], old=[])
    for entry in feed.entries:
        if entry_is_wanted(entry):
            if entry_is_new(entry):
                ses.send_email(SENDER_EMAIL,
                        'new item for my kindle',
                        entry.link,
                        [RECIPIENT_EMAIL])
                TABLE.put_item(data={'itemId': entry.link})
                result['sent'].append(entry.title)
            else:
                result['old'].append(entry.title)
        else:
            result['skipped'].append({'title': entry.title, 'tags': entry.tags})
    return result


def lambda_handler(event, context):
    return handle_feed('https://kit.se/feed')


if __name__ == '__main__':
    import sys
    print handle_feed(sys.argv[1])
