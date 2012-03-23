#!/usr/bin/env python2.5
import cgi
import datetime
import wsgiref.handlers
import logging
import os
import urllib
import sys, traceback


from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
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
      try:
          blog_data=db.GqlQuery("SELECT * FROM BlogData ORDER BY date DESC LIMIT 10")
          user=users.get_current_user()
          if user:
              username=user.nickname()
          else:
              username=''
          admin_status=users.is_current_user_admin()
          login=users.create_login_url('/')
          logout=users.create_logout_url('/')
          for data in blog_data:
              logging.debug(data.blob_key)
          template_value={'blog_data':blog_data,
                          'current_user':user,
                          'current_username':username,
                          'admin_status':admin_status,
                          'logout' : logout,
                          'login': login,
                          'date_list':self.get_month_count()
                          }
          path = os.path.join(os.path.dirname(__file__), 'pages/index.html')
          logging.debug('THE PATH!!')	
          logging.debug(path)
          self.response.out.write(template.render(path,template_value))
      except:
          exc_type, exc_value, exc_traceback = sys.exc_info()
          logging.debug('Error Occurred')
          logging.debug((traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2)))
          self.redirect('/error')

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
      try:
	bloburl=blobstore.create_upload_url('/save')
	logout = users.create_logout_url('/')
	template_value={'logout':logout,
			'bloburl':bloburl
			}
	user=users.get_current_user()
	if user:
		logging.debug('User login done')
		if users.is_current_user_admin():
			logging.debug('User is a admin')
			path = os.path.join(os.path.dirname(__file__), 'pages/admin_dash.html')
        		self.response.out.write(template.render(path,template_value))
		else:
			self.redirect('/error')
	else:
		logging.debug('User not found..Login please')
		self.redirect(users.create_login_url(self.request.uri))
      except:
          exc_type, exc_value, exc_traceback = sys.exc_info()
          logging.debug('Error Occurred')
          logging.debug((traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2)))
          self.redirect('/error')


class SavePost(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
      try:
        upload_files=self.get_uploads('file')
        if (upload_files):
            blob_info=upload_files[0]
            blob_key=blob_info.key()
            logging.debug('Blob Key')
            logging.debug(blob_key)
        else:
            blob_key="None"
	user = users.get_current_user()
	blogdata = BlogData()
  	blogdata.author = user.nickname()
	logging.debug('Author:'+blogdata.author)
        blogdata.title=self.request.get('title')
   	blogdata.content = self.request.get('content')
    	logging.debug('Content:'+blogdata.content)
        blogdata.blob_key=str(blob_key)
        blogdata.put()
	self.redirect('/')
      except:
          exc_type, exc_value, exc_traceback = sys.exc_info()
          logging.debug('Error Occurred')
          logging.debug((traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2)))
          self.redirect('/error')


class MonthArchive(webapp.RequestHandler):
  def get(self,year,month):
      try:
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
      except:
          exc_type, exc_value, exc_traceback = sys.exc_info()
          logging.debug('Error Occurred')
          logging.debug((traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2)))
          self.redirect('/error')

class EditPost(webapp.RequestHandler):
  def get(self,postid):
      try:
        logging.debug('In EditPost')
        logging.debug(int(postid))
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

        #user=users.get_current_user()
	if user_status:
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
      except:
          exc_type, exc_value, exc_traceback = sys.exc_info()
          logging.debug('Error Occurred')
          logging.debug((traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2)))
          self.redirect('/error')

class SaveEditPost(webapp.RequestHandler):
    def post(self):
        try:
            postid=int(self.request.get('postid'))
            bd=BlogData.get_by_id(postid)
            bd.title=self.request.get('title')
            bd.content=self.request.get('content')
            bd.put()
            self.redirect('/')
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.debug('Error Occurred')
            logging.debug((traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2)))
            self.redirect('/error')

class ShowImg(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self,resource):
        try:
            resource=str(urllib.unquote(resource))
            blob_info=blobstore.BlobInfo.get(resource)
            self.send_blob(blob_info)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.debug('Error Occurred')
            logging.debug((traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2)))
            self.redirect('/error')

class DeletePost(webapp.RequestHandler):
    def get(self,postid):
        try:
            blog_data = BlogData.all()
            start_cursor=memcache.get('blogdata_start_cursor')
            end_cursor=memcache.get('blogdata_end_cursor')
            if start_cursor:
                blog_data.with_cursor(start_cursor=start_cursor)
            if end_cursor:
                blog_data.with_cursor(end_cursor=end_cursor)
            for data in blog_data:
                if(data.key().id()==int(postid)):
                    if (data.blob_key != "None"):
                        blob_info=blobstore.BlobInfo.get(data.blob_key)
                        blob_info.delete()
                        data.delete()
            self.redirect('/')
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.debug('Error Occurred')
            logging.debug((traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2)))
            self.redirect('/error')

class DeleteImgHandler(webapp.RequestHandler):
    def get(self,postid):
        try:
            blog_data = BlogData.all()
            start_cursor=memcache.get('blogdata_start_cursor')
            end_cursor=memcache.get('blogdata_end_cursor')
            if start_cursor:
                blog_data.with_cursor(start_cursor=start_cursor)
            if end_cursor:
                blog_data.with_cursor(end_cursor=end_cursor)
            for data in blog_data:
                if(data.key().id()==int(postid)):
                    if (data.blob_key != "None"):
                        blob_info=blobstore.BlobInfo.get(data.blob_key)
                        blob_info.delete()
                        data.blob_key="None"
                        data.put()
                        logging.debug("Blob key : "+data.blob_key)
                        mod_title=data.title
                        mod_content=data.content
            user_status=users.get_current_user()
            admin_status=users.is_current_user_admin()
            bloburl=blobstore.create_upload_url('/imgresave')
            template_value={'postid':postid,
                            'user_status':user_status,
                            'admin_status':admin_status,
                            'mod_title':mod_title,
                            'mod_content':mod_content,
                            'bloburl':bloburl
                            }
            if user_status:
		logging.debug('User login done')
		if users.is_current_user_admin():
                    logging.debug('User is a admin')
                    path = os.path.join(os.path.dirname(__file__), 'pages/img_edit.html')
                    self.response.out.write(template.render(path,template_value))
		else:
                    self.redirect('/') #needs to be changed to a static non admin error page
            else:
		logging.debug('User not found..Login please')
		self.redirect(users.create_login_url(self.request.uri))
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.debug('Error Occurred')
            logging.debug((traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2)))
            self.redirect('/error')
class ResaveImgHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
      try:
        upload_files=self.get_uploads('file')
        if (upload_files):
            blob_info=upload_files[0]
            blob_key=blob_info.key()
            logging.debug('Blob Key')
            logging.debug(blob_key)
        else:
            blob_key="None"
	postid=int(self.request.get('postid'))
        bd=BlogData.get_by_id(postid)
        bd.blob_key=str(blob_key)
        bd.put()
        self.redirect('/')
      except:
          exc_type, exc_value, exc_traceback = sys.exc_info()
          logging.debug('Error Occurred')
          logging.debug((traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2)))
          self.redirect('/error')


application = webapp.WSGIApplication([
  ('/', IndexPage),
  ('/admin',AdminDash),
  ('/save',SavePost),
  ('/date/(\d\d\d\d)-(\d\d)/?$',MonthArchive),
  ('/edit/([\w]*)/?$',EditPost),
  ('/editsave',SaveEditPost),
  ('/showimg/([^/]+)?', ShowImg),
  ('/deletepost/([\w]*)/?$', DeletePost),
  ('/deleteimg/([\w]*)/?$', DeleteImgHandler),
  ('/imgresave', ResaveImgHandler)
], debug=True)



def main():
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
