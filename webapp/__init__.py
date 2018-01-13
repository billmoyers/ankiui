# -*- coding: UTF-8 -*-

import sys
import os
import tornado.web
import tornado.ioloop
sys.path.insert(0, './lib/anki/')
from anki import Collection as aopen

def setDeck(collection, deckName):
	d = collection.decks.byName(deckName)
	collection.decks.select(d['id'])

class BaseHandler (tornado.web.RequestHandler):
	def initialize(self, appPath, themePath, fdeck):
		self.appPath = appPath
		self.themePath = themePath
		self.fdeck = fdeck
	
class IndexHandler (BaseHandler):
	def get(self):
		coll = self.fdeck()
		try:
			decks = []
			for d in coll.decks.all():
				setDeck(coll, d['name'])
				card = coll.sched.getCard()
				counts = coll.sched.counts()
				decks.append({ 
					'name': d['name'],
					'counts': counts
				})
			self.render("%s/templates/index.html" % self.appPath,
				themePath=self.themePath,
				decks=decks,
			)
		finally:
			coll.close()
		

class StudyHandler (BaseHandler):
	def get(self, deckName):
		deck = self.fdeck()
		try:
			setDeck(deck, deckName)
			card = deck.sched.getCard()
			self.render("%s/templates/study.html" % self.appPath, 
				themePath=self.themePath, 
				card=card, 
				counts=deck.sched.counts(), 
				n=len(deck.decks.cids(1)),
				deckName=deckName
			)
		finally:
			deck.close()
	
	def post(self, deckName):
		deck = self.fdeck()
		try:
			setDeck(deck, deckName)
			card = deck.sched.getCard()
			note = card.note()
			n = int(self.get_argument('response'))
			deck.sched.answerCard(card, n)
			deck.save()
			self.render("%s/templates/study.result.html" % self.appPath, 
				themePath=self.themePath,
				note=note, 
				n=n, 
				counts=deck.sched.counts(),
				deckName=deckName
			)
		finally:
			deck.close()

class ResetHandler (tornado.web.RequestHandler):
	def initialize(self, appPath, themePath, fdeck, redirectUrl):
		super.initialize(appPath, themePath, fdeck)
		self.redirectUrl = redirectUrl

	def get(self, deckName):
		deck = self.fdeck()
		try:
			setDeck(deck, deckName)
			cids = deck.decks.cids(1)
			for cid in cids:
				c = deck.getCard(cid)
				c.due -= 1
			deck.save()
			self.redirect(self.redirectUrl % self.deckName)
		finally:
			deck.close()

def app(cwd, theme, ankiFilePath):
	fdeck = lambda: aopen(ankiFilePath)
	d = {'appPath': cwd, 'themePath': '%s/themes/%s/base.html' % (cwd, theme), 'fdeck': fdeck}
	return tornado.web.Application([
			(r'/anki/decks/*/', IndexHandler, d),
			(r'/anki/decks/([^/]+)/study', StudyHandler, d),
			(r'/anki/decks/([^/]+)/reset', ResetHandler, {**d, **{'redirectUrl': '/anki/decks/%s/study'}})
		], 
		debug = True,
		template_path = '%s/themes/%s/' % (cwd, theme),
		static_path = '%s/themes/%s/static' % (cwd, theme)
	)

if __name__ == '__main__':
	application = app(os.getcwd(), os.environ["ANKI_WEBAPP_THEME"], os.environ["ANKI_DECK_PATH"])
	application.listen(os.environ["TORNADO_PORT"])
	tornado.ioloop.IOLoop.instance().start()

