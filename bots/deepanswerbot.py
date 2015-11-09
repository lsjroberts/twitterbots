#!/usr/bin/env python2
# -*- coding: utf-8 -*- #

import re
import random
import requests
from twitterbot import TwitterBot

class DeepAnswerBot(TwitterBot):
    unrecognised_tweet = "@gelatindesign I could not understand this question :("
    no_concepts_tweet = "@gelatindesign I couldn't find any related concepts :("

    def bot_init(self):
        """
        Initialize and configure your bot!

        Use this function to set options and initialize your own custom bot
        state (if any).
        """

        ############################
        # REQUIRED: LOGIN DETAILS! #
        ############################
        self.config['api_key'] = 'EVbRnjczP1OR3CVBmxDMQ2eDN'
        self.config['api_secret'] = 'XWx4FcIEOI3mpWoGWW9TYfx9njsJnXdGer8ztaDaVcdcA8nO7Z'
        self.config['access_key'] = '4136721273-LLOCwFedBAj8bhN9UoEydCEjGJr57bzvr9LSjF3'
        self.config['access_secret'] = 'aAUjjCEai9IEIgcT2HmL8VrjeLmaeiDMu2N1sDTXe5ckr'


        ######################################
        # SEMI-OPTIONAL: OTHER CONFIG STUFF! #
        ######################################

        # how often to tweet, in seconds
        self.config['tweet_interval'] = 4 * 60 * 60     # 4 hours

        # use this to define a (min, max) random range of how often to tweet
        # e.g., self.config['tweet_interval_range'] = (5*60, 10*60) # tweets every 5-10 minutes
        self.config['tweet_interval_range'] = None

        # only reply to tweets that specifically mention the bot
        self.config['reply_direct_mention_only'] = False

        # only include bot followers (and original tweeter) in @-replies
        self.config['reply_followers_only'] = True

        # fav any tweets that mention this bot?
        self.config['autofav_mentions'] = False

        # fav any tweets containing these keywords?
        self.config['autofav_keywords'] = []

        # follow back all followers?
        self.config['autofollow'] = False


        ###########################################
        # CUSTOM: your bot's own state variables! #
        ###########################################

        # If you'd like to save variables with the bot's state, use the
        # self.state dictionary. These will only be initialized if the bot is
        # not loading a previous saved state.

        # self.state['butt_counter'] = 0

        # You can also add custom functions that run at regular intervals
        # using self.register_custom_handler(function, interval).
        #
        # For instance, if your normal timeline tweet interval is every 30
        # minutes, but you'd also like to post something different every 24
        # hours, you would implement self.my_function and add the following
        # line here:

        # self.register_custom_handler(self.my_function, 60 * 60 * 24)


    def on_scheduled_tweet(self):
        """
        Make a public tweet to the bot's own timeline.

        It's up to you to ensure that it's less than 140 characters.

        Set tweet frequency in seconds with TWEET_INTERVAL in config.py.
        """
        # text = function_that_returns_a_string_goes_here()
        # self.post_tweet(text)

        pass
        # raise NotImplementedError("You need to implement this to tweet to timeline (or pass if you don't want to)!")


    def on_mention(self, tweet, prefix):
        """
        Defines actions to take when a mention is received.

        tweet - a tweepy.Status object. You can access the text with
        tweet.text

        prefix - the @-mentions for this reply. No need to include this in the
        reply string; it's provided so you can use it to make sure the value
        you return is within the 140 character limit with this.

        It's up to you to ensure that the prefix and tweet are less than 140
        characters.

        When calling post_tweet, you MUST include reply_to=tweet, or
        Twitter won't count it as a reply.
        """
        # text = function_that_returns_a_string_goes_here()
        # prefixed_text = prefix + ' ' + text
        # self.post_tweet(prefix + ' ' + text, reply_to=tweet)

        # call this to fav the tweet!
        # if something:
        #     self.favorite_tweet(tweet)

        pass
        # raise NotImplementedError("You need to implement this to reply to/fav mentions (or pass if you don't want to)!")


    def on_timeline(self, tweet, prefix):
        """
        Defines actions to take on a timeline tweet.

        tweet - a tweepy.Status object. You can access the text with
        tweet.text

        prefix - the @-mentions for this reply. No need to include this in the
        reply string; it's provided so you can use it to make sure the value
        you return is within the 140 character limit with this.

        It's up to you to ensure that the prefix and tweet are less than 140
        characters.

        When calling post_tweet, you MUST include reply_to=tweet, or
        Twitter won't count it as a reply.
        """
        # print "---"
        # print tweet.text
        # print tweet.created_at

        tweet_format = self.get_tweet_format(tweet)

        if tweet_format is not None:
            text = self.get_response(tweet, tweet_format) + ' ' + self._tweet_url(tweet)
        else:
            text = DeepAnswerBot.unrecognised_tweet + ' ' + self._tweet_url(tweet)

        self.post_tweet(text, reply_to=tweet)


    def get_tweet_format(self, tweet):
        """
        Gets the type of the tweet with the subjects and relations.

        See ../learnings/deepanswerbot/deepquestionbot.txt for examples.
        """
        tweet_formats = [
            ('IsA', re.compile(ur'Why do(?:es)?(?: an?)? (?P<start>[a-z\s]+) have to be(?: an?)? (?P<end>[a-z\s]+)\?', re.IGNORECASE)),
            ('IsA', re.compile(ur'Why must?(?: an?)? (?P<start>[a-z\s]+) be(?: an?)? (?P<end>[a-z\s]+)\?', re.IGNORECASE)),
            ('IsA', re.compile(ur'Why(?: are|is)? (?P<start>[a-z\s]+)(?: so often) considered to be(?: an?)? (?P<end>[a-z\s]+)\?', re.IGNORECASE)),

            ('AtLocation', re.compile(ur'Why do(?:es)?(?: an?)? (?P<end>[a-z\s]+) have(?: an?)? (?P<start>[a-z\s]+)\?', re.IGNORECASE)),
            ('AtLocation', re.compile(ur'Why (?:are|is)?(?: an?)? (?P<start>[a-z\s]+) (?:kept|found) (?:in|near)(?: an?)? (?P<end>[a-z\s]+)\?', re.IGNORECASE)),

            ('AtLocation.GuessAtLocation', re.compile(ur'(?P<start>[a-z\s]+) are (?:kept|found) (?:near|in) (?P<end>[a-z\s]+)(?:, right\?|.)? (?:So|But) where do (?:you|we) (?:keep|find) (?P<subject>[a-z\s]+)\?(?: An?)? (?P<guess>[a-z\s]+)\?', re.IGNORECASE)),

            ('AtLocation.SubjectAtLocation', re.compile(ur'(?P<start>[a-z\s]+) are (?:kept|found) (?:near|in) (?P<end>[a-z\s]+)(?:, right\?|.)? (?:So|But) where do (?:you|we) (?:keep|find) (?P<subject>[a-z\s]+)\?', re.IGNORECASE)),

            ('AtLocation.InsteadAtLocation', re.compile(ur'What if (?:you|we) (?:kept|found)(?: an?)? (?P<start>[a-z\s]+) in(?: an?)? (?P<subject>[a-z\s]+), instead of (?:in|near)(?: an?)? (?P<end>[a-z\s]+)\?', re.IGNORECASE)),

            ('RelatedTo.InsteadIsA', re.compile(ur'Have (?:you|we) ever considered(?: an?)? (?P<start>[a-z\s]+) that is(?: an?)? (?P<guess>[a-z\s]+) instead of(?: an?)? (?P<end>[a-z\s]+)\?', re.IGNORECASE)),

            ('Compared', re.compile(ur'Why (?:are|is) (?P<start>[a-z\s]+)(?:so) (?P<startAttribute>[a-z\s]+), and (?P<end>[a-z\s]+)(?:comparitively) (?P<endAttribute>[a-z\s]+)\?', re.IGNORECASE)),

            ('StillA', re.compile(ur'If(?: an?)? (?P<start>[a-z\s]+) is(?: not)? (?P<startAttribute>[a-z\s]+), is it still(?: an?)? [a-z\s]+\?', re.IGNORECASE)),
        ]

        for tweet_format in tweet_formats:
            name, pattern = tweet_format
            matches = pattern.search(tweet.text)
            if matches:
                return (name, matches)

        return None

    def get_response(self, tweet, tweet_format):
        """
        Gets the response to a tweet given a format and subjects
        """
        relation, matches = tweet_format
        templates = []

        if relation == 'IsA':
            templates = [
                "Perhaps without [end.RelatedTo] we wouldn't have a [start]",
                "If [end.IsA] is [end] then surely the [start] can only be [end] too",
                "When [start.RelatedTo] becomes [end.RelatedTo] there is no other reality",
                "The greatest [start] of the greatest number is the foundation of [end]",
                # "[start] consists in doing [end]",
                "If [end] did not exist it would be necessary to invent [start]",
                # "[end] is the mother of [start]",
                # "[end] is the measure of all [start]",
                "It is wrong always, everywhere and for everyone, to believe anything upon insufficient [start]",
                "There is but one truly serious [end] problem, and that is [start]",
                "I once had a [start], it was a nice [start]. But that's not relevant now."
            ]
        elif relation == 'AtLocation':
            templates = [
                "Where else would [start] be?",
                "[end] are near [end.AtLocation], so [start] must be there too",
                "Because [start] is [start.IsA.end] and [end] is [end.IsA.end]"
            ]
        elif relation == 'AtLocation.SubjectAtLocation':
            templates = [
                "I'd usually look for [subject] near [subject.AtLocation]",
                "It depends, if [subject] is [subject.IsA] then it would be near [start.AtLocation]",
                "One cannot step twice in the same [end], so [subject] must be near [subject.AtLocation]"
            ]
        elif relation == 'AtLocation.GuessAtLocation':
            templates = [
                "Nope, [guess] is [guess.IsA] so it seems unlikely",
                "Only when [start] has a [start.HasA]",
                "Well, [guess] is a nice place to be, so long as [start] can be [start.UsedFor]",
                "[start] lies in [end], and perfect [subject] lies in the best [guess]"
            ]
        elif relation == 'AtLocation.InsteadAtLocation':
            templates = [
                "Woah... and what if a [start] can [start.CapableOf]?",
                "I doubt it would make much difference to a [start] considering it's not a [end.IsA]"
            ]
        elif relation == 'RelatedTo.InsteadIsA':
            templates = [
                "The [guess] [start] is that which overcomes not only it's [end] but also it's [start.HasA]",
                "When [guess] can [guess.CapableOf] I would suggest it must also be [end]"
            ]
        elif relation == 'Compared':
            templates = [
                "Occasionally a [endAttribute] [end] can also be a [startAttribute] [start]"
            ]
        elif relation == 'StillA':
            templates = [
                "Perhaps if a [start] is also a [start.IsA] then it could be",
                "Sometimes a [start] can be [startAttribute], but that is rare"
            ]

        if templates:
            random.shuffle(templates)
            for template in templates:
                composed = self.compose_tweet_with_concepts(template, matches)
                if composed:
                    return composed
            return DeepAnswerBot.no_concepts_tweet + ' ' + self._tweet_url(tweet)

        return DeepAnswerBot.unrecognised_tweet + ' ' + self._tweet_url(tweet)

    def compose_tweet_with_concepts(self, template, subjects):
        """
        Compose a tweet template with data from ConceptNet and subjects
        """
        composed = template
        pattern = re.compile(u'(?:[^\[\]]*\[([^\]]+)\])', re.IGNORECASE)
        items = pattern.findall(template)

        for item in items:
            subjectGroup, relation, rest = just(3, item.split('.'))
            subject = subjects.group(subjectGroup)
            if subject is not None:
                concept = subject
                if relation:
                    concept = self.get_concept(subject, relation)
                    if concept is None:
                        return None
                composed = composed.replace('[' + item + ']', concept)

        return composed

    def get_concept(self, subject, relation):
        baseUrl = 'http://conceptnet5.media.mit.edu/data/5.4/c/en/'
        r = requests.get(baseUrl + subject)
        json = r.json()
        choices = []

        for edge in json['edges']:
            if edge['rel'] == '/r/' + relation:
                concept = edge['start']
                if edge['start'] == '/c/en/' + subject:
                    concept = edge['end']
                if concept[:6] == '/c/en/':
                    formattedConcept, rest = just(2, concept[6:].split('/'))
                    formattedConcept = formattedConcept.replace('_', ' ')
                    choices.append(formattedConcept)

        if len(choices) > 0:
            return random.choice(choices)

        return None


def just(n, seq):
    """
    http://stackoverflow.com/a/10300081
    """
    it = iter(seq)
    for _ in range(n - 1):
        yield next(it, None)
    yield tuple(it)


if __name__ == '__main__':
    bot = DeepAnswerBot()
    bot.run()
