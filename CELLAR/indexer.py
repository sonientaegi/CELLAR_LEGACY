import os.path

from CELLAR             import config
from SonienStudio.log   import error, info


DESCRIPTOR = ".CELLAR"

def getDirIndex(fullPath):
    """
    Directory 식별자를 조회한다. 식별자 미 설정 시 none 을 반환한다.
    """
    try :
        file = open(os.path.normpath(fullPath + DESCRIPTOR))
        index = int(file.read())
        file.close()
        return index
          
    except IOError as err:
        error("getDirIndex : " + err.__str__())
        return None

def setDirIndex(fullPath, index):
    """
    Directory 식별자를 설정한다. 식별자 미 설정 시 none 을 반환한다. 
    """
    try :
        file = open(os.path.normpath(fullPath + DESCRIPTOR), mode='w')
        file.write(str(index))
        file.close()
        return True
    
    except IOError as err :
        error("setDirIndex : " + err.__str__())
        return False    
    
def delDirIndex(fullPath):
    """
    Directory 식별자를 삭제한다. 성공 시 참을 반환한다.
    """
    descriptor = fullPath + DESCRIPTOR
    try :
        os.remove(descriptor)
        info("REMOVE DESCRIPTOR " + fullPath )
        return True
    except IOError as err :
        error(err.__str__())
        return False
     
def resetDirIndex(path = None):
    """
    Directory 식별자를 전체 삭제 한다. 성공 시 참을 반환한다.
    """    
    global config
    if path is None :
        path = config.ROOT

    if os.path.exists(path + os.sep + DESCRIPTOR) : 
        try :
            os.remove(path + os.sep + DESCRIPTOR)
            info("REMOVE DESCRIPTOR " + path )
        except IOError as err:  
            error(err.__str__())
    
    try : 
        path = path + os.path.sep
        for child in os.listdir(path) :
            childPath = path + child
            if os.path.isfile(childPath) :  continue
            
            resetDirIndex(childPath)
    except IOError as err:  
        error(err.__str__())

    return True
