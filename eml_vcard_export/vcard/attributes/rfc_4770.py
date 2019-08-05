from .base import vAbstractTextAttr

class vImppAttribute( vAbstractTextAttr ):
    # RFC4770 section 2
    registered_names = ( 'impp', )
    _value_class_attr_name = 'impp'
