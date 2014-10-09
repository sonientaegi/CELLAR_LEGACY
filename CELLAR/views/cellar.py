'''
Created on 2014. 9. 19.

@author: SonienTaegi
'''
import re

from django.contrib.auth.models import User
from django.contrib.auth.views  import login
from django.http.response       import HttpResponse
from django.shortcuts           import render, redirect

from CELLAR                     import config
from CELLAR.models              import UserInfo
from CELLAR.views.util          import userCreate
from SonienStudio import log
from SonienStudio.log           import error


def copyrightPage(request, *args, **kwrags):
    return HttpResponse(render(request, "copyright.html"))

def _getContext(request) :
    userInfo = UserInfo.getUserInfo(request) 
    return {
        "config"    : config,
        "isAdmin"   : userInfo.isAdmin(),
        "isSuper"   : userInfo.isSuper(),
        "is_ajax"   : request.is_ajax()
    } 
    
def main(request, *args, **kwargs):
    context = {
        
    } 
    return HttpResponse(render(request, "cellar.html", _getContext(request)))

def directree(request, *args, **kwargs):
    return HttpResponse(render(request, "module_directree.html", _getContext(request) ))
 
def filelist(request, *args, **kwargs):
    return HttpResponse(render(request, "module_filelist.html", _getContext(request) ))

def upload(request, *args, **kwargs):
    cwd = request.POST.get("cwd")
    context = _getContext(request)
    context["cwd"] = cwd
    return HttpResponse(render(request, "module_upload.html", context ))

def myinfo(request, *args, **kwargs):
    userinfo    = UserInfo.getUserInfo(request)
    user        = User.objects.get(username = userinfo.username )
     
    context = {
        "username"  : user.username,
        "name"      : user.first_name,
        "email"     : user.email,
        "memo"      : userinfo.memo
    }
    return HttpResponse(render(request, "user_myinfo.html", context))

def signup(request, *args, **kwargs):
    if request.POST.get("signup") :
        response = userCreate(request.POST)
       
        if response["code"] == 0 :
            login(request, response["user"])
            return redirect("/")
        else :
            response["isAdmin"] = False
            return HttpResponse(render(request, "user_register.html", response ))
        
    else :
        return HttpResponse(render(request, "user_register.html", _getContext(request) ))

def authorityManager(request, *args, **kwargs) :
    """
    auth_type 
        4 : Read
        2 : Write
        1 : Delete
    """    
    cwd = request.POST.get("path")
    auth_type = request.POST.get("auth_type")
    if auth_type :
        auth_type = int(auth_type)
    else :
        auth_type = 4 
     
    response = render(request, "auth_manager.html", {'cwd' : cwd, 'auth_type' : auth_type})
    log.info(response.content)
    return HttpResponse(response)    
