import json
import sys

from .vcard import vAttribute
from .vcard.attributes import *


class JsonExportStrategy( object ):
    def __init__(self):
        pass

class DefaultJsonExportStrategy( JsonExportStrategy ):
    
    def __init__(self):
        super().__init__()
        
        self.attr_handlers = [
            ( vFnAttribute,        self._handle_text_attr ),
            ( vNameAttribute,      self._handle_attr_name ),
            ( vNicknameAttribute,  self._handle_text_list_attr ),
            ( vBdayAttribute,      self._handle_text_attr ),
            ( vAdrAttribute,       self._handle_attr_adr ),
            ( vLabelAttribute,     self._handle_text_attr ),
            ( vTelAttribute,       self._handle_text_attr ),
            ( vEmailAttribute,     self._handle_text_attr ),
            ( vMailerAttribute,    self._handle_text_attr ),
            ( vTzAttribute,        self._handle_text_attr ),
            ( vGeoAttribute,       self._handle_geo_attr ),
            ( vTitleAttribute,     self._handle_text_attr ),
            ( vRoleAttribute,      self._handle_text_attr ),
            ( vAgentAttribute,     self._handle_text_attr ),
            ( vOrgAttribute,       self._handle_attr_org ),
            ( vCategoriesAttribute, self._handle_text_list_attr ),
            ( vNoteAttribute,      self._handle_text_attr ),
            ( vProdidAttribute,    self._handle_text_attr ),
            ( vRevAttribute,       self._handle_text_attr ),
            ( vSortstringAttribute, self._handle_text_attr ),
            ( vUidAttribute,       self._handle_text_attr ),
            ( vUrlAttribute,       self._handle_text_attr ),
            ( vVersionAttribute,   self._handle_text_attr ),
            ( vClassAttribute,     self._handle_text_attr ),
            ( vImageAttribute,     self._handle_binuri_attr ),
            ( vSoundAttribute,     self._handle_binuri_attr ),
            # TODO: KEY attribute

            ( vSourceAttribute,    self._handle_text_attr ),
            ( vProfileAttribute,   self._handle_text_attr ),

            ( vImppAttribute,      self._handle_text_attr ),
        ]
    
    def vcard_to_native(self, vcard ):
        vcard_data = []
        for attr in vcard.attrs:
            name = str(attr.name).lower()
            if name in ("begin","end"):
                continue
            
            attr_data = { "name": name }
            
            group = str( attr.group )
            if group != "":
                attr_data[ "group" ] = group
                
            params = self._handle_params( attr.params )
            if params:
                attr_data[ "params" ] = params

            attr_data = self._handle_attr( attr, attr_data )

            vcard_data.append( attr_data )
        return vcard_data

    def vcard_dumps(self, vcard, indent=None ):
        return json.dumps( self.vcard_to_native(vcard), indent=indent )
    
    def _handle_params(self, params ):
        data = {}
        for param in params:
            name = str( param.name ).lower()
            if not name in data:
                data[ name ] = []
            data[ name ].extend( [ str(v) for v in param.values ] )
        return data
    
    def _handle_attr(self, attr, data):
        for handler in self.attr_handlers:
            if isinstance( attr, handler[0] ):
                return handler[1]( attr, data )

        if isinstance( attr, vAttribute ):
            # unknown value type
            data[ "type" ] = "vcard-original-value"
            data[ "value" ] = str( attr.original_value )
            return data

    def _get_value(self, attr, name ):
        return str( getattr( attr, name ) )
    
    def _get_value_list(self, attr, name):
        return [ str( v ) for v in getattr( attr, name ) ]
            
    def _handle_text_attr(self, attr, data ):
        data[ "type" ] = "text"
        data[ "value" ] = self._get_value( attr, "value" )
        return data
    
    def _handle_text_list_attr(self, attr, data ):
        data[ "type" ] = "text-list"
        data[ "value" ] = self._get_value_list( attr, "value" )
        return data

    def _handle_struct_attr(self, attr, data, name_map ):
        # name_map: json_key => attr
        data[ "type" ] = "text-struct"
        data[ "value" ] = {}
        for out_key, in_key in name_map.items():
            data[ "value" ][ out_key ] = self._get_value_list( attr, in_key )
        return data


    def _handle_attr_name(self, attr, data ):
        # json_key => attr
        name_map = {
            "family": "family_names", "given": "given_names", "additional": "additional_names", 
            "honor-prefix": "honorific_prefixes",  "honor-suffix": "honorific_suffixes", 
        }
        return self._handle_struct_attr( attr, data, name_map )

    def _handle_attr_adr(self, attr, data ):
        # json_key => attr
        name_map = {
            "po-box": "po_box", "extended": "extended", "street": "street",
            "locality": "locality", "region":"region", "postal-code": "postal_code",
            "country": "country"
        }
        return self._handle_struct_attr( attr, data, name_map )

    def _handle_geo_attr(self, attr, data ):
        data[ "type" ] = "text-struct"
        data[ "value" ] = { 
            "latitude": self._get_value( attr, "latitude" ), 
            "longitude": self._get_value( attr, "longitude" )
        }
        return data

    def _handle_attr_org(self, attr, data ):
        data[ "type" ] = "text-struct"
        data[ "value" ] = { 
            "organization": self._get_value( attr, "organization" ), 
            "divisions": self._get_value_list( attr,  "divisions" )
        }
        return data

    def _handle_binuri_attr(self, attr, data ):
        if attr.has_uri:
            data[ "type" ] = "uri"
            data[ "value" ] = self._get_value( attr, "uri" )
        else:
            data[ "type" ] = "bin-b64"
            data[ "value" ] = attr.uri.to_base64()
        return data
