from .lexer import vcard_fold_line

class vCardError( Exception ):
    pass


class vName( object ):
    def __init__(self, value):
        self.value = str(value)
    
    def __str__(self):
        return self.value

    def __eq__(self, other):
        return str(self).casefold() == str(other).casefold()

    def __add__(self, other):
        return vName( str(self)+str(other) )


class vCard( object ):

    def __init__(self):
        # storing attributes in a list to preserve original order
        self.attrs = []
    
    def find_attr(self, name):
        pass
    
    def append_attr(self, attr):
        self.attrs.append( attr )
    
    def __str__(self):
        return self.serialize()
    
    def serialize(self, original_values=False, line_length=75):
        lines = []
        for attr in self.attrs:
            line = attr.serialize( original_value=original_values ) 
            line = vcard_fold_line( line, line_length=line_length )
        return '\n'.join( lines )
