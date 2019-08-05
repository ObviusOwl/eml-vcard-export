from .base import vAbstractTextAttr

class vSourceAttribute( vAbstractTextAttr ):
    # RFC2425 section 6.1
    registered_names = ( 'source', )
    _value_class_attr_name = 'source'

class vProfileAttribute( vAbstractTextAttr ):
    # RFC2425 section 6.3
    registered_names = ( 'profile', )
    _value_class_attr_name = 'profile'
