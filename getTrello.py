#! /usr/bin/env python

## https://pypi.python.org/pypi/trello
## See also https://pythonhosted.org/trello/trello.html
from trello import TrelloApi

from requests.exceptions import HTTPError
import sys, os, re

assert(os.path.exists('APPKEY'))
assert(os.path.exists('TOKEN'))

## To get an app key, go here:
## https://trello.com/app-key
APPKEY = open('APPKEY').readlines()[0].strip()
trello = TrelloApi(APPKEY)

## To get a new token, call this:
## trello.get_token_url(APPKEY, write_access=False)
## and put the resulting URL in a browser
TOKEN = open('TOKEN').readlines()[0].strip()

trello.set_token(TOKEN)

try:
	BOARDID = sys.argv[1]
except IndexError:
	print "ERROR: Please provide a board id in the command line"
	sys.exit(-1)

try:
	cards = trello.boards.get_card(BOARDID)
except HTTPError, e:
	message = 'Unknown HTTPError'
	if e.message.startswith('400'):
		message = 'Undefined HTTPError (bad board id?)'
	if e.message.startswith('401'):
		message = 'Unauthorized (bad token or app key?)'

	print 'ERROR: %s' % message
	sys.exit(-1)


def getCADILine(line):
	try:
		return re.search(r'TOP-[0-9X]{2}-[0-9X]{3}', line).group(0)
	except AttributeError:
		return None

def getParticipants(line):
	return re.findall(r'^[\*]{2}([\w\s/?]*)[\*]{2} \([\*]{1}([\w\s,?]*)[\*]{1}\)', line, re.M)

def getAnalysisNotes(line):
	return list(set(re.findall(r'(AN-20[\d]{2}/[\d]{1,3})', line)))

def getPresentations(line):
	return re.findall(r'https:\/\/indico\.cern\.ch\/event\/(\d{6})', line)


def getHeadline(line):
	try:
		return re.match(r'(.*)\n---', line).group(1)
	except AttributeError:
		return None

## Loop on the cards and list their descriptions
analyses = {}
print 50*'#'
for card in cards:
	# Skip cards with label 'Organization'
	if len([l for l in card['labels'] if 'Organization' in l['name']]): continue

	analyses[card['idShort']] = (getCADILine(card['name']), card['desc'])

for cadi, desc in sorted(analyses.values()):
	print cadi,
	print ' | ',

	headl, parts, notes, press = [x(desc) for x in [getHeadline,
	                                                getParticipants,
	                                                getAnalysisNotes,
	                                                getPresentations]]

	print '%-60s' % headl,
	print ' | ',

	institutes = [i for i,_ in parts]
	print '%-30s' % ', '.join(institutes),
	print ' | ',
	# people = [p for _,p in parts]
	# print '%-120s' % ', '.join(people),
	# print ' | ',
	print '%-30s' % ', '.join(notes),
	print ' | '

