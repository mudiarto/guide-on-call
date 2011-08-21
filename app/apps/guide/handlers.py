from apps.base.handlers import BaseHandler
import logging

from apps.guide.models import Language

from webapp2_extras.appengine.users import login_required

class ManageHandler(BaseHandler):
    def get(self, **kwargs):
        return self.render_response('manage.html', **kwargs)

class LanguageLookupHandler(BaseHandler):
    @login_required
    def get(self, lang, **kwargs):
        language = Language.get_by_code(lang)
        if language:
            self.render_json_response(language.to_dict())
        self.abort(404)


class ExceptionTestHandler(BaseHandler):
    def get(self, template, **kwargs):
        raise(Exception)
        return self.render_response('home/%s.html'%template, **kwargs)



