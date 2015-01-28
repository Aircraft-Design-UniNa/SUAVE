
# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

from SUAVE.Plugins.VyPy.data import DiffedDataBunch
from Container import Container as ContainerBase
from Data import Data

from copy import deepcopy

# ----------------------------------------------------------------------
#  Config
# ----------------------------------------------------------------------

class DiffedData(DiffedDataBunch,Data):
    """ SUAVE.Core.DiffedData()
    """
    
    def finalize(self):
        ## dont do this here, breaks down stream dependencies
        # self.store_diff 
        
        self.pull_base()

# ----------------------------------------------------------------------
#  Config Container
# ----------------------------------------------------------------------

class Container(ContainerBase):
    """ SUAVE.Core.DiffedData.Container()
    """
    def append(self,value):
        try: value.store_diff()
        except AttributeError: pass
        ContainerBase.append(self,value)
        
    def pull_base(self):
        for config in self:
            try: config.pull_base()
            except AttributeError: pass

    def store_diff(self):
        for config in self:
            try: config.store_diff()
            except AttributeError: pass
    
    def finalize(self):
        for config in self:
            try: config.finalize()
            except AttributeError: pass


# ------------------------------------------------------------
#  Handle Linking
# ------------------------------------------------------------

DiffedData.Container = Container
