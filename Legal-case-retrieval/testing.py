"""
    File name: testing.py
    Authors: Svilen Stefanov, Arijit Pramanik, Wang Chin-Hao and Madhav Goel
    Date created: 05/04/2018
    Date last modified: 24/04/2018
    Python Version: 2.7
"""

correct_output = [3984147, 3984152, 6927452]
correct_count = 0
total_retrieved = 0
total_correct = len(correct_output)
pos_list = []

with open('output.txt', 'r') as content_file:
    content = content_file.read()
    content = content.split()
    for doc in content:
    	if int(doc) in correct_output:
    		correct_count = correct_count + 1
    		pos_list.append(total_retrieved)
    	total_retrieved = total_retrieved + 1

    print "Total correct documents to be retrieved = " + str(total_correct)
    print "Total correct documents retrieved = " + str(correct_count)
    print "Precision = " + str(float(correct_count)/float(total_retrieved))
    print "Recall = " + str(float(correct_count)/float(total_correct))
    print "The positions at which the correct documents were retrieved = "
    for pos in pos_list:
    	print str(pos)




