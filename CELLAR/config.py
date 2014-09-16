'''
Created on 2014. 4. 27.

@author: Sonien Studio
'''
import json
import os
import CELLAR

from CELLAR.settings    import BASE_DIR
from SonienStudio.log   import *

class Config :    
    def __init__(self) :
        self.TITLE              = "Tiny Home Storage"
        self.ROOT               = ""
        self.HOME_GUEST         = ""
        self.HOME_USER          = ""
#         self.DIR_ROOT           = ""
#         self.DIR_HOME_GUEST     = ""
#         self.DIR_HOME_USER   = ""
        
        self.DEFAULT_AUTH_DIR_READABLE  = True
        self.DEFAULT_AUTH_DIR_WRITEABLE = True
        self.DEFAULT_AUTH_DIR_DELETABLE = True
        self.DEFAULT_AUTH_DIR_INHERIT   = True
        
        self.USING_GUEST        = True
        self.SUGGEST_LOGIN      = True    
        
        self.load()
    
#     def setRoot(self, path) :
#         self.ROOT       = path
#         self.DIR_ROOT   = path
    
#     def setHomeDefault(self, path) :
#         self.HOME_USER       = path
#         self.DIR_HOME_USER = self.ROOT
#         if self.HOME_USER : 
#             self.DIR_HOME_USER += "/" + self.HOME_USER

#     def setHomeGuest(self, path) :
#         self.HOME_GUEST         = path
#         self.DIR_HOME_GUEST = self.ROOT
#         if self.HOME_GUEST :
#             self.DIR_HOME_GUEST += "/" + self.HOME_GUEST

    def getPathHomeDefault(self): 
    	return (self.ROOT, self.ROOT + "/" + self.HOME_USER)[self.HOME_USER != ""]
    
    def getPathHomeGuest(self): 
        return (self.ROOT, self.ROOT + "/" + self.HOME_GUEST)[self.HOME_GUEST != ""]
    
    def load(self) :
        try :
            fp = None
            fp = open(os.path.join(BASE_DIR, "THS/THS.conf"))
            conf = json.load(fp)
            for key in conf :
                value = conf[key]
                if value == "true" :
                    value = True
                elif value == "false" :
                    value = False
                
                # globals()[key] = value
                vars(self)[key] = value
                info("Configuration : {0} = {1}".format(key, value) )
                
                # for line in conf :
                #     match = re.search("(?P<param>[a-zA-Z_]*)\s*=\s*(?P<value>.*)", line)
                #     if not match :  continue
                #     param = match.group("param")
                #     value = match.group("value")                
        except Exception as err :
            warn("Configuration file is not exists or broken.")
        finally:
            if fp : fp.close()
        
        # 컨피그 초기화
#         self.DIR_ROOT = self.ROOT
#         self.setHomeDefault(self.HOME_USER)
#         self.setHomeGuest(self.HOME_GUEST)
    
    def save(self) :
        profile = {
            "TITLE"                         : self.TITLE,
            "ROOT"                          : self.ROOT,
            "HOME_GUEST"                    : self.HOME_GUEST,
            "HOME_USER"                     : self.HOME_USER,
            "DEFAULT_AUTH_DIR_INHERIT"      : self.DEFAULT_AUTH_DIR_INHERIT,
            "DEFAULT_AUTH_DIR_READABLE"     : self.DEFAULT_AUTH_DIR_READABLE,
            "DEFAULT_AUTH_DIR_WRITEABLE"    : self.DEFAULT_AUTH_DIR_WRITEABLE,
            "DEFAULT_AUTH_DIR_DELETABLE"    : self.DEFAULT_AUTH_DIR_DELETABLE,
            "USING_GUEST"                   : self.USING_GUEST,
            "SUGGEST_LOGIN"                 : self.SUGGEST_LOGIN
        }
        
        
        fp = open(os.path.join(BASE_DIR, "THS/THS.conf"),  "w")
        fp.write(json.dumps(profile))
        fp.close()
