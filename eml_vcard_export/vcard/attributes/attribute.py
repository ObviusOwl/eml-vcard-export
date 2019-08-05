from ..value import vValue, vTextValue, vBinaryValue
from ..parameter import vParameterList, vParameter
from ..common import vName

class vAttributeType( type ):
    attribute_class_registry = {}

    def __init__(cls, name, bases, nmspc):
        super().__init__(name, bases, nmspc)

        # using a list to allow a single class to handle multiple similar attributes
        reg_names = []
        try:
            reg_names = [ str(n).upper() for n in cls.registered_names ]
        except AttributeError:
            pass

        for reg_name in reg_names:
            # overriding previously registered attributes is fine
            vAttributeType.attribute_class_registry[ reg_name ] = cls
    
    @classmethod
    def class_for_name(cls, name):
        try:
            return cls.attribute_class_registry[ str(name).upper() ]
        except KeyError:
            return None


class vAttribute( object, metaclass=vAttributeType ):
    def __init__(self):
        self._value = vValue( "" )
        self._name = vName( "" )
        self._group = vName( "" )
        self._params = vParameterList()

    @property
    def original_value(self):
        # source of truth is the parsed vcard file
        return self._value

    @property
    def value(self):
        # source of truth are the decoded/modified/set class attributes
        return self.encode_value()

    @value.setter
    def value(self, value):
        self.decode_value( value )

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = vName( value )

    @property
    def group(self):
        return self._group
    @group.setter
    def group(self, value):
        self._group = vName( value )

    @property
    def full_name(self):
        if self._group != '':
            return str(self._group) + '.' + str(self._name)
        return str(self._name)

    @property
    def params(self):
        return self._params
    
    def __str__(self):
        return self.serialize( original_value=False )
    
    def serialize(self, original_value=False):
        params = self._params.serialize()
        if params != '':
            params = ';' + params

        if original_value:
            value = self.original_value
        else:
            value = self.value

        return "{}{}:{}".format( str(self.full_name), params, str(value) )
    
    def encode_value(self):
        # use class attributes to create a value usabe as self._value
        # should not have side effects
        return vValue( self._value )

    def decode_value(self, value):
        # parse/decode value and fill class attributes and self._value
        # can also have other side effects like setting correct params
        self._value = vValue( value )
