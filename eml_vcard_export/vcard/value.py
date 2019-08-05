import base64

class vValue( object ):
    # base class for value of concrete vAttribute 
    # and value implementation for unknwon attributes

    def __init__(self, value=""):
        self.value = str(value)

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return "<{}: '{}'>".format( self.__class__.__name__, self.value )

    def __eq__(self, other):
        return str(self) == str(other)

    def __add__(self, other):
        return vValue( str(self)+str(other) )

class vTextValue( vValue ):
    # the RFC's refer this value type as text-value and text-value-list
    
    def __init__(self, value=""):
        super().__init__( value )

    def __add__(self, other):
        return vTextValue( str(self)+str(other) )
    
    def escape(self):
        # Note the instruction order
        value = self.value.replace("\\", "\\\\")
        value = value.replace(";", "\;")
        value = value.replace(",", "\,")
        value = value.replace("\r\n", "\\n")
        value = value.replace("\n", "\\n")
        value = value.replace("\r", "\\n")
        return vTextValue( value )

    def unescape(self):
        # Note the instruction order
        value = self.value.replace("\\\\", "\\")
        value = value.replace("\;", ";")
        value = value.replace("\,", ",")
        value = value.replace("\\n", "\n")
        value = value.replace("\\N", "\n")
        return vTextValue( value )
    
    def escaped_split(self, delim_char, escape_char='\\', unescape_parts=False):
        if len(delim_char) != 1 or len(escape_char) != 1:
            raise ValueError( "delim_char and escape_char must be exactly one character long" )

        part_list = []
        def append_part( part ):
            if unescape_parts:
                part = part.unescape()
            part_list.append( part )
        
        # finite state machine
        prev, part = '', ""
        for curr in self.value:
            if prev != escape_char and curr == delim_char:
                append_part( vTextValue( part ) )
                part = ""
            else:
                prev = curr
                part += curr
        append_part( vTextValue( part ) )
        return part_list
    
    def join(self, value_list):
        str_value_list = [ str(c) for c in value_list ]
        return vTextValue( self.value.join( str_value_list ) )

class vBinaryValue( object ):
    # the RFC's refer this value type as "inline, encoded binary data"
    
    def __init__(self, data=b''):
        if isinstance(data, vBinaryValue):
            self.data = data.data
        else:
            if not hasattr( data, 'decode' ):
                raise TypeError( "data must be binary" )
            self.data = data
    
    @classmethod
    def from_base64(cls, value_str):
        value = cls()
        cls.data = base64.b64decode( value_str.encode("utf-8") )
        return value
    
    def to_base64(self):
        return base64.b64encode(self.data).decode("utf-8")
    
    def __str__(self):
        return self.to_base64()

    def __add__(self, other):
        if not isinstance( other, vBinaryValue ):
            return NotImplemented
        return vBinaryValue( self.data + other.data )
