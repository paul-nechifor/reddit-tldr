reddit-tldr
===========

A Reddit bot which posts automatic summarization to long comments. I'm running
it from time to time on [CGTLDR](http://www.reddit.com/user/CGTLDR).

Installation
------------

You need to install `praw` (for the Reddit API) and `ots` (for summarization).

    pip install praw
    pip install ots

OTS is a bit difficult to install.

Configuration
-------------

Copy the sample config and edit it.

    cp config-sample.json config.json
