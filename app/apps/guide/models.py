"""
    Project Model

    there are multiple languages defined in the system

    user can upload multiple documents
        - each documents can have different translation


    there is one "general" document that should be translated to all languages
    that contain translation for all general instruction, etc



    language short code is based on : http://www.loc.gov/standards/iso639-2/php/code_list.php


"""

from google.appengine.ext import db
from google.appengine.ext.blobstore import blobstore


class UniqueConstraintViolation(Exception):
  def __init__(self, scope, value):
    super(UniqueConstraintViolation, self).__init__("'%s' already registered in the system" % (value))


class Unique(db.Model):
    """
        a table to make sure there are no duplicate key + value in the system
        this is a root element, with key is the id you want to check
    """

    @classmethod
    def exists(cls, scope, value):
        """
            return true if value already exists within specified scope exists else false
        """
        key_name = str(scope)+":"+str(value)
        return (Unique.get_by_key_name(key_name) is not None)

    @classmethod
    def check_and_create(cls, scope, value):
        """
            check key and value, if not exists, create one
            run inside transaction to guarantee that no transaction slip between these 2 operation
            will raise UniqueConstraintViolation on duplicate email
        """
        key_name = str(scope)+":"+str(value)
        def tx(key_name):
            unique = Unique.get_by_key_name(key_name)
            if unique:
                raise UniqueConstraintViolation(scope, value)
            unique = Unique(key_name=key_name)
            unique.put()
            return unique
        return db.run_in_transaction(tx, key_name)

    @classmethod
    def remove(cls, scope, value):
        key_name = str(scope)+":"+str(value)
        def tx(key_name):
            unique = Unique.get_by_key_name(key_name)
            if not unique:
                raise KeyError("Cannot find '%s'"%key_name)
            unique.delete()
        return db.run_in_transaction(tx, key_name)




class Document(db.Model):
    """
        no parent
        auto generated key
    """

    # contain document number that will be accessible by phone
    # should be between -9223372036854775808 < x < 9223372036854775807
    # 18 digits ought to be enough for everyone :)
    number = db.IntegerProperty(required=True)

    # document language code, can be used for TTS(text-to-speech)
    lang = db.StringProperty(required=True)

    # document code, ex: W-4, I-765, etc
    code = db.StringProperty()

    # document title, ex: Tax Form, etc
    title = db.StringProperty(required=True)

    # title recording, if none, will use TTS
    title_speech = blobstore.BlobReferenceProperty()

    # additional description for specific recording
    description = db.StringProperty(multiline=True)

    #recording of the description, if none, will use TTS
    description_speech = blobstore.BlobReferenceProperty()

    # tts configuration
    # none for now

    # cache for available languages, when a translation is published, it should update this list as well
    translations = db.StringListProperty()


    @classmethod
    def create(cls, **kwargs):
        number = kwargs.get('number', None)
        lang = kwargs.get('lang')
        title = kwargs.get('title')

        if number is None:
            raise ValueError("required field(number) missing")

        Unique.check_and_create('Document', number)

        # if we get to this point, it means the number is ok, we can use it
        def txn():
            doc = Document(**kwargs)
            doc.put()
            return doc

        return db.run_in_transaction_custom_retries(3, txn)

    @classmethod
    def add_translation(cls, doc, lang_code):

       def txn():
            new_doc = Document.get(doc.key())
            new_doc.translations.append(lang_code)
            new_doc.put()
            return new_doc

       return db.run_in_transaction_custom_retries(3, txn)

    @classmethod
    def remove_translation(cls, doc, lang_code):

       def txn():
            new_doc = Document.get(doc.key())
            try:
                new_doc.translations.remove(lang_code)
                new_doc.put()
            except:
                pass # do nothing on error
            return new_doc

       return db.run_in_transaction_custom_retries(3, txn)

    @classmethod
    def fetch(cls, n=1000):
        return cls.all().fetch(n)


    @classmethod
    def get_by_number(cls, number):
        return cls.all().filter('number =', number).get()


    def get_published(self, n=1000):
        """
            get published document translation
        """
        return DocumentTranslation.all().ancestor(self).filter('status =', DocumentTranslation.PUBLISHED).fetch(n)


    def get_original(self, number):
        """
            get text with specific number
        """
        return Original.all().ancestor(self).filter('number =', number).get()


class Language(db.Model):
    """
        Language description
        parent -> None
        key -> lang (language short code), based on ISO_639-1 / 639-2 code
    """
    # lang = db.StringProperty(required=True) # will be used as key_name
    language = db.StringProperty(required=True) # language name -> English, Spanish
    phone = db.StringProperty() # a phone number used to reach this translation
    description = db.TextProperty() # language description (optional)

    @property 
    def lang(self):
        return self.key().name()

    @classmethod
    def create(cls, lang_code, **kwargs):

        if not lang_code:
            raise ValueError("required field(lang) missing")

        Unique.check_and_create('Language', lang_code)

        # if we get to this point, it means the number is ok, we can use it
        def txn():
            language = Language(key_name=lang_code, **kwargs)
            language.put()
            return language

        return db.run_in_transaction_custom_retries(3, txn)

    @classmethod
    def get_by_code(cls, lang_code):
        key = db.Key.from_path('Language', lang_code)
        return Language.get(key)

    def translation_available(self, document, n=1000):
        """
            check if translation available for a document
            return DocumentTranslation if available, else None
        """
        key = db.Key.from_path("DocumentTranslation", self.lang, parent=document.key())
        doc_translation = DocumentTranslation.get(key)
        return doc_translation is not None and doc_translation.status == DocumentTranslation.PUBLISHED

    def get_documents(self, n=1000):
        """
            get documents available for this language
        """
        keys = DocumentTranslation.all(keys_only=True).filter('status =', DocumentTranslation.PUBLISHED).filter('lang =', self.key().name()).fetch(n)
        doc_keys = [key.parent() for key in keys]
        return Document.get(doc_keys)

    def to_dict(self):
        result = {
                "lang": self.lang,
                "language": self.language,
                "phone": self.phone,
        }
        return result




class DocumentTranslation(db.Model):
    """
        This model is used to keep track of what translation available for specific documents

        parent: document
        key: lang (language short code)
    """
    DRAFT = 0
    PUBLISHED = 1

    status = db.IntegerProperty(default=DRAFT) # status of translation-> 0:draft 1:published, only published translation / guide is shown
    lang = db.StringProperty(required=True) # lang code, just in case we need to query per language
    # root_lang = db.StringProperty()  # FUTURE: root language. Example, us-en root is en. Used in case we can't find a translation for specific text, we can get it from their root language
    # note = db.TextProperty()  # FUTURE: translator note


    @classmethod
    def create(cls, document, lang_code, **kwargs):

        if not lang_code:
            raise ValueError("required field(lang_code) missing")

        def txn():
            doc_translation = DocumentTranslation(key_name=lang_code, parent=document.key(), lang=lang_code, **kwargs)
            doc_translation.put()
            return doc_translation 

        return db.run_in_transaction_custom_retries(3, txn)


    @classmethod
    def get_published_keys(cls, n=1000):
        """
            get keys for all published translation for all documents.
            based on the key, we can construct which documents available for which languages
            TODO: can be put in memcached later, since this value should not change too much, and only changed when
                there is new document or new translation published
        """

        return DocumentTranslation.all(keys_only=True).filter('status =', DocumentTranslation.PUBLISHED).fetch(n)

    def publish(self):
        doc = self.parent()

        if self.status == self.DRAFT:
            Document.add_translation(doc, self.lang)
            self.status = self.PUBLISHED
            self.put()
            return True
        return False

    def unpublish(self):
        doc = self.parent()

        if self.status == self.PUBLISHED:
            Document.remove_translation(doc, self.lang)
            self.status = self.DRAFT
            self.put()
            return True
        return False






class Original(db.Model):
    """
        original text, no translation

        parent -> Document
        auto generated key

        language is based on the document language code
    """

    number = db.IntegerProperty(required=True)
    text = db.TextProperty(required=True)
    description = db.TextProperty() # a more thorough description of the text, maybe good for translator

    @classmethod
    def create(cls, document, **kwargs):
        number = kwargs.get('number')
        text = kwargs.get('text')

        if document is None or number is None or not text:
            raise ValueError("required field(s) missing")

        # if we get to this point, it means the number is ok, we can use it
        def txn():
            original = Original(parent=document, **kwargs)
            original.put()
            return original

        return db.run_in_transaction_custom_retries(3, txn)

    def get_translation(self, lang_code):
        """
            get translation
            lang is the short language code
        """
        key = db.Key.from_path("Translation", lang_code, parent=self.key())
        return Translation.get(key)


class Translation(db.Model):
    """
        Guide for specific document

        parent -> Original
        key -> Language.key().id()

    """

    auto_translation = db.BooleanProperty() # if true, means this is translated using automated tool (google translate, etc)
    translation = db.TextProperty(required=True)

    auto_translation_speech = db.BooleanProperty() # if it is true, the translation speech is done using automated tool (googl translate, etc)
    translation_speech = blobstore.BlobReferenceProperty() # recording of the translation, if none, will use TTS

    @classmethod
    def create(cls, original, lang_code, **kwargs):

        if not original or not lang_code:
            raise ValueError("required field(s) missing")

        # if we get to this point, it means the number is ok, we can use it
        def txn():
            if original.get_translation(lang_code):
                raise ValueError("Document already contain this translation")
            translation = Translation(parent=original.key(), key_name=lang_code, **kwargs)
            translation.put()
            return translation

        return db.run_in_transaction_custom_retries(3, txn)


