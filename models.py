import cgi
import datetime
import wsgiref.handlers
import sys

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp

FETCH_THEM_ALL = ((sys.maxint - 1) >> 32) & 0xffffffff

class BlogData(db.Model):
  author = db.StringProperty()
  title = db.StringProperty()
  content = db.TextProperty()
  date = db.DateProperty(auto_now_add=True)
  time = db.TimeProperty(auto_now_add=True)
 # @classmethod
 # def get_all(cls):
 #	blog_data=db.Query(BlogData)
 # 	blog_data.order('-date')
 #	return blog_data.fetch(FETCH_THEM_ALL)	
	

