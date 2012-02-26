import os
import cgi
import datetime
import wsgiref.handlers
import logging

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from models import *

class SavePost(webapp.RequestHandler):
  def post(self):
	user = users.get_current_user()
	blogdata = BlogData()
  	blogdata.author = user.nickname()
	logging.debug('Author:'+blogdata.author)
        blogdata.title=self.request.get('title')
   	blogdata.content = self.request.get('content')
    	logging.debug('Content:'+blogdata.content)
	blogdata.put()
	self.redirect('/')
