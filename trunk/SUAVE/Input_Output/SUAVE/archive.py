# Input_Output.SUAVE.save.py
#
# Created By:   Trent Jan 2015

""" Save a native SUAVE file """

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

from SUAVE.Core import Data
from SUAVE.Plugins.VyPy.data import save as vypy_save

# ----------------------------------------------------------------------
#  Method
# ----------------------------------------------------------------------

def archive(data,filename):
    """ archive data to file 
        down-converts all Data-type classes to Data, regardless of type
        helps future-proof the data to changing package structure
    """
    
    data = Data(data)
    
    def to_data(D):
        for k,v in D.items():
            if isinstance(v,Data):
                D[k] = Data(v)
                to_data(D[k])
    
    to_data(data)
    
    vypy_save(data,filename,file_format='pickle')
    