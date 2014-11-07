import facebook
import urllib2
import json
import pickle
from Queue import *
import yaml
from get_newsfeed import *
from operator import itemgetter
ROOT = "comments/"
newsfeed = pickle.load( open( "pickle.p", "rb" ) )
data = parse_newsfeed(newsfeed)

dictionary = {}
person_vocab = {}

for person in data['posts_and_comments'].keys():
	if person not in person_vocab.keys():
		person_vocab[person] = {}
	comments = data['posts_and_comments'][person]
	for comment in comments:
		for word in comment.split():
			word = word.lower()
			if word not in dictionary.keys():
				dictionary[word] = 0
			if word not in person_vocab[person].keys():
				person_vocab[person][word] = 0
			dictionary[word] += 1
			person_vocab[person][word] +=1

def normalize_vocabs():
	print 'hi'
def lexicon_in_order(person, person_vocab):

	vocab = []
	for word in person_vocab[person].keys():
		if dictionary[word] >= 2:
			vocab.append([word, float(person_vocab[person][word])/float(dictionary[word])])
	vocab = sorted(vocab, key=itemgetter(1))
	vocab.reverse()
	return vocab

def print_all_lexicons(person_vocab):
	output_txt = ""
	people = person_vocab.keys()
	people.sort()
	for person in people:
		print "getting "+person+" vocab"
		output_txt+=person+"\n"
		words = lexicon_in_order(person, person_vocab)
		end = min(50, len(words))
		output_txt+="\t"
		for i in range(0, end):
			output_txt+= words[i][0]+", "
		output_txt+="\n"
	with open(ROOT+"vocabulary.txt", "w") as outfile:
		outfile.write(output_txt.encode('utf-8'))

def print_dictionary(dictionary):
	vocab = []
	for word in dictionary.keys():
		vocab.append([word, dictionary[word] ])
	vocab = sorted(vocab, key=itemgetter(1))
	vocab.reverse()
	output_txt = ""
	for word in vocab:
		output_txt+=word[0]+": "+str(word[1])+"\n"
	with open(ROOT+"dictionary.txt", "w") as outfile:
		outfile.write(output_txt.encode('utf-8'))
# print dictionary
# mywords = lexicon_in_order("David Liu", person_vocab)
# for word in mywords:
# 	print word[0]+": "+str(word[1])
			
print_all_lexicons(person_vocab)
print_dictionary(dictionary)