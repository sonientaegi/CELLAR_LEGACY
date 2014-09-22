"""
Created on 2014.04.xx.
@author: SonienTaegi

Get, set, delete and reset index value of target. 
Index will be unique identifier of targets serving by CELLAR.
"""

import os.path

from CELLAR import config
from SonienStudio.log   import error, ok, info


INDEX_FILE = ".file_id.CELLAR"

def dir_get(fullPath):
    """
    Get file_id of index file in fullPath. Will return None unless there is an file_id file.
    """  
    try :
        file = open(os.path.normpath(fullPath + INDEX_FILE))
        file_id = int(file.read())
        file.close()
        return file_id
          
    except Exception as err :
        # error("index.dir.get : " + err.__str__())
        return None

def dir_set(fullPath, file_id):
    """
    Set or update file_id of index file in fullPath. Will return False unless it is done successfully. 
    """
    try :
        file = open(os.path.normpath(fullPath + INDEX_FILE), mode='w')
        file.write(str(file_id))
        file.close()
        return True
    
    except Exception as err :
        error("index.dir.set : " + err.__str__())
        return False    
    
def dir_del(fullPath):
    """
    Delete index file of fullPath. Will return False unless it is done successfully.
    """
    indexPath = os.path.normpath(fullPath + INDEX_FILE)
    try :
        os.remove(indexPath)
        ok("index.dir.del : " + fullPath )
        return True
    except Exception as err :
        # error("index.dir.del : " + err.__str__())
        return False
     
def dir_reset(fullPath = None):
    """
    Delete any or children index files of fullPath.
    @param fullPath replaces with ROOT if it is None.:  
    """    
    
    if fullPath is None :
        fullPath = config.ROOT
        
    if fullPath == config.ROOT :
        info("index.dir.reset.full : start")
    
    dir_del(fullPath)            
    for child in os.listdir(fullPath) :
        try : 
            childPath = fullPath + os.path.sep + child
            if os.path.isfile(childPath) : continue
            
            dir_reset(childPath)
        except Exception as err :  
            error("index.dir.reset : " + err.__str__())
    
    if fullPath == config.ROOT :
        ok("index.dir.reset.full : finished")
        
    return True
