#! /usr/bin/python
from __future__ import print_function
import fileinput
import sys
import codecs
import os.path
import logging
import re
import file_util
import traceback
from file_util import ID,FORM,CPOSTAG #column index for the columns we'll need

try:
    import argparse
except:
    #we are on Python 2.6 or older
    from compat import argparse


def makeWordDictionary(trees):
	fileDictionary=open('fileWordDictionary.txt', 'w').close() #erase content
	fileDictionary=open('fileWordDictionary.txt', 'a') #open file to save
	list_word = ['_']
	print("_", end="\n", file=fileDictionary)
	for comments,tree in trees:
		for line in tree:
			tempPOS = line[FORM]
			if not line[ID].isdigit():
				continue
			if tempPOS not in list_word:
				temp = tempPOS.encode('UTF8')
				print(temp, end="\n", file=fileDictionary)
				list_word.append(tempPOS)
	return list_word

def makePOSTagDictionary(trees):
	filePOSTag=open('filePOSTag.txt', 'w').close() #open file to save
	filePOSTag=open('filePOSTag.txt', 'a') #open file to save
	list_postag = ['_']
	print("_", end="\n", file=filePOSTag)
	for comments,tree in trees:
		for line in tree:
			tempPOS = line[CPOSTAG]
			if not line[ID].isdigit():
				continue
			if tempPOS not in list_postag:
				print(tempPOS, end="\n", file=filePOSTag)
				list_postag.append(tempPOS)
	return list_postag

def loadWordDictionary():
	return [line.rstrip('\n') for line in open('fileWordDictionary.txt')]

def loadPOSTag():
	return [line.rstrip('\n') for line in open('filePOSTag.txt')]

opt_parser = argparse.ArgumentParser(description="CoNLL-U validation script")

io_group=opt_parser.add_argument_group("Input / output options")
opt_parser.add_argument('input', nargs='?', help='Input file name, or "-" or nothing for standard input.')
opt_parser.add_argument('output', nargs='?', help='Output file name, or "-" or nothing for standard output.')
opt_parser.add_argument('--type', default='withPrevPOS', help='Type arff data, you can give argument "onlyWord", "withPrevPOS", "withPrevPOSWord"')
opt_parser.add_argument('--mode', default='train', help='Mode dataset, you can give argument "train" or "validator"')
args = opt_parser.parse_args() #Parsed command-line arguments
inp,out=file_util.in_out(args)
trees = file_util.trees(inp)
trees = list(trees)

if (args.mode == 'train'):
	#make word dictionary
	print("Making word dictionary...")
	wordDictionary = makeWordDictionary(trees)
	print("Make word dictionary done.")
	#make pos tag dictionary
	print("Making pos tag list...")
	posTagList = makePOSTagDictionary(trees)
	print("Make pos tag list done.")
else:
	#load word dictionary
	print("Loading word dictionary...")
	wordDictionary = loadWordDictionary()
	print("Make word dictionary done.")
	#load pos tag dictionary
	print("Making pos tag list...")
	posTagList = loadPOSTag()
	print("Make pos tag list done.")
	
#make format for arff data
print("Creating arff file...")
print("% 1. Title: POSTag dataset\n%\n% 2. Sources: UD_Indonesian\n%\n@RELATION postag", end="\n", file=out)
print("@ATTRIBUTE form NUMERIC", end="\n", file=out)
if (args.type == 'withPrevPOS' or args.type == 'withPrevPOSWord'):
            print("@ATTRIBUTE prevpostag NUMERIC", end="\n", file=out)
            if (args.type == 'withPrevPOSWord'):
                print("@ATTRIBUTE prevword NUMERIC", end="\n", file=out)
print("@ATTRIBUTE class {", end="", file=out)
for item in posTagList:
    if posTagList[-1] != item:
        print(item, end=",", file=out)
    else:
        print(item, end="}\n", file=out)

print("@DATA", end="\n", file=out)
prevpostag = "_"
prevword = "_"
arrayData = []
arrayWordFeature = []
for comments,tree in trees:
    for line in tree:
    	tempPOS = line[CPOSTAG]
    	if not line[ID].isdigit():
    		continue
    	print(wordDictionary.index(line[FORM]) if line[FORM] in wordDictionary else u"-1", end=",", file=out)
    	if (args.type == 'withPrevPOS' or args.type == 'withPrevPOSWord'):
    		print(posTagList.index(prevpostag) if prevpostag in posTagList else u"-1", end=",", file=out)
    		prevpostag = tempPOS
    		if (args.type == 'withPrevPOSWord'):
    			print(wordDictionary.index(prevword) if prevword in wordDictionary else u"-1", end=",", file=out)
    			prevword = tempPOS
    	print(tempPOS, end="\n", file=out)
    	arrayWordFeature = []

print("Done")
