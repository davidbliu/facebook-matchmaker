import facebook
import urllib2
import json
import pickle
from Queue import *
import yaml
oauth_access_token = data['oauth_access_token']

ROOT = "comments/"
newsfeed = pickle.load( open( "pickle.p", "rb" ) )

