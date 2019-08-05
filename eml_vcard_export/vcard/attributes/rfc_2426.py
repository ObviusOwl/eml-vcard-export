from ..value import vTextValue

from .base import *

class vImageAttribute( vAbstractBinaryUriAttr ):
    # RFC2426 section 3.1.4, RFC2426 section 3.5.3
    registered_names = ( 'photo', 'logo')

class vFnAttribute( vAbstractTextAttr ):
    # RFC2426 section 3.1.1
    registered_names = ( 'fn', )
    _value_class_attr_name = 'fn'

class vNameAttribute( vAbstractStructTextAttr ):
    # RFC2426 section 3.1.2
    registered_names = ( 'n', )
    _component_order = ( 'family_names', 'given_names', 'additional_names', 
                        'honorific_prefixes', 'honorific_suffixes' )

class vNicknameAttribute( vAbstractTextListAttr ):
    # RFC2426 section 3.1.3
    registered_names = ( 'nickname', )
    _value_class_attr_name = 'nicknames'

class vBdayAttribute( vAbstractTextAttr ):
    # RFC2426 section 3.1.5
    registered_names = ( 'bday', )
    _value_class_attr_name = 'birthday'

class vAdrAttribute( vAbstractStructTextAttr ):
    # RFC2426 section 3.2.1
    registered_names = ( 'adr', )
    _component_order = ( 'po_box', 'extended', 'street', 'locality',
                        'region', 'postal_code', 'country' )

class vLabelAttribute( vAbstractTextAttr ):
    # RFC2426 section 3.1.2
    registered_names = ( 'label', )
    _value_class_attr_name = 'label'

class vTelAttribute( vAbstractTextAttr ):
    # RFC2426 section 3.3.1
    registered_names = ( 'tel', )
    _value_class_attr_name = 'tel'

class vEmailAttribute( vAbstractTextAttr ):
    # RFC2426 section 3.3.2
    registered_names = ( 'email', )
    _value_class_attr_name = 'email'

class vMailerAttribute( vAbstractTextAttr ):
    # RFC2426 section 3.3.3
    registered_names = ( 'mailer', )
    _value_class_attr_name = 'mailer'

class vTzAttribute( vAbstractTextAttr ):
    # RFC2426 section 3.4.1
    registered_names = ( 'tz', )
    _value_class_attr_name = 'time_zone'

class vGeoAttribute( vAbstractStructTextAttr ):
    # RFC2426 section 3.4.2
    registered_names = ( 'geo', )
    _component_order = ( 'latitude', 'longitude' )

class vTitleAttribute( vAbstractTextAttr ):
    # RFC2426 section 3.5.1
    registered_names = ( 'title', )
    _value_class_attr_name = 'title'

class vRoleAttribute( vAbstractTextAttr ):
    # RFC2426 section 3.5.2
    registered_names = ( 'role', )
    _value_class_attr_name = 'role'

class vAgentAttribute( vAbstractTextAttr ):
    # RFC2426 section 3.5.4
    registered_names = ( 'agent', )
    _value_class_attr_name = 'agent'

class vOrgAttribute( vAttribute ):
    # RFC2426 section 3.5.5
    registered_names = ( 'org', )

    def __init__(self):
        self.organization = self.new_value( "" )
        self.divisions = []
        super().__init__()

    def new_value(self, value):
        return vTextValue( value )

    def encode_value(self):
        text_value_list = [ self.organization ]
        text_value_list.extend( self.divisions )
        struct_str_list = [ str(c.escape()) for c in text_value_list ]
        return vTextValue(';').join( struct_str_list )

    def decode_value(self, value):
        self._value = vTextValue( value )
        text_value_list = self._value.escaped_split( ';', unescape_parts=True )
        if len( text_value_list ) >= 1:
            self.organization = text_value_list.pop(0)
        self.divisions = text_value_list

class vCategoriesAttribute( vAbstractTextListAttr ):
    # RFC2426 section 3.6.1
    registered_names = ( 'categories', )
    _value_class_attr_name = 'categories'

class vNoteAttribute( vAbstractTextAttr ):
    # RFC2426 section 3.6.2
    registered_names = ( 'note', )
    _value_class_attr_name = 'note'

class vProdidAttribute( vAbstractTextAttr ):
    # RFC2426 section 3.6.3
    registered_names = ( 'prodid', )
    _value_class_attr_name = 'prodid'

class vRevAttribute( vAbstractTextAttr ):
    # RFC2426 section 3.6.4
    registered_names = ( 'rev', )
    _value_class_attr_name = 'rev'

class vSortstringAttribute( vAbstractTextAttr ):
    # RFC2426 section 3.6.5
    registered_names = ( 'sort-string', )
    _value_class_attr_name = 'sort_string'

class vSoundAttribute( vAbstractBinaryUriAttr ):
    # RFC2426 section 3.6.6
    registered_names = ( 'sound', )

class vUidAttribute( vAbstractTextAttr ):
    # RFC2426 section 3.6.7
    registered_names = ( 'uid', )
    _value_class_attr_name = 'uid'

class vUrlAttribute( vAbstractTextAttr ):
    # RFC2426 section 3.6.8
    registered_names = ( 'url', )
    _value_class_attr_name = 'url'

class vVersionAttribute( vAbstractTextAttr ):
    # RFC2426 section 3.6.9
    registered_names = ( 'version', )
    _value_class_attr_name = 'version'

class vClassAttribute( vAbstractTextAttr ):
    # RFC2426 section 3.7.1
    registered_names = ( 'class', )
    _value_class_attr_name = 'class'

# TODO key
# RFC2426 section 3.7.2
