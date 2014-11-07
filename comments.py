import facebook
import urllib2
import json
import pickle
from Queue import *
import yaml
from get_newsfeed import *
from operator import itemgetter
import string
import csv
ROOT = "comments/"
newsfeed = pickle.load( open( "pickle.p", "rb" ) )
data = parse_newsfeed(newsfeed)
dictionary = {}
person_vocab = {}
punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
for person in data['posts_and_comments'].keys():
	if person not in person_vocab.keys():
		person_vocab[person] = {}
	comments = data['posts_and_comments'][person]
	for comment in comments:
		for word in comment.split():
			word = word.lower()
			word = "".join(c for c in word if c not in punctuations)
			if word not in dictionary.keys():
				dictionary[word] = 0
			if word not in person_vocab[person].keys():
				person_vocab[person][word] = 0
			dictionary[word] += 1
			person_vocab[person][word] +=1

#
# removes words that aren't words
# (words that have only been spoken by one person)
#
def clean_lexicon(dictionary, person_vocab):
	for key in dictionary.keys():
		if dictionary[key] < 2:
			dictionary.pop(key, None)
	dictionary_keys = dictionary.keys()
	for person in person_vocab.keys():
		person_dict = person_vocab[person]
		for key in person_dict.keys():
			if key not in dictionary_keys:
				person_dict.pop(key, None)
		person_vocab[person] = person_dict
	return {"dictionary":dictionary, "person_vocab" : person_vocab}
def lexicon_in_order(person, person_vocab, dictionary):
	vocab = []
	for word in person_vocab[person].keys():
		if dictionary[word] >= 2:
			vocab.append([word, float(person_vocab[person][word])/float(dictionary[word])])
	vocab = sorted(vocab, key=itemgetter(1))
	vocab.reverse()
	return vocab

def print_all_lexicons(person_vocab, dictionary):
	output_txt = ""
	people = person_vocab.keys()
	people.sort()
	for person in people:
		print "getting "+person+" vocab"
		output_txt+=person+"\n"
		words = lexicon_in_order(person, person_vocab, dictionary)
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

def get_speech_vector(person, person_vocab, dictionary):
	vec = []
	vec_txt = ""
	person_dict = person_vocab[person]
	dict_keys = dictionary.keys()
	dict_keys.sort()
	person_dict_keys = person_dict.keys()
	for key in dict_keys:
		occurrences = 0
		if key in person_dict_keys:
			occurrences = person_dict[key] #float(person_dict[key])/float(dictionary[key])
		vec.append(occurrences)
		vec_txt+=str(occurrences)+","
	# return vec_txt[1:len(vec_txt)-1]
	return vec

def write_speech_vectors(person_vocab, dictionary):
	with open(ROOT+"people.csv", "wb") as pplfile:
		pplwriter = csv.writer(pplfile, delimiter=',',
	                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
		with open(ROOT+'speech_vectors.csv', 'wb') as csvfile:
			for person in person_vocab.keys():
				speech_vec = get_speech_vector(person, person_vocab, dictionary)
				writer = csv.writer(csvfile, delimiter=',',
	                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
				writer.writerow(speech_vec)
				pplwriter.writerow([person.encode("utf-8")])

# print dictionary
# mywords = lexicon_in_order("David Liu", person_vocab)
# for word in mywords:
# 	print word[0]+": "+str(word[1])

clean_data = clean_lexicon(dictionary, person_vocab)
person_vocab = clean_data["person_vocab"]
dictionary = clean_data["dictionary"]
print_all_lexicons(person_vocab, dictionary)
print_dictionary(dictionary)

vector = get_speech_vector("David Liu", person_vocab, dictionary)
print vector
print len(vector)

write_speech_vectors(person_vocab, dictionary)