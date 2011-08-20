import logging
import os

from google.appengine.api import users
from django.utils import simplejson
#from tipfy import RequestHandler, Response
#from tipfy.auth import UserRequiredIfAuthenticatedMiddleware
#from tipfy.sessions import SessionMiddleware
#from tipfy.json import json_encode, json_decode
#from tipfy.utils import render_json_response


#import markdown2
import urllib
import sys
import traceback

import webapp2
from webapp2_extras import jinja2

from utils import safe_int
from google.appengine.api import mail


def linebreaker(value):
    escaped_lines = []
    for line in value.split('\n'):
        escaped_lines.append(jinja2.escape(line))
    escaped = "<br/>".join(escaped_lines)
    # mark as safe
    return jinja2.Markup(escaped)

def urlquote(text):
    """
    convert text to be url safe text
    """
    if text:
        return urllib.quote(text)
    return ""


def pluralize(text, value):
    count = safe_int(value)
    if count>1:
        return "%ss"%text
    return text


def dt_strftime(dt, format):
    if dt and format:
        return dt.strftime(format)


def jinja_helpers_env(env):
    """
    register our helpers to jinja environment
    """
    env.globals['linebreak']=linebreaker
    env.globals['urlquote']=urlquote
    env.globals['pluralize']=pluralize
    env.globals['strftime']=dt_strftime


# ----- Handlers -----

class BaseHandler(webapp2.RequestHandler):

    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app)


    def render_response(self, _template, **context):
        # Renders a template and writes the result to the response.
        self.context_processor(context)
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)

    def handle_exception(self, exception, debug):

        app_config = self.config["app"]

        if debug: # debug_mode:
            return super(BaseHandler, self).handle_exception(exception, debug)
        else:
            logging.exception(exception)
            # self.error(500)
            # self.response.out.write(template.render('templdir/error.html', {}))

            lines = ''.join(traceback.format_exception(*sys.exc_info()))
            logging.error(lines)

            mail.send_mail_to_admins(sender=app_config["admin_email"],
                                 subject='Caught Exception',
                                 body=lines)

            self.context_processor(self.context)
            return self.render_response('error_handlers/500.html', **self.context)

    def context_processor(self, context, forms=True):
        user = users.get_current_user()
        admin = users.is_current_user_admin()

        if user:
            context.update({
                'user': user,
                'admin': admin,
                'logout_url': users.create_logout_url("/"),
                })
        else:
            context.update({
                'user': None,
                'login_url': users.create_login_url(self.request.url),
                })

        return None


