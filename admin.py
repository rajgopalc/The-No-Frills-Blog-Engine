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

class AdminDash(webapp.RequestHandler):
  def post(self):
	self.processRequest()
  def get(self):
	self.processRequest()
  def processRequest(self):
	logout = users.create_logout_url('/')
	template_value={'logout':logout}
	user=users.get_current_user()
	if user:
		logging.debug('User login done')
		if users.is_current_user_admin():
			logging.debug('User is a admin')
			path = os.path.join(os.path.dirname(__file__), 'pages/admin_dash.html')
        		self.response.out.write(template.render(path,template_value))
		else:
			self.redirect('/') #needs to be changed to a static non admin error page
	else:
		logging.debug('User not found..Login please')
		self.redirect(users.create_login_url(self.request.uri))
