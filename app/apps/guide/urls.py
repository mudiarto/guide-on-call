# -*- coding: utf-8 -*-
"""URL definitions."""
from webapp2 import Route


routes = [
    Route(r'/manage', handler='apps.guide.handlers.ManageHandler', name='manage'),
    Route(r'/doc', handler='apps.guide.handlers.DocListHandler', name='doc_list'),
    Route(r'/doc/new', handler='apps.guide.handlers.DocNewHandler', name='doc_new'),
    Route(r'/doc/edit/<doc_id:\d+>', handler='apps.guide.handlers.DocEditHandler', name='doc_edit'),
    Route(r'/doc/delete/<doc_id>', handler='apps.guide.handlers.DocDeleteHandler', name='doc_delete'),
    Route(r'/doc/view/<doc_id>', handler='apps.guide.handlers.DocReadHandler', name='doc_view'),


    Route(r'/lang', handler='apps.guide.handlers.LangHandler', name='lang_list'),
    Route(r'/lang/new', handler='apps.guide.handlers.LangNewHandler', name='lang_new'),

    Route(r'/guide/<doc_id>', handler='apps.guide.handlers.GuideHandler', name='guide'),
    Route(r'/guide/<doc_id>/new', handler='apps.guide.handlers.DocEditHandler', name='guide'),
    Route(r'/guide/<doc_id>/update/<guide_id>', handler='apps.guide.handlers.DocEditHandler', name='guide'),
    Route(r'/guide/<doc_id>/delete/<guide_id>', handler='apps.guide.handlers.DocDeleteHandler', name='doc_delete'),


    # return language lookup
    # Route(r'/api/v1/lang/<lang_code>', handler='apps.guide.handlers.LanguageLookupHandler', name='lang_lookup'),

]


