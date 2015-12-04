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
	lists = trello.boards.get_list(BOARDID)
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
	return re.findall(r'^[\*]{2}([^*]*)[\*]{2} \([\*]{1}([^*]*)[\*]{1}\)', line, re.M)

def getAnalysisNotes(line):
	return list(set(re.findall(r'(AN-20[\d]{2}/[\d]{1,3})', line)))

def getPresentations(line):
	return re.findall(r'https:\/\/indico\.cern\.ch\/event\/(\d{6})', line)


def getHeadline(line):
	try:
		return re.match(r'(.*)\n---', line).group(1)
	except AttributeError:
		return None

# Get the names of lists
listnames = {}
for l in lists:
	listnames[l['id']] = l['name']

## Loop on the cards and list their descriptions
analyses = {}
for card in cards:
	# Skip cards with label 'Organization'
	if len([l for l in card['labels'] if 'Organization' in l['name']]): continue

	analyses[card['idShort']] = (getCADILine(card['name']), card['desc'], listnames[card['idList']])


# outtable = '| *CADI Line* | *Status* | *Title* | *Groups* | *People* | *Analysis Notes* | *Presentations* |\n'
outtable = '| *CADI Line* | *Status* | *Title* | *Groups* | *Analysis Notes* | *Presentations* |\n'
for cadi, desc, stat in sorted(analyses.values()):
	if 'Done' in stat: continue

	outtable += '| '
	outtable += '%s | ' % cadi

	outtable += '%s | ' % stat

	headl, parts, notes, press = [x(desc) for x in [getHeadline,
	                                                getParticipants,
	                                                getAnalysisNotes,
	                                                getPresentations]]

	outtable += '%s | ' % headl

	institutes = [i for i,_ in parts]
	outtable += '%s | ' % ', '.join(institutes)

	# people = [p for _,p in parts]
	# outtable += '%s | ' % ', '.join(people)

	outtable += '%s | ' % ', '.join(notes)

	outtable += '%s | ' % ', '.join(press)
	outtable += '\n'
outtable += '\n'

## Add links:
outtable = re.sub(r'(TOP-XX-XXX)', 'Not yet', outtable)
outtable = re.sub(r'(TOP-[0-9X]{2}-[0-9X]{3})', '[[http://cms.cern.ch/iCMS/analysisadmin/cadilines?line=\\1][\\1]]', outtable)
outtable = re.sub(r'(AN-20[\d]{2}/[\d]{1,3})',  '[[http://cms.cern.ch/iCMS/jsp/db_notes/noteInfo.jsp?cmsnoteid=CMS%20\\1][\\1]]', outtable)
outtable = re.sub(r'(\d{6})',                   '[[https://indico.cern.ch/event/\\1][\\1]]', outtable)

with open('twikitable.txt', 'w') as ofile:
	ofile.write(outtable)

