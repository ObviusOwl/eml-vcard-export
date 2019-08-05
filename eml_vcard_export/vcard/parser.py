from .lexer import vCardLineTokenizer, vCardTokenizer

from .common import vCard
from .attributes import vAttributeType, vAttribute
from .parameter import vParameter

from . import attributes

class ParserError( Exception ):
    # TODO: line infos
    pass

class vCardParser( object ):
    
    def __init__(self):
        self.current_line = 0
        self.line_tokenizer = None
        self.tokenizer = None
        
    def _parse_line(self, line):
        self.tokenizer = vCardTokenizer( line )
        #attr = vAttribute()
        #ABNF: contentline  = [group "."] name *(";" param) ":" value CRLF
        #ABNF: name         = iana-token / x-name
        #ABNF: group        = 1*(ALPHA / DIGIT / "-")
        #ABNF: value        = *VALUE-CHAR
        #ABNF: VALUE-CHAR   = WSP / VCHAR / NON-ASCII ; Any textual character

        group = ''
        name = self.tokenizer.require_next( 'identifier' )
        if self.tokenizer.has_next( 'dot-char' ):
            self.tokenizer.next( 'dot-char' )
            group = name
            name = self.tokenizer.require_next( 'identifier' )
        
        attr_cls = vAttributeType.class_for_name( name )
        if attr_cls is None:
            attr_cls = vAttribute
        attr = attr_cls()

        attr.name = name
        attr.group = group

        while self.tokenizer.has_next( 'semicolon-char' ):
            self.tokenizer.next( 'semicolon-char' )
            param = self._parse_param()
            attr.params.append( param )

        self.tokenizer.require_next( 'colon-char' )
        # note decoding/parsing the value is done in the setter
        # also set the value __after__ the params, since they contain decoding infos
        attr.value = self.tokenizer.next( 'any-string', allow_empty=True )
        return attr
    
    def _parse_param(self):
        #ABNF: param        = param-name "=" param-value *("," param-value)
        #ABNF: param-name   = iana-token / x-name
        #ABNF: param-value  = ptext / quoted-string
        #ABNF: ptext        = *SAFE-CHAR
        param = vParameter()
        param.name = self.tokenizer.require_next( 'identifier' )
        self.tokenizer.require_next( 'eq-char' )
        
        value = self.tokenizer.require_next( 'safe-string', 'quoted-string' )
        param.append_value( value )
        while self.tokenizer.has_next( 'comma-char' ):
            self.tokenizer.next( 'comma-char' )
            value = self.tokenizer.require_next( 'safe-string', 'quoted-string' )
            param.append_value( value )
        return param
    
    def parse_vcard(self, data):
        #TODO: search VERSION:3.0 in data and raise if not present
        self.line_tokenizer = vCardLineTokenizer( data )
        card = vCard()
        for line in self.line_tokenizer:
            attr = self._parse_line( line )
            card.append_attr( attr )
        return card
