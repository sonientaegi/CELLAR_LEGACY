import json
import os

import CELLAR
from CELLAR.settings    import BASE_DIR
from SonienStudio.log   import *

class __Config : 
    def __init__(self) :
        self.TITLE              = "CELLAR - TINY WEB STORAGE"
        self.ROOT               = ""
        self.HOME_GUEST         = ""
        self.HOME_USER          = ""
               
        self.DEFAULT_AUTH_DIR_READABLE  = True
        self.DEFAULT_AUTH_DIR_WRITEABLE = True
        self.DEFAULT_AUTH_DIR_DELETABLE = True
        self.DEFAULT_AUTH_DIR_INHERIT   = True
        
        self.USING_GUEST        = True
        self.LOGIN_CAMPAIGN     = True    
        
        self.load()

    def getHomeDefault(self): 
        return (self.ROOT, self.ROOT + "/" + self.HOME_USER)[self.HOME_USER != ""]
    
    def getHomeGuest(self): 
        return (self.ROOT, self.ROOT + "/" + self.HOME_GUEST)[self.HOME_GUEST != ""]
    
    def load(self) :
        try :
            info("Load configuration...")
            fp = None
            fp = open(os.path.join(BASE_DIR, "CELLAR/CELLAR.conf"))
            conf = json.load(fp)
            for key in conf :
                value = conf[key]
                if value == "true" :
                    value = True
                elif value == "false" :
                    value = False
                
                # globals()[key] = value
                vars(self)[key] = value
                # info("%30s = %s" % (key, value))
                info("{0:30s} = {1}".format(key, value))
            
                
                # for line in conf :
                #     match = re.search("(?P<param>[a-zA-Z_]*)\s*=\s*(?P<value>.*)", line)
                #     if not match :  continue
                #     param = match.group("param")
                #     value = match.group("value")
            ok("Load successfully!")                
        except Exception as err :
            warn("Configuration file is not exists or broken.")
        finally:
            if fp : fp.close()
    
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
            "LOGIN_CAMPAIGN"                : self.LOGIN_CAMPAIGN
        }
        
        
        fp = open(os.path.join(BASE_DIR, "CELLAR/CELLAR.conf"),  "w")
        fp.write(json.dumps(profile))
        fp.close()
config = __Config()

from CELLAR             import views

