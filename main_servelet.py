#!/usr/bin/env python2.5
import cgi
import datetime
import wsgiref.handlers
import logging
import os


from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from models import *

#DataCount class is based on the code snippet by B.Clapper - Picoblog
class DateCount(object):
    """
    Convenience class for storing and sorting year/month counts.
    """
    def __init__(self, date, count):
        self.date = date
        self.count = count

    def __cmp__(self, other):
        return cmp(self.date, other.date)

    def __hash__(self):
        return self.date.__hash__()

    def __str__(self):
        return '%s(%d)' % (self.date, self.count)

    def __repr__(self):
        return '(%s: %s)' % (self.__class__.__name__, str(self))

class IndexPage(webapp.RequestHandler):
  def post(self):
	self.processRequest()
  def get(self):
	self.processRequest()
  def processRequest(self):
	blog_data=db.GqlQuery("SELECT * FROM BlogData ORDER BY date DESC LIMIT 10")
        user_status=users.get_current_user()
        admin_status=users.is_current_user_admin()
        login=users.create_login_url('/')
	logout=users.create_logout_url('/')
	template_value={'blog_data':blog_data,
                        'user_status':user_status,
                        'admin_status':admin_status,
			'logout' : logout,
			'login': login,
			'date_list':self.get_month_count()
                        }
	path = os.path.join(os.path.dirname(__file__), 'pages/index.html')
        self.response.out.write(template.render(path,template_value))

  #get_month_count is a function written in Picoblog, reused in this application.
  #It is written by B.Clapper

  def get_month_count(self):
      hash = BlogData.get_all_datetimes()
      datetimes = hash.keys()
      date_count = {}
      for dt in datetimes:
          just_date = datetime.date(dt.year, dt.month, 1)
          try:
              date_count[just_date] += hash[dt]
          except KeyError:
              date_count[just_date] = hash[dt]
      dates = date_count.keys()
      dates.sort()
      dates.reverse()
      return [DateCount(date, date_count[date]) for date in dates]

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



class MonthArchive(webapp.RequestHandler):
  def get(self,year,month):
	blog_data=BlogData.all_for_month(int(year),int(month))
        user_status=users.get_current_user()
        admin_status=users.is_current_user_admin()
        login=users.create_login_url('/')
	logout=users.create_logout_url('/')
	logging.debug("Debug of Query object incoming")
	for data in blog_data:
          logging.debug('Content is :'+ data.content)
	#for i in self.get_month_count():
        #    logging.debug(i.count)
	template_value={'blog_data':blog_data,
                        'user_status':user_status,
                        'admin_status':admin_status,
			'logout' : logout,
			'login': login
                        }
	path = os.path.join(os.path.dirname(__file__), 'pages/index.html')
        self.response.out.write(template.render(path,template_value))

class EditPost(webapp.RequestHandler):
  def get(self,postid):
        logging.debug('In EditPost')
        #logging.debug(int(postid))
	blog_data = BlogData.all()
        start_cursor=memcache.get('blogdata_start_cursor')
        end_cursor=memcache.get('blogdata_end_cursor')
        if start_cursor:
            blog_data.with_cursor(start_cursor=start_cursor)
        if end_cursor:
            blog_data.with_cursor(end_cursor=end_cursor)
        for data in blog_data:
            if(data.key().id()==int(postid)):
                mod_title=data.title
                mod_content=data.content
        user_status=users.get_current_user()
        admin_status=users.is_current_user_admin()
        login=users.create_login_url('/')
	logout=users.create_logout_url('/')
	template_value={'postid':postid,
                        'mod_title':mod_title,
                        'mod_content':mod_content,
                        'user_status':user_status,
                        'admin_status':admin_status,
			'logout' : logout,
			'login': login,
			}

        user=users.get_current_user()
	if user:
		logging.debug('User login done')
		if users.is_current_user_admin():
			logging.debug('User is a admin')
			path = os.path.join(os.path.dirname(__file__), 'pages/admin_edit.html')
        		self.response.out.write(template.render(path,template_value))
		else:
			self.redirect('/') #needs to be changed to a static non admin error page
	else:
		logging.debug('User not found..Login please')
		self.redirect(users.create_login_url(self.request.uri))

class SaveEditPost(webapp.RequestHandler):
    def post(self):
        postid=int(self.request.get('postid'))
        bd=BlogData.get_by_id(postid)
        bd.title=self.request.get('title')
        bd.content=self.request.get('content')
        bd.put()
        self.redirect('/')
application = webapp.WSGIApplication([
  ('/', IndexPage),
  ('/admin',AdminDash),
  ('/save',SavePost),
  ('/date/(\d\d\d\d)-(\d\d)/?$',MonthArchive),
  ('/edit/(\w)*/?$',EditPost),
  ('/editsave',SaveEditPost)
], debug=True)



def main():
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
