#!/usr/bin/env python2
# coding: utf-8

import json, time, re, random, traceback, htmlentitydefs
from HTMLParser import HTMLParser
import praw, ots

def escapeHtml(what):
    return HTMLParser.unescape.__func__(HTMLParser, what)

class CommentParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tags = set()
        self.text = ''
    def handle_starttag(self, tag, attrs):
        self.tags.add(tag)
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
        self.retrivePause = config['retrivePause']
        self.replyPause = config['replyPause']
        self.reddit = praw.Reddit(config['userAgent'])
        self.respondedTo = set()
        self.lastResponded = 0
        self.lastGoodComment = None
        self.lastGoodReply = None
        self.permitedTags = set('div,p,i,em,b,strong'.split(','))


    def start(self):
        self.reddit.login(self.config['username'], self.config['password'])

        self.loop()

    def loop(self):
        while True:
            try:
                comments = self.reddit.get_comments('all', limit=None)
            except:
                traceback.print_exc()
                return

            try:
                self.checkComments(comments)
            except:
                print "A problem commenting..."
                traceback.print_exc()

            self.tryToSendAReply()

            time.sleep(self.retrivePause)

    def checkComments(self, comments):
        for comment in comments:
            if comment.id in self.respondedTo:
                continue
            clean = self.commentIsGood(comment)
            if clean != None:
                print clean
                print '\n'

                self.lastGoodComment = comment
                self.lastGoodReply = self.getReplyFor(clean)
                break

    def commentIsGood(self, comment):
        html = escapeHtml(comment.body_html)

        cp = CommentParser()
        cp.feed(html)

        if len(cp.text) < 4000:
            return None

        for tag in cp.tags:
            if tag not in self.permitedTags:
                return None
        
        return cp.text

    def getReplyFor(self, text):
        ret = 'Computer generated TLDR:\n\n'
        summary = self.getSummary(text)
        print '#' * 80
        print summary
        print '#' * 80
        for line in summary.split('\n'):
            ret += '>' + line + '\n'
        ret += '\n\n' + self.config['signature']
        return ret

    def getSummary(self, text):
        letters = 900
        per = int(letters * 100.0 / len(text))

        o = ots.OTS()
        o.percentage = per
        o.parseUnicode(text)    
        return o.__str__()

    def tryToSendAReply(self):
        pausePassed = time.time() - self.lastResponded >= self.replyPause
        goodCommentExists = self.lastGoodComment != None

        if goodCommentExists and pausePassed:
            try:
                self.lastGoodComment.reply(self.lastGoodReply)
            except:
                print 'Problem replying. Abandoning this reply.'
                traceback.print_exc()
                
            self.respondedTo.add(self.lastGoodComment.id)
            self.lastGoodComment = None
            self.lastResponded = time.time()

def main():
    config = json.loads(open('config.json').read())

    c = Client(config)
    c.start()

if __name__ == '__main__':
    main()
