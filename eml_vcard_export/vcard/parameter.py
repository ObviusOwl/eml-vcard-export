import re

from .common import vCardError, vName

class vParameterValue( object ):
    def __init__(self, value, force_quote=None):
        if force_quote is None:
            # preserve quoting if string is quoted, even if not strictly needed
            self.force_quote = '"' in value
        else:
            self.force_quote = force_quote

        # double unquote is safe, since no quotes allowed in raw value
        self.value = self.unquote(value)
        self._check_value( self.value )

    @staticmethod
    def _check_value(value):
        if '"' in value:
            raise ValueError( "No '\"' allowed in parameter values" )

    @staticmethod
    def quote(value, force=False):
        vParameterValue._check_value( value )
        if force or re.search( "[;:,]", value ) is not None:
            return '"' + value + '"'
        return value

    @staticmethod
    def unquote(value):
        return value.strip('"')

    def __str__(self):
        return self.value

    def __add__(self, other):
        return vParameterValue( str(self)+str(other) )
    
    def __eq__(self, other):
        # MAY be case sensitive or insensitive depending on thier definition
        return str(self) == str(other)
    
    def as_quote(self, force_quote=None):
        if force_quote is None:
            force_quote = self.force_quote
        return self.quote( self.value, force=force_quote )
    
    def serialize(self):
        return self.quote( self.value, force=self.force_quote )
        

class vParameter( object ):
    def __init__(self, name="", values=None ):
        if values is None:
            values = []
        self.values = [ vParameterValue(str(v)) for v in values ]
        self._name = vName( name )
    
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = vName( value )
    
    def append_value(self, value):
        self.values.append( vParameterValue(value) )
    
    def has_value(self, value, ignorecase=False):
        value = str(value)
        if ignorecase:
            value = value.casefold()
        for v in self.values:
            if str(v) == value or (ignorecase and str(v).casefold() == value):
                return True
        return False
    
    def __str__(self):
        return self.serialize()

    def serialize(self):
        va = [ value.as_quote() for value in self.values ]
        return "{}={}".format( str(self.name), ",".join(va) )

class vParameterList( object ):
    
    def __init__(self):
        self.params = []
    
    def _check_item_type(self, item):
        if not isinstance(item, vParameter ):
            raise TypeError( "vParameterList can only store vParameter objects" )

    def __iter__(self):
        return iter( self.params )

    def __len__(self):
        return len( self.params )

    def __str__(self):
        return self.serialize()
    
    def serialize(self):
        pa = [ p.serialize() for p in self.params ]
        return ';'.join(pa)

    def index(self, name):
        name = vName( name )
        for i in range( len(self.params) ):
            if self.params[ i ].name == name:
                return i
        raise ValueError()
    
    def __getitem__(self, name):
        name = vName( name )
        for param in self.params:
            if param.name == name:
                return param
        raise KeyError()
    
    def __setitem__(self, name, param):
        self._check_item_type( param )
        param.name = name
        try:
            index = self.index( param.name )
            self.params[ index ] = param 
        except ValueError:
            self.params.append( param )
    
    def __delitem__(self, name):
        try:
            index = self.index( name )
            del self.params[ index ]
        except ValueError:
            pass
    
    def get(self, name, default=None):
        try:
            return self.__getitem__( name )
        except KeyError:
            return default
    
    def set(self, name, value_str):
        param = vParameter( name=name, values=[value_str] )
        self.__setitem__( name, param )
    
    def append(self, param):
        self._check_item_type( param )
        self.params.append( param )
