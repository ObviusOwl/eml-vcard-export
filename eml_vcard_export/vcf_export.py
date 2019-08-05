import base64

from . import vcard
from .vcard.lexer import vcard_fold_line
from .directory_message import ContentId

from .vcard.attributes import *

class VcfExportStrategy( object ):
    def __init__(self):
        pass

class DefaultVcfExportStrategy( VcfExportStrategy ):
    
    def __init__(self, line_length=75):
        self.line_length = line_length

    def message_to_vcard(self, dir_message ):
        vcard_data = dir_message.extract_vcard()

        p = vcard.parser.vCardParser()
        card = p.parse_vcard( vcard_data )
        
        for attr in card.attrs:
            self.load_visit_attr( dir_message, attr )
        
        return card
    
    def load_visit_attr(self, dir_message, attr):
        if isinstance( attr, vImageAttribute ):
            self.load_attr_content_uri( dir_message, attr )
        elif isinstance( attr, vSoundAttribute ):
            self.load_attr_content_uri( dir_message, attr )
    
    def load_attr_content_uri(self, dir_message, attr):
        if not attr.has_uri:
            return

        try:
            cid = ContentId.from_URI( str(attr.uri) )
        except ValueError:
            return
        
        message = dir_message.find_part_by_cid( cid )
        if message is None:
            return 

        data = message.get_content()
        if not isinstance(data, bytes):
            return
        # setter also sets attr to binary mode
        attr.data = data


    def serialize_vcard(self, card):
        lines= []
        for attr in card.attrs:
            line = self.serialize_attr( attr )
            line = vcard_fold_line( line, line_length=self.line_length )
            lines.append( line )
        return '\n'.join( lines )
    
    def serialize_attr(self, attr):
        if isinstance( attr, vImageAttribute ):
            return attr.serialize( original_value=False ) 
        elif isinstance( attr, vSoundAttribute ):
            return attr.serialize( original_value=False ) 

        else:
            return attr.serialize( original_value=True ) 
