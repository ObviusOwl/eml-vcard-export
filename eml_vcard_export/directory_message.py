import os.path
import email
import email.policy
import re
import base64
import urllib.parse

class ContentId( object ):
    # content-id URI is defined in https://tools.ietf.org/html/rfc2392
    def __init__(self, id):
        self.id = id
    
    @classmethod
    def from_URI(cls, uri):
        if not uri[:4].lower() == "cid:":
            raise ValueError("Not a cid URI")
        id = urllib.parse.unquote( uri[4:] )
        return cls( id=id )
    
    def as_URI(self):
        return 'cid:' + urllib.parse.quote_plus( self.id )

    @classmethod
    def from_header_value(cls, header_value):
        if header_value[0] != '<' or header_value[-1] != '>':
            raise ValueError("Not a Content-ID or Message-ID header value")
        return cls( id=header_value[1:-1] )
    
    def as_header_value(self):
        return '<' + self.id + '>'

    def __eq__(self, other):
        if not hasattr( other, 'id'):
            return False
        return self.id == other.id
    
    def __str__(self):
        return self.id

    def __repr__(self):
        return '<Conent-Id: {}>'.format( self.id )

class DirectoryMessage( object ):
    
    def __init__(self):
        self.message = None
    
    def load_file(self, file_path ):
        with open(file_path, 'rb') as fp:
            self.message = email.message_from_binary_file(fp, policy=email.policy.default)
    
    def _require_message(self):
        if self.message is None:
            raise RuntimeError( "No email message loaded" )
    
    def find_part_by_cid(self, cid):
        self._require_message()
        for part in self.message.walk():
            h_cid = part.get("content-id")
            if h_cid is None:
                continue
            if ContentId.from_header_value( h_cid ) == cid:
                return part
        return None

    def extract_vcard(self):
        self._require_message()
        body = self.message.get_body( preferencelist=('vcard','plain') )
        return body.get_content()
    
