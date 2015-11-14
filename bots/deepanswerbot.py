#!/usr/bin/env python2
# -*- coding: utf-8 -*- #

import re
import random
import requests
import inflect
from twitterbot import TwitterBot

inflector = inflect.engine()

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
        self.config['api_key'] = ''
        self.config['api_secret'] = ''
        self.config['access_key'] = ''
        self.config['access_secret'] = ''


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
        print "---"
        print tweet.text

        tweet_format = self.get_tweet_format(tweet)

        if tweet_format is not None:
            text = self.get_response(tweet, tweet_format) + ' ' + self._tweet_url(tweet)
        else:
            text = DeepAnswerBot.unrecognised_tweet + ' ' + self._tweet_url(tweet)

        print text
        self.post_tweet(text, reply_to=tweet)


    def get_tweet_format(self, tweet):
        """
        Gets the type of the tweet with the subjects and relations.

        See ../learnings/deepanswerbot/deepquestionbot.txt for examples.
        """
        tweet_formats = [
            ('IsA', re.compile(ur'Why do(?:es)?(?: an?)? (?P<start>[a-z\s]+) have to be(?: an?)? (?P<end>[a-z\s]+)\?', re.IGNORECASE)),
            ('IsA', re.compile(ur'Why must(?: an?)? (?P<start>[a-z\s]+) be(?: an?)? (?P<end>[a-z\s]+)\?', re.IGNORECASE)),
            ('IsA', re.compile(ur'Why(?: are|is)?(?: an?)? (?P<start>[a-z\s]+)(?: so often) considered to be(?: an?)? (?P<end>[a-z\s]+)\?', re.IGNORECASE)),

            ('AtLocation', re.compile(ur'Why do(?:es)?(?: an?)? (?P<end>[a-z\s]+) have(?: an?)? (?P<start>[a-z\s]+)\?', re.IGNORECASE)),
            ('AtLocation', re.compile(ur'Why (?:are|is)?(?: an?)? (?P<start>[a-z\s]+) (?:kept|found) (?:in|near)(?: an?)? (?P<end>[a-z\s]+)\?', re.IGNORECASE)),

            ('AtLocation.GuessAtLocation', re.compile(ur'(?P<start>[a-z\s]+) are (?:kept|found) (?:near|in)(?: an?)? (?P<end>[a-z\s]+)(?:, right\?|.)? (?:So|But) where do (?:you|we) (?:keep|find)(?: an?)? (?P<subject>[a-z\s]+)\?(?: an?)?(?: an?)? (?P<guess>[a-z\s]+)\?', re.IGNORECASE)),

            ('AtLocation.SubjectAtLocation', re.compile(ur'(?P<start>[a-z\s]+) are (?:kept|found) (?:near|in)(?: an?)? (?P<end>[a-z\s]+)(?:, right\?|.)? (?:So|But) where do (?:you|we) (?:keep|find)(?: an?)? (?P<subject>[a-z\s]+)\?', re.IGNORECASE)),

            ('AtLocation.InsteadAtLocation', re.compile(ur'What if you (?:kept|found)(?: an?)? (?P<start>[a-z\s]+) (?:near|in)(?: an?)? (?P<startLocation>[a-z\s]+), instead of (?:near|in)(?: an?)? (?P<end>[a-z\s]+)\?', re.IGNORECASE)),

            ('RelatedTo.InsteadIsA', re.compile(ur'Have (?:you|we) ever considered(?: an?)? (?P<start>[a-z\s]+) that is(?: an?)? (?P<guess>[a-z\s]+) instead of(?: an?)? (?P<end>[a-z\s]+)\?', re.IGNORECASE)),

            ('Compared', re.compile(ur'Why (?:are|is)(?: an?)? (?P<start>[a-z\s]+)(?:so) (?P<startAttribute>[a-z\s]+), and(?: an?)? (?P<end>[a-z\s]+)(?:comparitively) (?P<endAttribute>[a-z\s]+)\?', re.IGNORECASE)),

            ('StillA', re.compile(ur'If(?: an?)? (?P<start>[a-z\s]+) is(?: not)?(?: an?)? (?P<startAttribute>[a-z\s]+), is it still [a-z\s]+\?', re.IGNORECASE)),
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
                "Perhaps without [singular_noun:a:end.RelatedTo] we wouldn't have [singular_noun:a:start]",
                "If [a:end.IsA] is [a:end] then surely the [start] can only be [a:end] too",
                "When [singular_noun:a:start.RelatedTo] becomes [singular_noun:a:end.RelatedTo] there is no other reality",
                "The greatest [plural:start] of the greatest number is the foundation of [plural:end]",
                "[singular_noun:start] consists in doing [plural:end]",
                "If [plural:end] did not exist it would be necessary to invent [plural:start]",
                "It is wrong always, everywhere and for everyone, to believe anything upon insufficient [plural:start]",
                "There is but one truly serious [singular_noun:end] problem, and that is [plural:start]",
                "I once had [singular_noun:a:start], it was a nice [singular_noun:start]. But that's not relevant now."
            ]
        elif relation == 'AtLocation':
            templates = [
                "Where else would [singular_noun:a:start] be?",
                "[plural:end] are near [plural:end.AtLocation], so [singular_noun:a:start] must be there too",
                "Because [singular_noun:a:start] is [singular_noun:a:start.IsA.end] and [singular_noun:a:end] is [singular_noun:a:end.IsA.end]",
                "I found [singular_noun:a:start] once, it wasn't near [singular_noun:a:end], I miss my [singular_noun:a:start] :(",
                u"╰( ⁰ ਊ ⁰ )━☆ﾟ.*･｡ﾟ"
            ]
        elif relation == 'AtLocation.SubjectAtLocation':
            templates = [
                "I'd usually look for [singular_noun:a:subject] near [plural:subject.AtLocation]",
                "It depends, if [singular_noun:a:subject] is [singular_noun:a:subject.IsA] then it would be near [plural:start.AtLocation]",
                "One cannot step twice in the same [singular_noun:end], so [singular_noun:a:subject] must be near [subject.AtLocation]",
                "To put it bluntly, not near [singular_noun:a:end]",
                "I find [plural:subject] in my imagination!",
                u"¯\_(ツ)_/¯"
            ]
        elif relation == 'AtLocation.GuessAtLocation':
            templates = [
                "Nope, [singular_noun:a:guess] is [singular_noun:a:guess.IsA] so it seems unlikely",
                "Only when [singular_noun:a:start] has [singular_noun:a:start.HasA]",
                "Well, [singular_noun:guess] is a nice place to be, so long as [singular_noun:a:start] can be [start.UsedFor]",
                "[singular_noun:a:start] lies in [singular_noun:a:end], and perfect [plural:subject] lies in the best [singular_noun:guess]",
                "Sometimes, it depends on if the [singular_noun:subject] is [singular_noun:a:subject.IsA]",
                u"I know the answer to that one but I'm not going to tell you ᕕ( ⁰ ▽ ⁰ )ᕗ"
            ]
        elif relation == 'AtLocation.InsteadAtLocation':
            templates = [
                "Woah... and what if [singular_noun:a:start] can [start.CapableOf]?",
                "I doubt it would make much difference to [singular_noun:a:start] considering it's not [singular_noun:a:end.IsA]",
                "I would run scared, [singular_noun:a:start] should never be near [plural:startLocation]",
                "What? No, [singular_noun:a:start] would never be near [singular_noun:a:end]"
            ]
        elif relation == 'RelatedTo.InsteadIsA':
            templates = [
                "The [guess] [singular_noun:start] is that which overcomes not only it's [end] but also it's [singular_noun:start.HasA]",
                "When [singular_noun:a:guess] can [guess.CapableOf] I would suggest it must also be [singular_noun:a:end]",
                "[singular_noun:a:guess] is the sign of the [singular_noun:start], it is the opium of the people",
                u"(ʘᗩʘ’)"
            ]
        elif relation == 'Compared':
            templates = [
                "Occasionally a [endAttribute] [singular_noun:end] can also be a [startAttribute] [singular_noun:start]",
                "The only thing I know is that I know [plural:start] are [singular_noun:start.IsA]",
                "[start] [startAttribute] for the worst, if they be not altered for the [endAttribute] designedly"
            ]
        elif relation == 'StillA':
            templates = [
                "Perhaps if [singular_noun:a:start] is also [singular_noun:a:start.IsA] then it could be",
                "Sometimes [singular_noun:a:start] can be [startAttribute], but that is rare",
                "I don't know why [plural:start] are [startAttribute], but I'm pretty sure it's not to [start.CapableOf]"
            ]

        if templates:
            random.shuffle(templates)
            for template in templates:
                # print "-- " + template
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
            splits = item.split(':')
            inflections = splits[:-1]
            concepts = splits[-1:][0]

            subjectGroup, relation, rest = just(3, concepts.split('.'))
            subject = subjects.group(subjectGroup)

            if subject is not None:
                concept = subject
                if relation:
                    concept = self.get_concept(subject, relation)
                    if concept is None:
                        return None
                inflected = concept
                for inflection in inflections:
                    inflectorMethod = getattr(inflector, inflection)
                    temp = inflectorMethod(inflected)
                    if temp:
                        inflected = temp
                composed = composed.replace('[' + item + ']', inflected)

        return composed

    def get_concept(self, subject, relation):
        baseUrl = 'http://conceptnet5.media.mit.edu/data/5.4/c/en/'
        self.log('Getting concept from {}'.format(baseUrl + subject))
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
