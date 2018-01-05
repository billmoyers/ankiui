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

class StudyHandler (tornado.web.RequestHandler):
	def initialize(self, appPath, themePath, fdeck):
		self.appPath = appPath
		self.themePath = themePath
		self.fdeck = fdeck

	def get(self, deckName):
		deck = self.fdeck()
		try:
			setDeck(deck, deckName)
			card = deck.sched.getCard()
			print(tornado.escape.utf8(str(card.note().keys())))
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
			n = self.get_argument('n')
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
		self.appPath = appPath
		self.themePath = themePath
		self.fdeck = fdeck
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
			self.redirect(self.redirectUrl)
		finally:
			deck.close()

def app(cwd, theme, ankiFilePath):
	fdeck = lambda: aopen(ankiFilePath)
	d = {'appPath': cwd, 'themePath': '%s/themes/%s/base.html' % (cwd, theme), 'fdeck': fdeck}
	return tornado.web.Application([
			(r'/anki/([^/]+)/study', StudyHandler, d),
			(r'/anki/([^/]+)/reset', ResetHandler, {**d, **{'redirectUrl': '/anki/study'}})
		], 
		debug = True,
		template_path = '%s/themes/%s/' % (cwd, theme),
		static_path = '%s/themes/%s/static' % (cwd, theme)
	)

if __name__ == '__main__':
	application = app(os.getcwd(), 'basic', os.environ["ANKI_DECK_PATH"])
	application.listen(os.environ["TORNADO_PORT"])
	tornado.ioloop.IOLoop.instance().start()

