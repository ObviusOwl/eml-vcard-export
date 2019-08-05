from ..value import vValue, vTextValue, vBinaryValue
from ..parameter import vParameterList, vParameter

from .attribute import vAttribute, vAttributeType

class vAbstractTextAttr( vAttribute ):
    # abstract class implementing an attribute-type with a single text value

    # class attribute storing the decoded value
    _value_class_attr_name = 'text'
    
    def __init__(self):
        text_value = vTextValue( "" )
        self.__setattr__( self._value_class_attr_name, text_value )
        super().__init__()

    def encode_value(self):
        text_value = getattr(self, self._value_class_attr_name )
        return text_value.escape()

    def decode_value(self, value):
        self._value = vTextValue( value )
        text_value = self._value.unescape()
        setattr( self, self._value_class_attr_name, text_value )

class vAbstractTextListAttr( vAttribute ):
    # abstract class implementing an attribute-type with a single text list value

    # class attribute storing the decoded value list
    _value_class_attr_name = 'text'
    
    def __init__(self):
        self.__setattr__( self._value_class_attr_name, [] )
        super().__init__()

    def encode_value(self):
        text_value_list = getattr(self, self._value_class_attr_name )
        str_value_list = [ str(c.escape()) for c in text_value_list ]
        return vTextValue(',').join( str_value_list )

    def decode_value(self, value):
        self._value = vTextValue( value )
        text_value_list = self._value.escaped_split( ',', unescape_parts=True )
        setattr( self, self._value_class_attr_name, text_value_list )

class vAbstractStructTextAttr( vAttribute ):
    # abstract class for structured text attributes: 
    # a list of components (lists of text-value) with fixed semantic 

    # list of class attribute names. The order corresponds to the semantic 
    # defined in the RFCs
    _component_order = ( )

    def __init__(self):
        for prop_name in self._component_order:
            setattr(self, prop_name, [] )
        super().__init__()

    def encode_value(self):
        struct_str_list = []
        for prop_name in self._component_order:
            text_value_list = getattr( self, prop_name )
            str_value_list = [ str(c.escape()) for c in text_value_list ]
            struct_str_list.append( ','.join(str_value_list) )
        return vTextValue(';').join( struct_str_list )

    def decode_value(self, value):
        self._value = vTextValue( value )
        struct = self._value.escaped_split( ';' )
        len_diff = len( self._component_order ) - len( struct )
        if len_diff > 0:
            struct.extend( [ vTextValue("") for i in range(len_diff) ] )

        for i in range( len(self._component_order) ):
            text_value_list = struct[ i ].escaped_split( ',', unescape_parts=True )
            setattr( self, self._component_order[i], text_value_list )

class vAbstractBinaryUriAttr( vAttribute ):
    # abstract class implementing a binary value type with inline or url content
    
    def __init__(self):
        super().__init__()
        self._uri = vValue( '' )
        self._data = vBinaryValue( b'' )

    @property
    def has_uri(self):
        value_param = self._params.get( 'value', default=vParameter() )
        return value_param.has_value( 'uri', ignorecase=True )

    @property
    def uri(self):
        return self._uri

    @uri.setter
    def uri(self, uri):
        self._params.set( 'value', 'uri' )
        self._uri = vValue( uri )
    
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        del self.params['value']
        self._params.set( 'encoding', 'b' )
        self._data = vBinaryValue( data )
    
    def encode_value(self):
        if self.has_uri:
            return vValue( self._uri )
        return vBinaryValue( self._data )

    def decode_value(self, value):
        if self.has_uri:
            self._value = vValue( value )
            self._uri = self._value
            self._data = vBinaryValue( b'' )
        else:
            self._value = vBinaryValue( value )
            self._uri = vValue( '' )
            self._data = self._value
            self._params.set( 'encoding', 'b' )
