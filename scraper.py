import facebook
import os
import urllib2
import json
import pickle
"""
you get get access token here
https://developers.facebook.com/tools/explorer/?method=GET&path=me?fields=id,name&version=v2.0
"""
# RELOAD = True
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
GROUP_NAME = 'Berkeley PBL Fall 2015'
GRAPH = facebook.GraphAPI(ACCESS_TOKEN)
AVALON_ID = -1
DATA_FILENAME = 'fbdata.p'

# gets all posts from the GROUP_NAME
def get_posts():
    newsfeed = []
    groups = GRAPH.get_object("me/groups")
    for group in groups['data']:
        if group['name'] == GROUP_NAME:
            GROUP_ID = group['id']
    
    fb_url_suffix = "?access_token="+ACCESS_TOKEN
    fb_url_prefix = "https://graph.facebook.com/"
    posts = urllib2.urlopen(fb_url_prefix+GROUP_ID+"/feed"+fb_url_suffix).read()
    posts = json.loads(posts)
    print 'these are group posts'
    while posts and 'data' in posts.keys() and len(posts['data'])>0:
        for post in posts['data']:
            newsfeed.append(post)
        print 'done adding those there are now '+str(len(newsfeed))+' elems in newsfeed'
        next_url = posts['paging']['next']
        posts = json.loads(urllib2.urlopen(next_url).read())
    return newsfeed

def load_posts():
    return pickle.load(open(DATA_FILENAME, 'rb'))

if __name__ == '__main__':
    newsfeed = get_posts()
    print newsfeed
    pickle.dump(newsfeed, open(DATA_FILENAME, 'wb'))
