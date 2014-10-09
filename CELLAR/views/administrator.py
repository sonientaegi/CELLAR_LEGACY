'''
Created on 2014. 9. 19.c

@author: SonienTaegi
'''

import re

from django.contrib.auth.models import User
from django.contrib.auth.views  import login
from django.http.response       import HttpResponse
from django.shortcuts           import render, redirect

from CELLAR                     import config
from CELLAR.models              import UserInfo, UserGroups
from CELLAR.views.util          import isChecked, restart, userCreate
from SonienStudio.log           import error


def general(request, *args, **kwargs):
    userinfo = UserInfo.getUserInfo(request)
      
    isSubmitted = request.POST.get("isSubmitted");
    pageYOffset = "0";
      
    if userinfo.isAdmin() and isSubmitted :
        config.TITLE            = request.POST.get("title")
        config.ROOT             = request.POST.get("root")
        config.HOME_USER        = request.POST.get("home_user")
        config.HOME_GUEST       = request.POST.get("home_guest")
        config.USING_GUEST      = isChecked(request,"using_guest")
        config.LOGIN_CAMPAIGN   = isChecked(request,"login_campaign")
        config.INDEX_FILE       = request.POST.get("index_file")       
          
        config.DEFAULT_AUTH_DIR_READABLE    = isChecked(request,"default_readable") 
        config.DEFAULT_AUTH_DIR_WRITEABLE   = isChecked(request,"default_writeable")
        config.DEFAULT_AUTH_DIR_DELETABLE   = isChecked(request,"default_deletable")
        config.DEFAULT_AUTH_DIR_INHERIT     = isChecked(request,"default_inherit")
        
        config.save()
          
        pageYOffset = request.POST.get("pageYOffset")
          
        restart(userinfo)
      
    context = { 
           "config"         : vars(config), 
           "pageYOffset"    : pageYOffset,
           "isAdmin"        : UserInfo.getUserInfo(request).isAdmin()
        } 
    return HttpResponse(render(request, "admin_general.html", context ))


def userNew(request, *args, **kwargs):
    context = {}
    userinfo = UserInfo.getUserInfo(request)
    
    if request.POST.get("signup") :
        response = userCreate(request.POST, userinfo.isAdmin())
       
        if response["code"] == 0 :
            context["code"]     = 0
            context["message"]  = "사용자 {0} 이(가) 등록되었습니다.".format(response["username"])
        else :
            response["isAdmin"] = userinfo.isAdmin()
            return HttpResponse(render(request, "admin_user_new.html", response ))
        
    context["isAdmin"]  = userinfo.isAdmin()
    return HttpResponse(render(request, "admin_user_new.html", context))

def userEdit(request, *args, **kwargs):
    user_group = { 'group' : [], 'user' : []}
    users = []
    if request.POST.get('user.group.update') :
        username    = request.POST.get('username')
        groupname   = request.POST.get('groupname')
        assign      = request.POST.get('assign') == 'True' or request.POST.get('assign') == 'true'
            
        if assign :
            user        = UserInfo.objects.get(username=username)
            group       = UserInfo.objects.get(username=groupname)
            userGroup   = UserGroups(user=user, group=group)
            userGroup.save()
        else :
            userGroup   = UserGroups.objects.get(user=username, group=groupname)
            userGroup.delete()
            
        if request.is_ajax() :
            return HttpResponse({"username" : username, "groupname" : groupname, "assign" : assign })
        else :
            users = UserInfo.objects.filter(username=username)
    else :
        search_term = request.POST.get("user.group.search.term")
        if not search_term or not request.POST.get('user.group.search') :
            search_term = ""
        users = UserInfo.objects.filter(username__contains=search_term).exclude(usertype=UserInfo.GROUP)
            
    general = 0
    groupIndex = {}
    groups = list(UserInfo.objects.filter(usertype=UserInfo.GROUP))
    for group in groups :
        auth_group = User.objects.get(username=group.username)
        groupIndex[group.username] = general
        general = general + 1
        user_group['group'].append([general, {'username'     : group.username,
                                            'first_name'   : auth_group.first_name,
                                            'last_name'    : auth_group.last_name }])
            
    for userinfo in users :
        auth_user = User.objects.get(username=userinfo.username)
        user = {'username'      : userinfo.username, 
                'first_name'    : auth_user.first_name, 
                'last_name'     : auth_user.last_name,
                'usertype'      : userinfo.usertype,
                'isAdmin'       : userinfo.isAdmin(), 
                'assign'        : [] }
        for group in groups :
            user['assign'].append([group.username, False])
            
        userGroups = UserGroups.objects.filter(user=userinfo.username)
        for userGroup in userGroups :
            user['assign'][groupIndex[userGroup.group.username]][1] = True
            
        user_group['user'].append(user)
      
    context = {
        'user_group'    : user_group,
        'config'        : vars(config),
        'isAdmin'       : UserInfo.getUserInfo(request).isAdmin()
    }
    return render(request, "admin_user_edit.html", context)     
    
def etc(request, *args, **kwargs):
    context = {
        'config'        : vars(config),
        'isAdmin'       : UserInfo.getUserInfo(request).isAdmin()
    }
    return HttpResponse(render(request, "admin_etc.html", context))