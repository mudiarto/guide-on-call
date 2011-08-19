# -*- coding: utf-8 -*-
"""URL definitions."""
from webapp2 import Route


routes = [
    Route(r'/', handler='apps.home.handlers.HomeHandler', name='home'),
    Route(r'/<template>.html', handler='apps.home.handlers.HomeFlatpageHandler', name='flatpage'),
    Route(r'/protected/<template>.html', handler='apps.home.handlers.HomeProtectedFlatpageHandler', name='protected_flatpage'),
]


