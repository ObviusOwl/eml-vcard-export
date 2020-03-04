import os.path
import sys

import pandas as pd

class FileOutput( object ):
    def __init__(self, file_name, method ):
        self.do_close = False

        if file_name is None:
            file_name = sys.stdout
        if file_name != sys.stdout and file_name != sys.stderr:
            self.fh = open( file_name, method )
            self.do_close = True
        else:
            self.fh = file_name
        
    def __enter__(self):
        return self.fh

    def __exit__(self, type, value, traceback):
        if self.do_close:
            self.fh.close()

class FileIterator( object ):
    
    def __init__(self, *base_paths, extensions=None, limit=None ):
        # base_path can be directory or single eml file
        self.base_paths = list(base_paths)
        self.extensions = []
        self.max_items = -1

        if extensions is not None:
            self.extensions = extensions
        if limit is not None:
            self.max_items = limit

        self.base_stack = []
        self.file_stack = []
        self.curr_iter = None
        self.item_count = 0
        self.reset()

    def reset(self):
        self.base_stack = self.base_paths.copy()
        self.file_stack = []
        self.curr_iter = None
        self.item_count = 0
    
    def _mk_walk_iter(self, base_path):
        if os.path.isfile( base_path ):
            base_dir = os.path.dirname( base_path )
            filename = os.path.basename( base_path )
            walk_tuple = ( base_dir, (), (filename,) )
            return iter( (walk_tuple,) )
        elif os.path.isdir( base_path ):
            return iter( os.walk( base_path ) )
        return None
    
    def __iter__(self):
        return self

    def __next__(self):
        if not self.base_stack and not self.file_stack:
            raise StopIteration()
        if self.max_items >= 0 and self.item_count >= self.max_items:
            raise StopIteration()

        if self.file_stack:
            file = self.file_stack.pop()
            ext = os.path.splitext( file )[1].lstrip('.')
            if not self.extensions or ext in self.extensions:
                self.item_count += 1
                return file
            else:
                # recursion skipping this file
                return self.__next__()
        
        if self.curr_iter is None:
            self.curr_iter = self._mk_walk_iter( self.base_stack.pop() )
        if self.curr_iter is None:
            raise StopIteration()
        
        try:
            (dirpath, dirnames, filenames) = self.curr_iter.__next__()
            for name in filenames:
                self.file_stack.append( os.path.join(dirpath, name) )
        except StopIteration:
            self.curr_iter = None
        finally:
            # tail recursion until base_stack and file_stack are empty
            # assuming here that we reached this code because file_stack was/is empty
            return self.__next__()


