with open('names.txt', 'r') as infile:
    names = [x for x in infile]
with open('males.txt', 'r') as infile:
    males = [x for x in infile]
print names
print males
females = [x for x in names if x not in males]
with open('females.txt', 'w') as outfile:
    for female in females:
        outfile.write(female)
