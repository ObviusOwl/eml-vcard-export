import csv
import sys

import pandas as pd
import numpy as np

from .vcard import vAttribute
from .vcard.attributes import *

class CsvTable( object ):
    
    def __init__(self, sep='|'):
        self.df = pd.DataFrame()
        self.sep = sep
    
    def append_row_df(self, row_df):
        self.df = self.df.append( row_df, ignore_index=True )
    
    def drop_na_columns(self): 
        self.df.dropna( axis=1, how='all', inplace=True )

    def write_file(self, file_path=None):
        if file_path is None:
            outf = sys.stdout
        else:
            outf = open(file_path, 'w')

        try:
            self.df.to_csv( outf, index=False, sep=self.sep, quoting=csv.QUOTE_ALL )
        finally:
            if not file_path is None:
                outf.close()

class CsvExportStrategy( object ):
    def __init__(self):
        pass

class FullCsvExportStrategy( CsvExportStrategy ):
    
    def __init__(self):
        super().__init__()
        self.rdata = {}
    
    def _set_data(self, column_name, value, empty_is_na=False ):
        if empty_is_na and value == '':
            value = np.nan
        self.rdata[ column_name ] = [ value ]
    
    def _set_data_list( self, column_name, value_list, empty_is_na=False ):
        for i in range( len(value_list) ):
            item_col = column_name+'_{}'.format(i+1)
            self._set_data( item_col, str(value_list[i]), empty_is_na )

    def vcard_to_df(self, vcard):
        self.rdata = {}

        name_counts = {}
        for attr in vcard.attrs:
            name = str(attr.name).upper()
            if name in [ 'BEGIN','END' ]:
                continue
            
            if name in name_counts:
                name_counts[ name ] += 1
            else:
                name_counts[ name ] = 1
            num = name_counts[ name ]
            
            col_pref = "{}_{}_".format( name, num )
            param_value = ';'.join( [ str(p) for p in attr.params ] )

            self._set_data( col_pref+'GROUP', str(attr.group), empty_is_na=True )
            self._set_data( col_pref+'PARAM', param_value, empty_is_na=True )
            self.visit_attr( attr, col_pref )

        df = pd.DataFrame( self.rdata )
        return df
    
    def visit_attr(self, attr, prefix):

        if isinstance( attr, vFnAttribute ):
            self.visit_simple_text_attr( attr, 'fn', prefix+'VALUE' )
        elif isinstance( attr, vNameAttribute ):
            self.visit_attr_name( attr, prefix )
        elif isinstance( attr, vNicknameAttribute ):
            self.visit_simple_text_list_attr( attr, 'nickname', prefix+'VALUE' )
        elif isinstance( attr, vBdayAttribute ):
            self.visit_simple_text_attr( attr, 'birthday', prefix+'VALUE' )
        elif isinstance( attr, vAdrAttribute ):
            self.visit_attr_adr( attr, prefix )
        elif isinstance( attr, vLabelAttribute ):
            self.visit_simple_text_attr( attr, 'label', prefix+'VALUE' )
        elif isinstance( attr, vTelAttribute ):
            self.visit_simple_text_attr( attr, 'tel', prefix+'VALUE' )
        elif isinstance( attr, vEmailAttribute ):
            self.visit_simple_text_attr( attr, 'email', prefix+'VALUE' )
        elif isinstance( attr, vMailerAttribute ):
            self.visit_simple_text_attr( attr, 'mailer', prefix+'VALUE' )
        elif isinstance( attr, vTzAttribute ):
            self.visit_simple_text_attr( attr, 'time_zone', prefix+'VALUE' )
        elif isinstance( attr, vGeoAttribute ):
            self.visit_attr_geo( attr, prefix )
        elif isinstance( attr, vTitleAttribute ):
            self.visit_simple_text_attr( attr, 'title', prefix+'VALUE' )
        elif isinstance( attr, vRoleAttribute ):
            self.visit_simple_text_attr( attr, 'role', prefix+'VALUE' )
        elif isinstance( attr, vAgentAttribute ):
            self.visit_simple_text_attr( attr, 'agent', prefix+'VALUE' )
        elif isinstance( attr, vOrgAttribute ):
            self.visit_attr_org( attr, prefix )
        elif isinstance( attr, vCategoriesAttribute ):
            self.visit_simple_text_list_attr( attr, 'categories', prefix+'VALUE' )
        elif isinstance( attr, vNoteAttribute ):
            self.visit_simple_text_attr( attr, 'note', prefix+'VALUE' )
        elif isinstance( attr, vProdidAttribute ):
            self.visit_simple_text_attr( attr, 'prodid', prefix+'VALUE' )
        elif isinstance( attr, vRevAttribute ):
            self.visit_simple_text_attr( attr, 'rev', prefix+'VALUE' )
        elif isinstance( attr, vSortstringAttribute ):
            self.visit_simple_text_attr( attr, 'sort_string', prefix+'VALUE' )
        elif isinstance( attr, vUidAttribute ):
            self.visit_simple_text_attr( attr, 'uid', prefix+'VALUE' )
        elif isinstance( attr, vUrlAttribute ):
            self.visit_simple_text_attr( attr, 'url', prefix+'VALUE' )
        elif isinstance( attr, vVersionAttribute ):
            self.visit_simple_text_attr( attr, 'version', prefix+'VALUE' )
        elif isinstance( attr, vClassAttribute ):
            self.visit_simple_text_attr( attr, 'class', prefix+'VALUE' )
        elif isinstance( attr, vImageAttribute ):
            self.visit_binuri_attr( attr, prefix+'VALUE' )
        elif isinstance( attr, vSoundAttribute ):
            self.visit_binuri_attr( attr, prefix+'VALUE' )
        # TODO: KEY attribute

        elif isinstance( attr, vSourceAttribute ):
            self.visit_simple_text_attr( attr, 'source', prefix+'VALUE' )
        elif isinstance( attr, vProfileAttribute ):
            self.visit_simple_text_attr( attr, 'profile', prefix+'VALUE' )

        elif isinstance( attr, vImppAttribute ):
            self.visit_simple_text_attr( attr, 'impp', prefix+'VALUE' )

        elif isinstance( attr, vAttribute ):
            self._set_data( prefix+'VALUE_ENC', str(attr.value), empty_is_na=False )
    
    def visit_simple_text_attr(self, attr, attr_name, column_name):
        self._set_data( column_name, str( getattr(attr, attr_name) ) )

    def visit_simple_text_list_attr(self, attr, attr_name, column_name):
        self._set_data_list( column_name, getattr(attr, attr_name) )

    def visit_binuri_attr(self, attr, column_name):
        if attr.has_uri:
            self._set_data( column_name, str( attr.uri ) )
        else:
            self._set_data( column_name, attr.uri.to_base64() )

    def visit_attr_name(self, attr, prefix):
        self._set_data_list( prefix+'FAMILY', attr.family_names )
        self._set_data_list( prefix+'GIVEN', attr.given_names )
        self._set_data_list( prefix+'ADDITIONAL', attr.additional_names )
        self._set_data_list( prefix+'HONOR_PREF', attr.honorific_prefixes )
        self._set_data_list( prefix+'HONOR_SUFF', attr.honorific_suffixes )

    def visit_attr_adr(self, attr, prefix):
        self._set_data_list( prefix+'POBOX', attr.po_box )
        self._set_data_list( prefix+'EXTEND', attr.extended )
        self._set_data_list( prefix+'STREET', attr.street )
        self._set_data_list( prefix+'CITY', attr.locality )
        self._set_data_list( prefix+'REGION', attr.region )
        self._set_data_list( prefix+'POSTCODE', attr.postal_code )
        self._set_data_list( prefix+'COUNTRY', attr.country )

    def visit_attr_geo(self, attr, prefix):
        self._set_data( prefix+'LAT', str( attr.latitude ) )
        self._set_data( prefix+'LON', str( attr.longitude ) )

    def visit_attr_org(self, attr, prefix):
        self._set_data( prefix+'ORG_NAME', str( attr.organization ) )
        self._set_data_list( prefix+'DIV', attr.divisions )
