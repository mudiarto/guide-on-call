# -*- coding: utf-8 -*-
"""URL definitions."""
from webapp2 import Route


routes = [
    Route(r'/', handler='apps.home.handlers.HomeHandler', name='home'),
]


