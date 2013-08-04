#!/usr/bin/env python2
# coding: utf-8

import json
import time
import re
import random
import htmlentitydefs
import traceback
import sys
from HTMLParser import HTMLParser

import praw
import ots
from praw.helpers import comment_stream


def escapeHtml(what):
    return HTMLParser.unescape.__func__(HTMLParser, what)

class CommentParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tags = set()
        self.text = ''
    def handle_starttag(self, tag, attrs):
        self.tags.add(tag)
    def handle_endtag(self, tag):
        if tag == 'p':
            self.text += '\n\n'
    def handle_data(self, data):
        self.text += data
    def handle_entityref(self, name):
        self.text += htmlentitydefs.entitydefs[name]
    def handle_charref(self, name):
        if name[0] == 'x':
            self.text += unichr(int(name[1:], 16))
        else:
            self.text += unichr(int(name))

class Client:
    def __init__(self, config):
        self.config = config
        self.summaryChars = config['summaryChars']
        self.minimumChars = config['minimumChars']
        self.replyPause = config['replyPause']
        self.allowedTags = set('div,p,i,em,b,strong'.split(','))
        self.reddit = praw.Reddit(config['userAgent'])
        self.commentList = []
        self.lastReplyTime = 0

    def start(self):
        self.reddit.login(self.config['username'], self.config['password'])
        while True:
            try:
                for comment in comment_stream(self.reddit, 'all'):
                    self.processComment(comment)
            except KeyboardInterrupt:
                return
            except:
                traceback.print_exc()
                time.sleep(15)

    def processComment(self, comment):
        plainText = self.getCommentAsGood(comment)
        if plainText is None:
            return

        self.commentList.append((len(plainText), comment, plainText))

        diff = time.time() - self.lastReplyTime
        if diff > self.replyPause and len(self.commentList) > 0:
            best = max(self.commentList, key=lambda x: x[0])
            self.commentList = []
            chars, comment, plainText = best
            replyText = self.getReplyFor(plainText)
            try:
                comment.reply(replyText)
                print replyText
                self.lastReplyTime = time.time()
            except:
                traceback.print_exc()

    def getCommentAsGood(self, comment):
        try:
            html = escapeHtml(comment.body_html)
            cp = CommentParser()
            cp.feed(html)
        except:
            traceback.print_exc()
            print 'This is bad. I should fix it.', comment.body_html
            return None

        if len(cp.text) < self.minimumChars:
            return None

        for tag in cp.tags:
            if tag not in self.allowedTags:
                return None
        
        return cp.text

    def getSummary(self, text):
        o = ots.OTS()
        o.percentage = int(self.summaryChars * 100.0 / len(text))
        o.parseUnicode(text)    
        summary = ''
        for sentence, good in o.hilite():
            if good == 1:
                summary += '* ' + sentence.replace('\n', '') + '\n'
        return summary

    def getReplyFor(self, text):
        ret = 'Computer generated TL;DR:\n\n'
        ret += unicode(self.getSummary(text), 'utf-8') 
        ret += '\n\n' + self.config['signature']
        return ret

def main():
    config = json.loads(open('config.json').read())
    client = Client(config)
    client.start()

if __name__ == '__main__':
    main()
