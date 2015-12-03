#! /usr/bin/env python

## https://pypi.python.org/pypi/trello
## See also https://pythonhosted.org/trello/trello.html
from trello import TrelloApi

from requests.exceptions import HTTPError
import sys, os

assert(os.path.exists('APPKEY'))
assert(os.path.exists('TOKEN'))

## To get an app key, go here:
## https://trello.com/app-key
APPKEY = open('APPKEY').readlines()[0].strip() #'b7c87d9c9fa46d2cfd6ffe83708ab231'
trello = TrelloApi(APPKEY)

## To get a new token, call this:
## trello.get_token_url('b7c87d9c9fa46d2cfd6ffe83708ab231', write_access=False)
## and put the resulting URL in a browser
TOKEN = open('TOKEN').readlines()[0].strip() # '546a304d04c4964f66ce556ac904406b7f5169a76d132c06b16a1303db1a5565'

trello.set_token(TOKEN)

try:
	BOARDID = sys.argv[1] ## top mass board: https://trello.com/b/qARjRq3f
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


## Loop on the cards and list their descriptions
print 50*'#'
for card in cards:
	# Skip cards with label 'Organization'
	if len([l for l in card['labels'] if 'Organization' in l['name']]): continue

	print '-'*30
	print card['name']
	print card['desc']

print 50*'#'
