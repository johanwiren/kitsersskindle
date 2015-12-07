#!/usr/bin/env python

import awsresources
import feedparser
import boto.dynamodb2
import boto.dynamodb2.table
import boto.ses
import os

class KitseRssHandler(object):
    SENDER_EMAIL = 'johan@johanwiren.se'
    PUSH_TO_KINDLE_EMAIL = 'johan.wiren.se_65@pushtokindle.com'
    NOT_WANTED = [
            'Beauty',
            'DIY',
            'Food and Drink',
            'Health and Fitness',
            'Hobbies and Interests',
            'Home and Garden',
            'Makeup',
            'Real Estate',
            'Recipes',
            ]

    def __init__(self, feed):

        self.feed = feed
        self.table = boto.dynamodb2.table.Table(awsresources.dynamodb_table,
                     connection=boto.dynamodb2.connect_to_region(
                         'eu-west-1',
                          aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                          aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                          security_token=os.environ.get('AWS_SESSION_TOKEN',None)))

        self.ses = boto.ses.connect_to_region(
                       'eu-west-1',
                       aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                       aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                       security_token=os.environ.get('AWS_SESSION_TOKEN',None))


    def _entry_is_new(self, entry):
        if self.table.has_item(itemId=entry.link):
            return False
        return True


    def _entry_is_wanted(self, entry):
        for tag in entry.tags:
            if tag.term in self.NOT_WANTED:
                return False
        return True


    def _push_to_kindle(self, entry):
        self.ses.send_email(self.SENDER_EMAIL,
                'new item for my kindle',
                entry.link,
                [self.PUSH_TO_KINDLE_EMAIL])

    def _result_body(self, result):
        lines = []
        for item in result['sent']:
            lines.append(item['title'].encode('iso-8859-1', 'ignore'))
            lines.append(" ".join([" %s" % x['term'].encode('iso-8859-1', 'ignore') for x in item['tags']]))
        text = "\n".join(lines)
        return text

    def _send_status_email(self, result):
        body = self._result_body(result)
        if body:
            self.ses.send_email(self.SENDER_EMAIL,
                    'Kit.se RSS - Delivery status',
                    body,
                    [self.SENDER_EMAIL])

    def handle_feed(self):
        feed = self.feed
        result = dict(sent=[], skipped=[], old=[])
        for entry in feed.entries:
            if self._entry_is_wanted(entry):
                if self._entry_is_new(entry):
                    self._push_to_kindle(entry)
                    self.table.put_item(data={'itemId': entry.link})
                    result['sent'].append(entry)
                else:
                    result['old'].append(entry)
            else:
                result['skipped'].append(entry)
        self._send_status_email(result)
        return result


def lambda_handler(event, context):
    feed = feedparser.parse('https://kit.se/feed')
    handler = KitseRssHandler(feed)
    return handler.handle_feed()


if __name__ == '__main__':
    import sys
    import json
    feed = feedparser.parse(sys.argv[1])
    handler = KitseRssHandler(feed)
    print handler._result_body(handler.handle_feed())
