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

class IndexPage(webapp.RequestHandler):
  def post(self):
	self.processRequest()
  def get(self):
	self.processRequest()
  def processRequest(self):
	blog_data=db.GqlQuery("SELECT * FROM BlogData ORDER BY date DESC LIMIT 10")
        #query=BlogData.all()
        #blog_data=query.fetch(10)
        user_status=users.get_current_user()
        admin_status=users.is_current_user_admin()
        login=users.create_login_url('/')
	logout=users.create_logout_url('/')
	logging.debug("Debug of Query object incoming")
	for data in blog_data:
          logging.debug('Author is :'+ data.author)
	#logging.debug(cgi.escape(display_data.author))
	template_value={'blog_data':blog_data,
                        'user_status':user_status,
                        'admin_status':admin_status,
			'logout' : logout,
			'login': login,
                        }
	path = os.path.join(os.path.dirname(__file__), 'pages/index.html')
        self.response.out.write(template.render(path,template_value))

