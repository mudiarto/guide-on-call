# -*- coding: utf-8 -*-
"""URL definitions."""

#
# combine all routes here
#
routes = []

from apps.home.urls import routes as home_routes
routes.extend(home_routes)

from apps.guide.urls import routes as guide_routes
routes.extend(guide_routes)


