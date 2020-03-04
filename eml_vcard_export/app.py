import argparse
import os
import os.path
import sys
import traceback

import pandas as pd

from .helper import FileIterator, FileOutput
from .directory_message import DirectoryMessage
from . import vcard
from . import csv_export
from . import vcf_export

class ExportCsvApp( object ):
    
    def parse_args(self, export_p):
        export_p.add_argument('input_path', metavar="PATH", 
                              help="Path to a input eml file or a directory to search for eml files" )
        export_p.add_argument('--limit', metavar='COUNT', dest='limit_infiles', type=int, default=-1,
                              help="Limit processing to the first COUNT found files. Defaults to -1, unlimited." )
        export_p.add_argument('--out-file','-o', metavar='FILE.CSV', dest='output_path', default=None,
                              help="Path to the output file. If omitted, stdout is used." )
        
    def main(self, args ):
        strategy = csv_export.FullCsvExportStrategy()
        table = csv_export.CsvTable()
        file_it = FileIterator( args.input_path, extensions=('eml',), limit=args.limit_infiles )

        for file_path in file_it:
            print( file_path, file=sys.stderr )
            try:
                dm = DirectoryMessage.from_file( file_path )
                card = vcard.parser.parse_vcard( dm.extract_vcard() )

                data = {
                    'FILE_PATH': [file_path],
                }
                file_df = pd.DataFrame( data )
                vcard_df = strategy.vcard_to_df( card )
                df = file_df.join( vcard_df )
                table.append_row_df( df )
            except Exception as e:
                traceback.print_exc()
                print( "Error:", str(e), file=sys.stderr )
                print("Ignoring file:", file_path, file=sys.stderr )

        print( "file count:", file_it.item_count, file=sys.stderr )

        table.drop_na_columns()
        print( table.df.info(), file=sys.stderr )
        
        table.write_file( args.output_path )

class ExportVcfApp( object ):
    
    def parse_args(self, export_p):
        export_p.add_argument('input_path', metavar="PATH", 
                              help="Path to a input eml file or a directory to search for eml files" )
        export_p.add_argument('--limit', metavar='COUNT', dest='limit_infiles', type=int, default=-1,
                              help="Limit processing to the first COUNT found files. Defaults to -1, unlimited." )
        export_p.add_argument('--out-file','-o', metavar='FILE.CSV', dest='output_path', default=None,
                              help="Path to the output file. If omitted, stdout is used." )
        
    def main(self, args ):
        strategy = vcf_export.DefaultVcfExportStrategy()
        file_it = FileIterator( args.input_path, extensions=('eml',), limit=args.limit_infiles )

        with FileOutput( args.output_path, "w" ) as out_fh:
            for file_path in file_it:
                print( file_path, file=sys.stderr )
                try:
                    dm = DirectoryMessage.from_file( file_path )
                    card = vcard.parser.parse_vcard( dm.extract_vcard() )
                    card_vcf = strategy.serialize_vcard( card )
                    
                    out_fh.write( card_vcf+'\n\n' )
                except Exception as e:
                    traceback.print_exc()
                    print( "Error:", str(e), file=sys.stderr )
                    print("Ignoring file:", file_path, file=sys.stderr )

        print( "file count:", file_it.item_count, file=sys.stderr )


class CliApp( object ):
    def __init__(self):
        self.args = None
        self.csv_app = ExportCsvApp()
        self.vcf_app = ExportVcfApp()

    def parse_args(self):
        main_p = argparse.ArgumentParser()
        main_sub_p = main_p.add_subparsers( dest="subcommand", help="Action to run" )

        export_p = main_sub_p.add_parser( 'csv_export', help="Export eml files to csv" )
        export_p.set_defaults( subparser_callback=self.csv_app.main )
        self.csv_app.parse_args( export_p )

        export_p = main_sub_p.add_parser( 'vcf_export', help="Export eml files to vcf" )
        export_p.set_defaults( subparser_callback=self.vcf_app.main )
        self.vcf_app.parse_args( export_p )

        self.args = main_p.parse_args()
        if not hasattr(self.args, 'subparser_callback'):
            main_p.print_help()
            sys.exit( 2 )

    def main(self):
        self.args.subparser_callback( self.args )
