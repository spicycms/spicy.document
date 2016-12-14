# coding=utf-8
import itertools
import json
import random
import urllib2
import re

from collections import defaultdict
from datetime import datetime, timedelta
from operator import itemgetter

from django.core.cache import cache
from django.db.models import get_model

from . import defaults

class DateFuckUpMix(object):
    @staticmethod
    def date_fuckup(doc): 
        # XXX wtf? why __str__ instead datettime
        # cached_property ? or some property cache effect?
        try:
            return doc.pub_date.date()
        except TypeError:
            return doc.pub_date.date


class PubsPerDayList(DateFuckUpMix):
    def __init__(self, docs):
        self._all_pubs = []

        pub_date = None
        pubs_per_day = PubsPerDay()

        if docs:
            for doc in docs:
                doc_date = self.date_fuckup(doc)

                if pub_date is None:
                    pub_date = doc_date
                    pubs_per_day.append(doc)

                elif pub_date != doc_date:
                    self.pubs_per_day_completed(pubs_per_day)

                    pub_date = doc_date
                    pubs_per_day = PubsPerDay()
                    pubs_per_day.append(doc)
                else:
                    pubs_per_day.append(doc)
            self.pubs_per_day_completed(pubs_per_day)

    def pubs_per_day_completed(self, pubs_per_day):
        """
        This should be called when we're done adding publications for a day.
        """
        self._all_pubs.append(pubs_per_day)
        #pubs_per_day.limit_stories()

    def __len__(self):
        return len(self._all_pubs)

    def __iter__(self):
        return iter(self._all_pubs)


class PubsPerDay(DateFuckUpMix):
    def __init__(self):
        self.date = None
        self.all_docs = list()
        self.top_docs = list() # imp, important =) 
        self.docs = list()
        self.docs_with_preview = list()
        self.docs_iterator = itertools.chain(self.docs_with_preview, self.docs)
        self.stories = list()
        self.frequencies = defaultdict(int)
        self.partner_index = random.randint(defaults.PARTNERS_IN_FEED_FROM, defaults.PARTNERS_IN_FEED_TO)
        self.selected_partner = random.randint(1, 3)

    def append(self, doc):
        if self.date is None:
            self.date = self.date_fuckup(doc)
        if self.date != self.date_fuckup(doc):
            raise ValueError

        self.all_docs.append(doc)

        if doc.priority == 'exclusive':
            self.top_docs.append(doc)
        else:
            if doc.genre is not None and doc.genre.slug == 'news':
                self.docs.append(doc)
            else:
                self.docs_with_preview.append(doc)

        for tag in doc.tags[:3]:
            if tag.tag_id not in self.frequencies:
                self.stories.append(tag)
            self.frequencies[tag.tag_id] += 1

    def limit_stories(self, limit=defaults.STORIES_PER_DAY):
        """
        Limit number of stories.
        """
        freqs = sorted(
            self.frequencies.items(), key=itemgetter(1), reverse=True)
        stories = []
        for story_pk, _freq in freqs[:limit]:
            for story in self.stories:
                if story.tag_id == story_pk:
                    stories.append(story)
                    break
        self.stories = stories


URL_RE = re.compile(
    r'https?://'
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?])[^ \n\r\t"\'<>]*', re.IGNORECASE)


class Twitter(object):
    def make_links(self, text):
        all_links_in_text = URL_RE.findall(text)
        for link in all_links_in_text:
            html_link = '<a target="_blank" href="%s">%s</a>' % (link, link)
            text = text.replace(link, html_link)
        return text

    def get_json_from_web(self):
        remote_url = 'http://api.twitter.com/1/statuses/user_timeline.json?count=8&include_rts=1&screen_name=' + defaults.TWITTER_ACCOUNT
        connection = urllib2.urlopen(remote_url, timeout=defaults.TWITTER_TIMEOUT)
        if connection.getcode() == 200:
            return connection.read()
        #print '@@@@ERROR'

    def cache_tweets(self, json_data):
        cache.set('twitter_timeline_cache', json_data, defaults.TWITTER_CACHE_PERIOD)

    def get_tweets(self):
        cached_data = cache.get('twitter_timeline_cache')
        if cached_data:
            json_data = cached_data
        else:
            try:
                json_data = self.get_json_from_web()
            except:
                json_data = '[]'
            self.cache_tweets(json_data)

        tweets = json.loads(json_data, 'utf-8')        
        for tweet in tweets:
            tweet['date'] = datetime.strptime(tweet['created_at'][0:18], '%a %b %d %H:%M:%S') + timedelta(hours=defaults.TWITTER_TIME_DELTA)
            tweet['text'] = self.make_links(tweet['text'])
        return tweets


"""
def random_place_blocks(blocks, positions=4):
	from siteskin.models import ContentBlock

    blocks_to_pick = []
    result_blocks = []
    position_priorities = {}
    block_cnt = 0
    for block in blocks:
        try:
            content_block = ContentBlock.objects.get(slug=block)
            priority = content_block.content_provider.priority
            pos_priority = content_block.content_provider.position_priority
            block_cnt += 1
        except:
            continue
        for i in range(priority):
            blocks_to_pick.append(block)
            position_priorities[block] = pos_priority
    if block_cnt < positions:
        return []
    for position in range(positions):
        random_position = random.randrange(0, len(blocks_to_pick))
        selected_block = blocks_to_pick[random_position]
        result_blocks.append(selected_block)
        # removing all selected block instances from array to pick
        blocks_to_pick = [block for block in blocks_to_pick if block != selected_block]
    result_blocks = sorted(result_blocks, key=lambda result_block: position_priorities[result_block])
    result_blocks.reverse()
    return result_blocks
"""


def get_concrete_document():
    return get_model(*defaults.CUSTOM_DOCUMENT_MODEL.split('.'))
