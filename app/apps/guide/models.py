"""
    Project Model

    there are multiple languages defined in the system

    user can upload multiple documents
        - each documents can have different translation


    there is one "general" document that should be translated to all languages
    that contain translation for all general instruction, etc


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
    def get_by_number(cls, number):
        return cls.all().filter('number =', number).get()


    def get_original(self, number):
        """
            get text with specific number
        """
        return Original.all().ancestor(self).filter('number =', number).get()


class Language(db.Model):
    """
        Language description
        parent -> None
        key -> lang (language short code)
    """
    # lang = db.StringProperty(required=True) # will be used as key_name
    language = db.StringProperty(required=True) # language name -> English, Spanish
    phone_number = db.StringProperty() # a phone number used to reach this translation
    description = db.TextProperty() # language description (optional)

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


