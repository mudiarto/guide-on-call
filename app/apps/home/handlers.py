from apps.base.handlers import BaseHandler
import logging

from webapp2_extras.appengine.users import login_required
from google.appengine.api import users

class HomeHandler(BaseHandler):
    def get(self, **kwargs):

        # get all documents
        # get all available translations
        context = {

        }

        return self.render_response('index.html', **kwargs)


class ExceptionTestHandler(BaseHandler):
    def get(self, template, **kwargs):
        raise(Exception)
        return self.render_response('home/%s.html'%template, **kwargs)



