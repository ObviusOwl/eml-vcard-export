import re

def vcard_fold_line( logical_line, line_length=75 ):
    # RFC2425 section 5.8.1 
    out = ""
    log_line_len = len( logical_line )

    for i in range( log_line_len ):
        out += logical_line[ i ]

        if i % line_length == 0 and i != 0 and i < log_line_len-1:
            # only fold if there is still content
            out += "\n "
    
    return out

class vCardLineTokenizer( object ):
    # TODO: track line range: current logical line L, which is from line l to line k
    def __init__(self, data=''):
        self.load( data )
    
    def load(self, data):
        self.index = 0
        self.max_index = len(data)
        self.data = data
        self.line_number = 0
        self.line = ""
    
    def next(self):
        state = ''
        idx = self.index
        line_buff = ''
        while True:
            if idx == self.max_index:
                break
            c = self.data[ idx ]
            
            # state machine transition
            if c in ('\r', '\n'):
                # accepting \r\n, \r, \n as line end (RFC accepts only \r\n)
                state = 'CR_LF'
            elif state == 'CR_LF':
                if c in ('\t', ' '):
                    state = 'CR_LF_SP'
                else:
                    state = 'CR_LF_NSP'
            else:
                state = ''
            
            if state == 'CR_LF_NSP':
                # normal line without folding or end of folded line
                break
            elif c != '\r' and c != '\n' and state != 'CR_LF_SP':
                # filter CR, LF and CR_LF_SP
                line_buff += c

            idx += 1
        
        self.index = idx
        self.line = line_buff
        return self.line
    
    def __iter__(self):
        return self
    def __next__(self):
        line = self.next()
        if line == '':
            raise StopIteration()
        return line

class vCardTokenizer( object ):
    # https://tools.ietf.org/html/rfc2426#section-4
    
    def __init__(self, data=""):
        self.load( data )
        self.terminal_re_map = {
            #ABNF: group        = 1*(ALPHA / DIGIT / "-")
            #ABNF: name         = x-name / iana-token
            #ABNF: iana-token   = 1*(ALPHA / DIGIT / "-")
            #ABNF: x-name       = "x-" 1*(ALPHA / DIGIT / "-")
            #ABNF: param-name   = x-name / iana-token
            'identifier': re.compile( '[a-zA-z0-9-]+' ),
            #ABNF: quoted-string = DQUOTE QSAFE-CHAR DQUOTE
            #ABNF: QSAFE-CHAR   = WSP / %x21 / %x23-7E / NON-ASCII ; Any character except CTLs, DQUOTE
            'quoted-string': re.compile( '"[^"]*"' ),
            #ABNF:   SAFE-CHAR    = WSP / %x21 / %x23-2B / %x2D-39 / %x3C-7E / NON-ASCII 
            #                       ; Any character except CTLs, DQUOTE, ";", ":", ","
            'safe-string': re.compile( '[^";:,]+' ),
            # non-safe-chars:
            'dot-char': re.compile( '\.' ),
            'colon-char': re.compile( ':' ),
            'semicolon-char': re.compile( ';' ),
            'comma-char': re.compile( ',' ),
            'eq-char': re.compile( '=' ),
            # may match empty string
            'any-string': re.compile( '.*' ),
        }
    
    def load(self, data):
        self.data = data
        self.index = 0
        self.token = ''
    
    def _set_current(self, index, token, peek=False):
        if not peek:
            self.token = token
            self.index = index
        return token
    
    def next(self, *included_terminals, peek=False, allow_empty=False):
        for terminal_name in included_terminals:
            if not terminal_name in self.terminal_re_map:
                continue

            m = self.terminal_re_map[ terminal_name ].match( self.data, self.index )
            if m != None:
                if m.start == m.end and not allow_empty:
                    raise RuntimeError( "vcard tokenizer regex matched an empty string" )
                # first matching regex wins
                return self._set_current( m.end(0), m.group(0), peek=peek )
        # no regex matched
        return self._set_current( self.index, '', peek=peek )
    
    def require_next(self, *args, **kwargs):
        kwargs['peek'] = False
        self.next( *args, **kwargs )

        if self.token == '':
            terms = []
            curr = self.data[ self.index ]
            for k,v in self.terminal_re_map.items():
                if k in args:
                    terms.append( '{} ({})'.format(k,v.pattern) )
            raise ParserError( "Expected a char of {}, but got '{}'".format(', '.join(terms), curr) )

        return self.token

    def has_next(self, *args, **kwargs):
        kwargs['peek'] = True
        token = self.next( *args, **kwargs )
        return token != ''
