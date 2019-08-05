import argparse
import os
import os.path
import sys
import traceback

import pandas as pd

from .helper import FileIterator
from .directory_message import DirectoryMessage
from . import vcard
from . import csv_export
from . import vcf_export

class CliApp( object ):
    def __init__(self):
        self.args = None

    def parse_args(self):
        main_p = argparse.ArgumentParser()
        main_sub_p = main_p.add_subparsers( dest="subcommand", help="Action to run" )
        
        export_p = main_sub_p.add_parser( 'csv_export', help="Export eml files to csv" )
        export_p.set_defaults( subparser_callback=self.subcommand_export_csv )
        export_p.add_argument('input_path', metavar="PATH", 
                              help="Path to a input eml file or a directory to search for eml files" )
        export_p.add_argument('--limit', metavar='COUNT', dest='limit_input_files', type=int, default=-1,
                              help="Limit processing to the first COUNT found files. Defaults to -1, unlimited." )
        export_p.add_argument('--out-file','-o', metavar='FILE.CSV', dest='output_path', default=None,
                              help="Path to the output file. If omitted, stdout is used." )

        export_p = main_sub_p.add_parser( 'vcf_export', help="Export eml files to vcf" )
        export_p.set_defaults( subparser_callback=self.subcommand_export_vcf )
        export_p.add_argument('input_path', metavar="PATH", 
                              help="Path to a input eml file or a directory to search for eml files" )
        export_p.add_argument('--limit', metavar='COUNT', dest='limit_input_files', type=int, default=-1,
                              help="Limit processing to the first COUNT found files. Defaults to -1, unlimited." )
        export_p.add_argument('--out-file','-o', metavar='FILE.VCS', dest='output_path', default=None,
                              help="Path to the output file. If omitted, stdout is used." )
        
        self.args = main_p.parse_args()
        if not hasattr(self.args, 'subparser_callback'):
            main_p.print_help()
            sys.exit( 2 )

    def main(self):
        self.args.subparser_callback( self.args )
        
    def subcommand_export_csv(self, args):
        export_strategy = csv_export.FullCsvExportStrategy()
        table = csv_export.CsvTable()
        
        file_it = FileIterator( args.input_path )
        file_it.extensions = ['eml']
        file_it.max_items = args.limit_input_files
        
        for file_path in file_it:
            try:
                print( file_path, file=sys.stderr )
                data = {
                    'FILE_PATH': [file_path],
                }
                file_df = pd.DataFrame( data )

                dm = DirectoryMessage()
                dm.load_file( file_path )
                vcard_data = dm.extract_vcard()
                p = vcard.parser.vCardParser()
                card = p.parse_vcard( vcard_data )
                vcard_df = export_strategy.vcard_to_df( card )
                
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

    def subcommand_export_vcf(self, args):
        export_strategy = vcf_export.DefaultVcfExportStrategy()

        if args.output_path is None:
            out_fh = sys.stdout
        else:
            out_fh = open(args.output_path, 'w')
        
        file_it = FileIterator( args.input_path )
        file_it.extensions = ['eml']
        file_it.max_items = args.limit_input_files
        
        for file_path in file_it:
            try:
                print( file_path, file=sys.stderr )

                dm = DirectoryMessage()
                dm.load_file( file_path )
                card = export_strategy.message_to_vcard( dm )
                card_vcf = export_strategy.serialize_vcard( card )
                
                out_fh.write( card_vcf+'\n\n' )
            except Exception as e:
                traceback.print_exc()
                print( "Error:", str(e), file=sys.stderr )
                print("Ignoring file:", file_path, file=sys.stderr )

        if args.output_path is not None:
            out_fh.close()

        print( "file count:", file_it.item_count, file=sys.stderr )
