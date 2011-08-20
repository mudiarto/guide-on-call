from __future__ import with_statement 
import unittest2 as unittest
#from google.appengine.api import memcache
#from google.appengine.ext import db
from google.appengine.ext import testbed

#from apps.user.models import User
#from apps.project.models import Project, ProjectShareRequest
#from apps.program.models import Program

from apps.guide.models import *

class ProjectTestCase(unittest.TestCase):

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        # create a new user for testing
        #self.user = User.create("user@5000hands.com", "own|user@5000hands.com", fullname="user")


    def tearDown(self):
        self.testbed.deactivate()


    def testDocument(self):

        # test regular create
        doc = Document.create(number=1, lang="en", title="Hello World 1" )
        self.assertIsNotNone(doc)

        # test regular create
        doc = Document.create(number=2, lang="en", title="Hello World 2" )
        self.assertIsNotNone(doc)
        doc.put()


        # test duplicate
        self.assertRaises(UniqueConstraintViolation, Document.create, number=1, lang="en", title="conflict")

        # test get_by_number
        doc = Document.get_by_number(1)
        self.assertIsNotNone(doc)


        # test add & remove translation
        Document.add_translation(doc, 'en')
        Document.add_translation(doc, 'es')
        doc = Document.get_by_number(1)
        self.assertEqual(len(doc.translations), 2)


        Document.remove_translation(doc, 'es')
        doc = Document.get_by_number(1)
        self.assertEqual(len(doc.translations), 1)



    def testOriginal(self):

        # test regular create
        doc = Document.create(number=1, lang="en", title="Hello World 1" )
        self.assertIsNotNone(doc)

        orig = Original.create(doc, number=1, text='a quick brown fox', description='a quickish and brownish vulpes vulpes')
        self.assertIsNotNone(orig)

        # test get_by_number
        orig = doc.get_original(1)
        self.assertIsNotNone(orig)


    def testTranslation(self):


        # test regular create
        doc = Document.create(number=1, lang="en", title="Hello World 1" )
        self.assertIsNotNone(doc)

        orig = Original.create(doc, number=1, text='a quick brown fox', description='a quickish and brownish vulpes vulpes')
        self.assertIsNotNone(orig)

        translation = Translation.create(orig, 'id', translation='seekor serigala coklat yang cepat')
        self.assertIsNotNone(translation)

        # test duplicate
        self.assertRaises(ValueError, Translation.create, orig, 'id',  translation='seekor serigala coklat yang cepat')

        # test get
        translation = orig.get_translation("id")
        self.assertIsNotNone(translation)


    def testDocumentTranslation(self):

        # setup - create doc
        doc = Document.create(number=1, lang="en", title="Hello World 1" )
        self.assertIsNotNone(doc)

        # register translation
        language = Language.create("id", language="indonesian")
        doc_translate = DocumentTranslation.create(doc, "id")

        # setup translation
        orig = Original.create(doc, number=1, text='a quick brown fox', description='a quickish and brownish vulpes vulpes')
        translation = Translation.create(orig, 'id', translation='seekor serigala coklat yang cepat')

        # publish translation
        doc_translate.publish()

        # test
        published = doc.get_published()
        self.assertEqual(len(published), 1)

        available = language.translation_available(doc)
        self.assertTrue(available)

        documents = language.get_documents()
        self.assertEqual(len(documents), 1)

        # unpublish translation
        doc_translate.unpublish()

        # test
        published = doc.get_published()
        self.assertEqual(len(published), 0)

        available = language.translation_available(doc)
        self.assertFalse(available)

        documents = language.get_documents()
        self.assertEqual(len(documents), 0)



