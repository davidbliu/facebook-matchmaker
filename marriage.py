import facebook
import urllib2
import json
import pickle
from Queue import *
from get_newsfeed import *
from operator import itemgetter
ROOT = "fa14/"
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

#
# load pickled newsfeed
#
newsfeed = pickle.load( open( "pickle.p", "rb" ) )

print "newsfeed has "+str(len(newsfeed))+" items"
print 'parsing newsfeed for juicy details...'
data = parse_newsfeed(newsfeed)


MALES = load_genders()["males"]
FEMALES = load_genders()["females"]


def get_index_in_list(item, thelist):
	if item not in thelist:
		return 100000000
	return thelist.index(item)
#
# do stable marriage
#
def stable_marriage(data, MALES, FEMALES):
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


with open(ROOT+"male_optimal.txt", "w") as outfile:
	assignments = stable_marriage(data, MALES, FEMALES)
	text = ""
	for assignment in assignments.keys():
		text+= assignment+" and "+assignments[assignment]+"\n"
	outfile.write(text.encode('utf-8'))

with open(ROOT+"female_optimal.txt", "w") as outfile:
	assignments = stable_marriage(data, FEMALES, MALES)
	text = ""
	for assignment in assignments.keys():
		text+= assignment+" and "+assignments[assignment]+"\n"
	outfile.write(text.encode('utf-8'))

#
# also output like ranks
#

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

with open(ROOT+"like_ranks.txt", "w") as outfile:
	outfile.write(like_rank_txt.encode('utf-8'))
with open(ROOT+"percent_liked_rank_txt.txt", "w") as outfile:
	outfile.write(percent_liked_rank_txt.encode('utf-8'))