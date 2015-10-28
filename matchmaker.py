import processor
import scraper
import pickle
from operator import itemgetter

newsfeed = scraper.load_posts()
processor.get_people(newsfeed)
data = processor.parse_newsfeed(newsfeed)

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

for key in data['popular'].keys():
    popular_authors.append([key,data['popular'][key]])
for key in data['posts'].keys():
    author_posts.append([key,len(data['posts'][key])])
for key in data['comments'].keys():
    popular_comments.append([key, data['comments'][key]])

print author_posts
sorted_author_posts = sorted(author_posts, key= itemgetter(1))
sorted_author_posts.reverse()

sorted_popular_authors = sorted(popular_authors, key=itemgetter(1))# x: x[1])
sorted_popular_authors.reverse()

sorted_popular_comments = sorted(popular_comments, key = itemgetter(1))
sorted_popular_comments.reverse()

sorted_post_like_ratios = sorted(post_like_ratios, key = itemgetter(1))
sorted_post_like_ratios.reverse()

# writing results to outfile
post_like_ratio_txt = ""
for p in sorted_post_like_ratios:
    post_like_ratio_txt+=p[0]+": "+str(p[1])+"\n"
pop_authors_txt= ""
for p in sorted_popular_authors:
    pop_authors_txt+=p[0]+": "+str(p[1])+"\n"
most_posts_txt = ""
for p in sorted_author_posts:
    most_posts_txt+=p[0]+": "+str(p[1])+"\n"
pop_comments_txt = ""
for p in sorted_popular_comments:
    pop_comments_txt+=p[0]+": "+str(p[1])+"\n"

like_rank_txt = ""
percent_liked_rank_txt = ""
for person in data['likes'].keys():
    like_rank_txt+=person+"\n"
    percent_liked_rank_txt += person+"\n"
    like_ranks = processor.get_like_ranks(data['likes'][person])
    percent_like_ranks = processor.get_percent_liked(data['likes'][person], data['posts_and_comments'])
    for rank in like_ranks:
        like_rank_txt+="\t"+rank[0]+":  "+str(rank[1])+"\n"
    for rank in percent_like_ranks:
        percent_liked_rank_txt+="\t"+rank[0]+":  "+str(rank[1])+"\n"
    like_rank_txt+="\n"
    percent_liked_rank_txt+='\n'



with open("fa15/most_posts.txt", "w") as outfile:
    outfile.write(most_posts_txt.encode('utf-8'))
with open("fa15/popular_authors.txt", "w") as outfile:
    outfile.write(pop_authors_txt.encode('utf-8'))
with open("fa15/popular_comments.txt", "w") as outfile:
    outfile.write(pop_comments_txt.encode('utf-8'))
with open("fa15/post_like_ratios.txt", "w") as outfile:
    outfile.write(post_like_ratio_txt.encode('utf-8'))
with open("fa15/like_ranks.txt", "w") as outfile:
    outfile.write(like_rank_txt.encode('utf-8'))
with open("fa15/percent_liked_rank.txt", "w") as outfile:
    outfile.write(percent_liked_rank_txt.encode('utf-8'))

"""
STABLE MARRIAGE CODE BELOW
"""

MALES = processor.load_genders()["females"]
FEMALES = processor.load_genders()["males"]


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
        pref_list = processor.get_pref_list(person, data['likes'][person], data['posts_and_comments'], MALES, FEMALES)
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
with open("fa15/female_opt_stable_marriage.txt", "w") as outfile:
    text = ""
    for assignment in assignments.keys():
        text+= assignment+" and "+assignments[assignment]+"\n"
    outfile.write(text.encode('utf-8'))
