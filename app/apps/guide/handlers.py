from apps.base.handlers import BaseHandler
import logging

from webapp2_extras.appengine.users import login_required

class HomeHandler(BaseHandler):
    def get(self, **kwargs):
        self.response.write('This is the HomeHandler.')

class HomeFlatpageHandler(BaseHandler):
    def get(self, template, **kwargs):
        return self.render_response('%s.html'%template, **kwargs)

    def handle_exception(self, exception, debug=False):
        # for flatpage, if we can't find the file, just throw 404
        self.abort(404)

class HomeProtectedFlatpageHandler(BaseHandler):
    @login_required
    def get(self, template, **kwargs):
        return self.render_response('%s.html'%template, **kwargs)

    def handle_exception(self, exception, debug=False):
        # for flatpage, if we can't find the file, just throw 404
        self.abort(404)



class ExceptionTestHandler(BaseHandler):
    def get(self, template, **kwargs):
        raise(Exception)
        return self.render_response('home/%s.html'%template, **kwargs)



