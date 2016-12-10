reddit-tldr
===========

A Reddit bot which posts automatic summarization to long comments. I'm running
it from time to time on [CGTLDR](http://www.reddit.com/user/CGTLDR).

Installation
------------

You need to install `praw` (for the Reddit API) and `ots` (for summarization).

    pip install praw
    
To install ots, do the following :
    
    sudo apt-get install libots

    sudo apt-get install libots-dev
	
    pip install ots


Configuration
-------------

Copy the sample config and edit it.

    cp config-sample.json config.json
