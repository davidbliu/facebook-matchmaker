import facebook
import urllib2
import json
import pickle
from Queue import *
import yaml
from operator import itemgetter

data = yaml.load(open('config.yaml', 'r'))
oauth_access_token = data['oauth_access_token']

"""
you get get access token here
https://developers.facebook.com/tools/explorer/?method=GET&path=me?fields=id,name&version=v2.0
"""

def get_newsfeed_list():
    newsfeed = []
    profile = graph.get_object("me")
    groups = graph.get_object("me/groups")
    PBL_GROUP_ID = -1
    for group in groups['data']:
        if group['name'] == 'Berkeley PBL Spring 2015':
            PBL_GROUP_ID = group['id']
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
    print "writing names into names.txt"
    names = set()
    for post in newsfeed:
        author_id = post['from']['id']
        name = post['from']['name']
        names.add(name)
        if 'comments' in post.keys():
            for comment in post['comments']['data']:
                author_id = comment['from']['id']
                name = comment['from']['name']
                names.add(name)
        if 'likes' in post.keys():
            for like in post['likes']['data']:
                author_id = like['id']
                name = like['name']
                names.add(name)
    with open('names.txt', 'w') as outfile:
        for name in names:
            try:
                outfile.write(name)
                outfile.write('\n')
            except:
                print 'had problem with '+name
    """ you need to manually filter males and femlaes"""


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


def load_genders():
    males = []
    with(open("males.txt", "r")) as mfile:
        line = mfile.readline()
        while line:
            males.append(line.strip("\n"))
            line = mfile.readline()
    females = []
    with(open("females.txt", "r")) as ffile:
        line = ffile.readline()
        while line:
            females.append(line.strip("\n"))
            line = ffile.readline()
    return {"males":males, "females":females}

def get_like_ranks(liked_people):
    ranks = {}
    total_likes = len(liked_people)
    for person in liked_people:
        ranks[person]=float(liked_people.count(person))/float(total_likes)
    tuples = []
    for key in ranks.keys():
        tuples.append([key, ranks[key]])
    sorted_tuples = sorted(tuples, key=itemgetter(1))
    sorted_tuples.reverse()
    return sorted_tuples

def get_percent_liked(liked_people, posts_and_comments):
    ranks = {}
    total_likes = len(liked_people)
    for person in liked_people:
        ranks[person]=float(liked_people.count(person))/float(len(posts_and_comments[person]))
    tuples = []
    for key in ranks.keys():
        tuples.append([key, ranks[key]])
    sorted_tuples = sorted(tuples, key=itemgetter(1))
    sorted_tuples.reverse()
    return sorted_tuples

def get_pref_list(name, liked_people, posts_and_comments, males, females):
    opposite_gender = males
    if name in males:
        opposite_gender = females
    percent_liked = get_percent_liked(liked_people, posts_and_comments)
    # pref_list = Queue()
    pref_list = []
    for person in percent_liked:
        if person[0] in opposite_gender:
            pref_list.append(person[0])
    return pref_list

if __name__=='__main__':
    print 'running newsfeed.py'

"""
HACKY STUFF HERE: commented out for fall 2015


pickled = True

if not pickled:
    newsfeed = get_newsfeed_list()
    pickle.dump( newsfeed, open( "pickle.p", "wb" ) )
else:
    newsfeed = pickle.load( open( "pickle.p", "rb" ) )

get_people(newsfeed)

def load_genders():
    males = []
    with(open("males.txt", "r")) as mfile:
        line = mfile.readline()
        while line:
            males.append(line.strip("\n"))
            line = mfile.readline()
    females = []
    with(open("females.txt", "r")) as ffile:
        line = ffile.readline()
        while line:
            females.append(line.strip("\n"))
            line = ffile.readline()
    return {"males":males, "females":females}
print len(newsfeed)

print 'parsing newsfeed for juicy details...'
data = parse_newsfeed(newsfeed)


author_posts = []
popular_authors = []
popular_comments = []
post_like_ratios = []
for key in data['posts_and_comments']:
    author = key
    num_posts = len(data['posts_and_comments'][key])
    likes = data['popular'][key]
    ratio = float(likes)/float(num_posts)
    post_like_ratios.append([key, ratio])

    # print author
    # print num_posts
    # print likes
    # print ratio
for key in data['popular'].keys():
    popular_authors.append([key,data['popular'][key]])
for key in data['posts'].keys():
    # print key+": "+str(len(data['posts'][key]))
    author_posts.append([key,len(data['posts'][key])])
for key in data['comments'].keys():
    popular_comments.append([key, data['comments'][key]])

from operator import itemgetter
sorted_author_posts = sorted(author_posts, key=itemgetter(1))
sorted_author_posts.reverse()

sorted_popular_authors = sorted(popular_authors, key=itemgetter(1))
sorted_popular_authors.reverse()

sorted_popular_comments = sorted(popular_comments, key=itemgetter(1))
sorted_popular_comments.reverse()

sorted_post_like_ratios = sorted(post_like_ratios, key = itemgetter(1))
sorted_post_like_ratios.reverse()

#
# writing name: number of posts
#
post_like_ratio_txt = ""
for p in sorted_post_like_ratios:
    # print p[0]+": "+str(p[1])
    post_like_ratio_txt+=p[0]+": "+str(p[1])+"\n"
pop_authors_txt= ""
for p in sorted_popular_authors:
    # print p[0]+": "+str(p[1])
    pop_authors_txt+=p[0]+": "+str(p[1])+"\n"
most_posts_txt = ""
for p in sorted_author_posts:
    # print p[0]+": "+str(p[1])
    most_posts_txt+=p[0]+": "+str(p[1])+"\n"
pop_comments_txt = ""
for p in sorted_popular_comments:
    # print p[0]+": "+str(p[1])
    pop_comments_txt+=p[0]+": "+str(p[1])+"\n"
# print data['likes']['David Liu']
like_rank_txt = ""
percent_liked_rank_txt = ""
for person in data['likes'].keys():
    like_rank_txt+=person+"\n"
    percent_liked_rank_txt += person+"\n"
    like_ranks = get_like_ranks(data['likes'][person])
    percent_like_ranks = get_percent_liked(data['likes'][person], data['posts_and_comments'])
    for rank in like_ranks:
        like_rank_txt+="\t"+rank[0]+":  "+str(rank[1])+"\n"
    for rank in percent_like_ranks:
        percent_liked_rank_txt+="\t"+rank[0]+":  "+str(rank[1])+"\n"
    like_rank_txt+="\n"
    percent_liked_rank_txt+='\n'
    # like_rank_txt+='\t'+str(get_like_ranks(data['likes'][person]))+'\n'

# def stable_marriage():


MALES = load_genders()["males"]
FEMALES = load_genders()["females"]


def get_index_in_list(item, thelist):
    if item not in thelist:
        return 100000000
    return thelist.index(item)
#
# do stable marriage
#
def stable_marriage(data):
    assignments = {}
    people = data['likes'].keys()
    preferences = {}
    m_preferences = {}
    f_preferences = {}
    for person in people:
        pref_list = get_pref_list(person, data['likes'][person], data['posts_and_comments'], MALES, FEMALES)
        if person in MALES:
            m_preferences[person]=pref_list
        else:
            f_preferences[person] = pref_list
    assignments = {}
    maxrounds = 30
    round_index = 0
    while len(m_preferences.keys()) > 0 and round_index < maxrounds:
        round_index+=1
        data = do_round(assignments, m_preferences, f_preferences)
        assignments = data['assignments']
        m_preferences = data['m_preferences']
    return assignments

def do_round(assignments, m_preferences, f_preferences):
    print 'doing a round....'
    num_assigned = 0
    for male in m_preferences.keys():
        # if already assignmed, move on
        if len(m_preferences[male]) == 0:
            print male +' has no preferences'
            m_preferences.pop(male, None)
        elif male not in assignments.values():
            prefs = m_preferences[male]
            top_choice = prefs[0]
            if len(prefs) <= 1:
                m_preferences.pop(male, None)
            else:
                m_preferences[male] = prefs[1:]
            # propose to top choice
            if top_choice not in assignments.keys():
                assignments[top_choice] = male
            else:
                current_male = assignments[top_choice]
                current_rank = get_index_in_list(current_male, f_preferences[top_choice])
                this_rank = get_index_in_list(male, f_preferences[top_choice])
                if this_rank < current_rank:
                    assignments[top_choice] = male

    return {"assignments":assignments, "m_preferences":m_preferences}

assignments = stable_marriage(data)
with open("spring/male_opt_stable_marriage.txt", "w") as outfile:
    text = ""
    for assignment in assignments.keys():
        text+= assignment+" and "+assignments[assignment]+"\n"
    outfile.write(text.encode('utf-8'))

with open("spring/most_posts.txt", "w") as outfile:
    outfile.write(most_posts_txt.encode('utf-8'))
with open("spring/popular_authors.txt", "w") as outfile:
    outfile.write(pop_authors_txt.encode('utf-8'))
with open("spring/popular_comments.txt", "w") as outfile:
    outfile.write(pop_comments_txt.encode('utf-8'))

with open("spring/random.txt", "w") as outfile:
    outfile.write(pop_comments_txt.encode('utf-8'))

with open("spring/post_like_ratios.txt", "w") as outfile:
    outfile.write(post_like_ratio_txt.encode('utf-8'))
with open("spring/like_ranks.txt", "w") as outfile:
    outfile.write(like_rank_txt.encode('utf-8'))
with open("spring/percent_liked_rank_txt.txt", "w") as outfile:
    outfile.write(percent_liked_rank_txt.encode('utf-8'))

with open("spring/people.txt", "w") as outfile:
    plist = ""
    for person in data['likes'].keys():
        plist+=person+"\n"
    outfile.write(plist.encode('utf-8'))
"""
