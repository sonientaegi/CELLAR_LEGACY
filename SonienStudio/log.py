'''
Created on 2014. 6. 27.

@author: Sonien Taegi
'''
from datetime import datetime


_LOG_TYPE = [" OK ", "WARN", "DAMN", "INFO"]

def ok(text) :
    _log(0, text)
    
def warn(text) :
    _log(1, text)

def error(text) :
    _log(2, text)

def info(text) :
    _log(3, text)

def _log(type, text):
    print("{0} [{1}] {2}".format(datetime.now(), _LOG_TYPE[type], text))
