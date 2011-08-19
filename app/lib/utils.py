import uuid
import re

def base36encode(number, alphabet='0123456789abcdefghijklmnopqrstuvwxyz'):
    '''
    Convert positive integer to a base36 string.
    '''
    if not isinstance(number, (int, long)):
        raise TypeError('number must be an integer')
    if number < 0:
        raise ValueError('number must be nonnegative')

    # Special case for zero
    if number == 0:
        return '0'

    base36 = ''
    while number != 0:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36

    return base36

def base36decode(number):
    return int(number, 36)

def uuid36():
    return base36encode(uuid.uuid4().int)

def safe_int(value, default=0):
    """
    convert to int safely
    """
    try:
        return int(value)
    except ValueError:
        return default

def safe_float(value, default=0.0):
    """
    convert to float safely
    """
    try:
        return float(value)
    except ValueError:
        return default

def xfrange(start, stop, step):
    """
    a generator to create ranged item, can be float / double, etc
    """
    while start < stop:
        yield start
        start += step

def uniqify(seq, idfun=None):
    """
    uniqify an array
    """
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result


def get_key(model, prop_name):
    """
        get a raw key from a appengine.ext.db.ReferenceProperty
        normally if we refer to RefProperty, it will transparently retrieve the object
        if we want to get the key, without retrieving the object, use this 
    """
    return getattr(model.__class__, prop_name).get_value_for_datastore(model)


#######################
#
# Create slugs, derived from django's JS implementation
# http://djangosnippets.org/snippets/29/
#
# name = "This IS A boOk's TiTle"
# slug = slugify(name)
#
# >>> print slug
# 'this-is-a-books-title'
#
#######################

def slugify(inStr):
    removelist = ["a", "an", "as", "at", "before", "but", "by", "for","from","is", "in", "into", "like", "of", "off", "on", "onto","per","since", "than", "the", "this", "that", "to", "up", "via","with"];
    for a in removelist:
        aslug = re.sub(r'\b'+a+r'\b','',inStr)
    aslug = re.sub('[^\w\s-]', '', aslug).strip().lower()
    aslug = re.sub('\s+', '-', aslug)
    return aslug
