# -*- coding: utf-8 -*-
"""WSGI app setup."""
import os
import sys
import logging
import traceback


from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext import ereporter
ereporter.register_logger()

from google.appengine.api import mail

cd = os.path.abspath(os.path.dirname(__file__))
import set_sys_path # will initialize the path, do not remove


import webapp2
from webapp2_extras import jinja2

from config import config
from urls import routes

# Is this the development server?
debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

# Instantiate the application.
app = webapp2.WSGIApplication(routes=routes, config=config, debug=debug)
app_config = config["app"]

def get_jinja2():
    return jinja2.get_jinja2(app=app)

def enable_jinja2_debugging():
    """Enables blacklisted modules that help Jinja2 debugging."""
    if not debug:
        return

    # This enables better debugging info for errors in Jinja2 templates.
    from google.appengine.tools.dev_appserver import HardenedModulesHook
    HardenedModulesHook._WHITE_LIST_C_MODULES += ['_ctypes', 'gestalt']


def handle_403(request, response, exception):
    logging.exception(exception)
    #self.context_processor(self.context, forms=False)
    return response.write(get_jinja2().render_template('error_handlers/403.html'))

def handle_404(request, response, exception):
    logging.exception(exception)
    #self.context_processor(self.context, forms=False)
    return response.write(get_jinja2().render_template('error_handlers/404.html'))

def handle_500(request, response, exception):
    logging.exception(exception)

    lines = ''.join(traceback.format_exception(*sys.exc_info()))
    #logging.error(lines)
    mail.send_mail_to_admins(sender=app_config["admin_email"],
                         subject='Caught Exception',
                         body=lines)

    return response.write(get_jinja2().render_template('error_handlers/500.html'))


# initialize the app
enable_jinja2_debugging()

app.error_handlers[403] = handle_403
app.error_handlers[404] = handle_404
app.error_handlers[405] = handle_500


def main():
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    set_sys_path.set_path()

    # Run the app.
    app.run()


if __name__ == '__main__':
    main()


