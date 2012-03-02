import cgi
import datetime
import wsgiref.handlers
import sys
import logging

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import blobstore

FETCH_THEM_ALL = ((sys.maxint - 1) >> 32) & 0xffffffff

class BlogData(db.Model):
  author = db.StringProperty()
  title = db.StringProperty()
  content = db.TextProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  blob_key=db.StringProperty()
 # @classmethod
 # def get_all(cls):
 #	blog_data=db.Query(BlogData)
 # 	blog_data.order('-date')
 #	return blog_data.fetch(FETCH_THEM_ALL)	

 #Code snippet taken from Picoblog - Written by clapper.
  @classmethod
  def get_all_datetimes(cls):
	dates = {}
	published_data= db.Query(BlogData)
	#logging.debug('Published Data from models')
	#logging.debug(published_data)
	for blogdata in published_data:
		date = datetime.datetime(blogdata.date.year,blogdata.date.month,blogdata.date.day)
		try:
			dates[date] += 1
		except KeyError:
			dates[date] = 1
	return dates
  @classmethod
  def all_for_month(cls, year, month):
	start_date = datetime.datetime(year, month, 1,0,0,0)
        logging.debug('Start Date')
        logging.debug(start_date)
	if start_date.month == 12:
        	next_year = start_date.year + 1
        	next_month = 1
      	else:
        	next_year = start_date.year
        	next_month = start_date.month + 1
      	end_date = datetime.datetime(next_year, next_month, 1,0,0,0)
	query_output=db.Query(BlogData).filter('date >=', start_date).filter('date <', end_date).order('-date')
	return query_output
   	

