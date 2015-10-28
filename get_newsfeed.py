import facebook
import urllib2
import json
import pickle
import yaml
from Queue import *

data = yaml.load(open('config.yaml', 'r'))
oauth_access_token = data['oauth_access_token']
print 'access token: '+oauth_access_token
"""
you get get access token here
https://developers.facebook.com/tools/explorer/?method=GET&path=me?fields=id,name&version=v2.0
"""

graph = facebook.GraphAPI(oauth_access_token)
print 'grabbing your newsfeed...'

#
# should also populate males and females list
#
def get_newsfeed_list():
	newsfeed = []
	groups = graph.get_object("me/groups")
        print 'groups'
	PBL_GROUP_ID = -1
	for group in groups['data']:
		if group['name'] == "Berkeley PBL Fall 2015": #'Berkeley PBL Fall 2014':
			PBL_GROUP_ID = group['id']
	# PBL_GROUP_ID="648338708594339"
        print 'this is the group id: '+PBL_GROUP_ID
	fb_url_suffix = "?access_token="+oauth_access_token
	fb_url_prefix = "https://graph.facebook.com/"
	pbl_group_posts = urllib2.urlopen(fb_url_prefix+PBL_GROUP_ID+"/feed"+fb_url_suffix).read()
	pbl_group_posts = json.loads(pbl_group_posts)
	print 'these are group posts'
	while pbl_group_posts and 'data' in pbl_group_posts.keys() and len(pbl_group_posts['data'])>0:
		# print pbl_group_posts
		for post in pbl_group_posts['data']:
			newsfeed.append(post)
		print 'done adding those there are now '+str(len(newsfeed))+' elems in newsfeed'
		next_url = pbl_group_posts['paging']['next']
		pbl_group_posts = json.loads(urllib2.urlopen(next_url).read())
	return newsfeed

def get_people(newsfeed):
	males = []
	females = []
	for post in newsfeed:
		author_id = post['from']['id']
		name = post['from']['name']
		if name not in males and name not in females:
			gender = graph.get_object(author_id)['gender']
			if gender == "male":
				males.append(name)
			else:
				females.append(name)
		if 'comments' in post.keys():
			for comment in post['comments']['data']:
				author_id = comment['from']['id']
				name = comment['from']['name']
				if name not in males and name not in females:
					gender = graph.get_object(author_id)['gender']
					if gender == "male":
						males.append(name)
					else:
						females.append(name)
		if 'likes' in post.keys():
			for like in post['likes']['data']:
				author_id = like['id']
				name = like['name']
				if name not in males and name not in females:
					gender = graph.get_object(author_id)['gender']
					if gender == "male":
						males.append(name)
					else:
						females.append(name)
	male_txt = ""
	female_txt = ""
	for male in males:
		male_txt+=male+"\n"
	for female in females:
		female_txt+=female+"\n"
	with open("males.txt", "w") as outfile:
		outfile.write(male_txt.encode('utf-8'))
	with open("females.txt", "w") as outfile:
		outfile.write(female_txt.encode('utf-8'))

# 
# gets you the data on who did what
#
def parse_newsfeed(newsfeed):
	posts = {}
	comments = {}
	likes = {}
	popular = {}
	posts_and_comments = {}
	for post in newsfeed:
		author = post['from']['name']
		# print author
		if 'message' in post.keys():
			message = post['message']
		else:
			message = ""
			print 'this post by ' +author+' has no message'
		if author not in posts.keys():
			posts[author] = []
		if author not in posts_and_comments.keys():
			posts_and_comments[author] = []
		posts[author].append(message)
		posts_and_comments[author].append(message)

		# count people that like posts
		if 'likes' in post.keys():
			post_likes = post['likes']['data']
			for like in post_likes:
				liker =  like['name']
				if liker not in likes.keys():
					likes[liker] = []
				likes[liker].append(author)
				if author not in popular.keys():
					popular[author] = 0
				popular[author]+=1
		# count people that like comments
		if 'comments' in post.keys():
			post_comments = post['comments']['data']
			for comment in post_comments:
				comment_author = comment['from']['name']
				num_likes = int(comment['like_count'])
				if comment_author not in popular.keys():
					popular[comment_author] = 0
				if comment_author not in posts_and_comments.keys():
					posts_and_comments[comment_author] = []
				posts_and_comments[comment_author].append(comment['message'])
				popular[comment_author]+= int(num_likes)
				comments[comment_author+" said: "+comment['message']] = int(num_likes)

	return {"posts": posts, "comments": comments, "likes": likes, 'popular':popular, 'posts_and_comments':posts_and_comments}

def get_newsfeed_and_save():
	newsfeed = get_newsfeed_list()
	with open('newsfeed15.p', 'w') as outfile:
		pickle.dump(newsfeed, outfile)

if __name__ == "__main__":
	# newfeed = get_newsfeed_list()
	get_newsfeed_and_save()
	# if True:
	# 	newsfeed = get_newsfeed_list()
	# 	pickle.dump( newsfeed, open( "pickle.p", "wb" ) )
	# else:
	# 	newsfeed = pickle.load( open( "pickle.p", "rb" ) )
	# get_people(newsfeed)
