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
from SonienStudio.log           import error


def copyrightPage(request, *args, **kwrags):
    return HttpResponse(render(request, "copyright.html"))

def main(request, *args, **kwargs):
    context = {
        "config"    : config,
        "isSuper"   : UserInfo.getUserInfo(request).isSuper()
    } 
    return HttpResponse(render(request, "cellar.html", context))

def directree(request, *args, **kwargs):
    return HttpResponse(render(request, "module_directree.html", { "is_ajax" : request.is_ajax() }))
 
def filelist(request, *args, **kwargs):
    return HttpResponse(render(request, "module_filelist.html", { "is_ajax" : request.is_ajax() }))

def upload(request, *args, **kwargs):
    cwd = request.POST.get("cwd")
    return HttpResponse(render(request, "module_upload.html", {"cwd" : cwd }))

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
            response["isSuper"] = False
            return HttpResponse(render(request, "user_register.html", response ))
        
    else :
        return HttpResponse(render(request, "user_register.html", { "isSuper" : False } ))
    
