'''
Created on 2014. 4. 27.

@author: Sonien Taegi
'''
"""
Index 페이지를 호출한다.
"""
from builtins                   import Exception
from datetime                   import datetime
import json
import os
import re
from subprocess                 import call
from wsgiref.util               import FileWrapper

from django.contrib.auth        import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.views  import login, logout 
from django.core.urlresolvers   import reverse
from django.db                  import transaction
from django.db.utils            import IntegrityError
from django.http                import HttpResponse
from django.http.response       import HttpResponseRedirect, StreamingHttpResponse, \
                                       HttpResponseNotAllowed, HttpResponseServerError
from django.shortcuts           import render, redirect

from CELLAR                     import config, index
from CELLAR                     import util
from CELLAR.authority           import Directory
from CELLAR.models              import UserInfo, UserGroups, FileDescriptor, UserAuthority
from CELLAR.util                import CELLAR_FileManager
from SonienStudio.file          import FileManager
from SonienStudio.log           import error, info
from SonienStudio.tarstream     import TarStream

global config

def copyrightPage(request, *args, **kwrags):
    return HttpResponse(render(request, "copyright.html"))

def index(request, *args, **kwargs):
    context = {
        "config"    : config,
        "isSuper"   : UserInfo.getUserInfo(request).isSuper()
    } 
    return HttpResponse(render(request, "index.html", context))

"""
관리자 페이지를 연다 
"""
def administrator(request, *args, **kwargs):
    userinfo = UserInfo.getUserInfo(request)
      
    isSubmitted = request.POST.get("isSubmitted");
    pageYOffset = "0";
      
    if userinfo.isSuper() and isSubmitted :
#         config.setRoot(request.POST.get("ths_root"))
#         config.setHomeGuest(request.POST.get("guest_root"))
#         config.setHomeDefault(request.POST.get("user_root"))
        config.TITLE            = request.POST.get("title")
        config.ROOT             = request.POST.get("root")
        config.HOME_USER        = request.POST.get("home_user")
        config.HOME_GUEST       = request.POST.get("home_guest")
        config.USING_GUEST      = isChecked(request,"using_guest")
        config.LOGIN_CAMPAIGN   = isChecked(request,"login_campaign")
          
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
           "isSuper"        : UserInfo.getUserInfo(request).isSuper()
        } 
    return HttpResponse(render(request, "admin_general.html", context ))
 
# def administrator_user_edit(request, *args, **kwargs):
#     user_group = { 'group' : [], 'user' : []}
#     users = []
#     if request.POST.get('user.group.update') :
#         username    = request.POST.get('username')
#         groupname   = request.POST.get('groupname')
#         assign      = request.POST.get('assign') == 'True' or request.POST.get('assign') == 'true'
#            
#         if assign :
#             user        = UserInfo.objects.get(username=username)
#             group       = UserInfo.objects.get(username=groupname)
#             userGroup   = UserGroups(user=user, group=group)
#             userGroup.save()
#         else :
#             userGroup   = UserGroups.objects.get(user=username, group=groupname)
#             userGroup.delete()
#            
#         if request.is_ajax() :
#             return HttpResponse({"username" : username, "groupname" : groupname, "assign" : assign })
#         else :
#             users = UserInfo.objects.filter(username=username)
#     else :
#         search_term = request.POST.get("user.group.search.term")
#         if search_term and request.POST.get('user.group.search') :
#             users = UserInfo.objects.filter(username__contains=search_term, usertype__in=[UserInfo.NORMAL, UserInfo.SUPER])
#         else :
#             users = UserInfo.objects.filter(usertype__in=[UserInfo.NORMAL, UserInfo.SUPER])
#            
#     index = 0
#     groupIndex = {}
#     groups = list(UserInfo.objects.filter(usertype=UserInfo.GROUP))
#     for group in groups :
#         auth_group = User.objects.get(username=group.username)
#         groupIndex[group.username] = index
#         index = index + 1
#         user_group['group'].append([index, {'username'     : group.username,
#                                             'first_name'   : auth_group.first_name,
#                                             'last_name'    : auth_group.last_name }])
#            
#     for userinfo in users :
#         auth_user = User.objects.get(username=userinfo.username)
#         user = {'username'      : userinfo.username, 
#                 'first_name'    : auth_user.first_name, 
#                 'last_name'     : auth_user.last_name,
#                 'isSuper'       : userinfo.isSuper(), 
#                 'assign'        : [] }
#         for group in groups :
#             user['assign'].append([group.username, False])
#            
#         userGroups = UserGroups.objects.filter(user=userinfo.username)
#         for userGroup in userGroups :
#             user['assign'][groupIndex[userGroup.group.username]][1] = True
#            
#         user_group['user'].append(user)
#      
#     context = {
#         'user_group'    : user_group,
#         'config'        : vars(config),
#         'isSuper'       : UserInfo.getUserInfo(request).isSuper()
#     }
#     return render(request, "admin_user_edit.html", context)     
#  
# def administrator_user_new(request, *args, **kwargs):
#     user_create = {}
#        
#     if request.POST.get("user_create") :        
#         is_group    = request.POST.get('is_group')
#         username    = request.POST.get('username')
#         password    = request.POST.get("password")
#         email       = request.POST.get("email")
#         first_name  = request.POST.get("first_name")
#         memo        = request.POST.get("memo")
#          
#         # 최고 관리자에 의해 등록되는 ID 는 E-MAIL 은 필요 없음
#         if not email and request.user.is_superuser :
#             email = ""
#            
#         if is_group and not request.user.is_superuser :
#             user_create['message'] = '그룹 사용자는 관리자만이 추가할 수 있습니다.'
#         elif not re.match("[a-zA-Z0-9]{6,}|@[a-zA-Z0-9]{5,}", username) :
#             user_create['message'] = 'ID 는 6글자 이상의 영숫자로 작성해주세요.'
#         elif is_group and not re.match("@.*", username) :
#             user_create['message'] = '그룹 사용자의 아이디는 @로 시작해야합니다.'
#         elif username and password and first_name and ( email or request.user.is_superuser ) :
#             try :
#                 usertype = UserInfo.NORMAL
#                 if is_group :
#                     usertype = UserInfo.GROUP
#                         
#                 user = User.objects.create_user(username, email, password, first_name=first_name)
#                 userinfo = UserInfo(username=username, usertype=usertype, memo=memo)
#                 userinfo.save()
#                  
#                 if UserInfo.getUserInfo(request).isSuper() :
#                     user_create['message'] = '사용자가 등록되었습니다.'
#                     context = {
#                         'user_create'   : user_create,
#                         "isSuper"       : True
#                     }
#                     return HttpResponse(render(request, "admin_user_new.html", context ))
#                 else :
#                     login(request, user) 
#                     return redirect("/")
#             except Exception as err :
#                 error(err.__str__())
#                 user_create['message'] = '이미 존재하는 아이디 입니다.'
#         else :
#             user_create['message'] = '필수 항목을 입력하여주십시오.'
#            
#         if request.user.is_superuser and is_group :
#             user_create['is_group'] = is_group
#            
#         if username :
#             user_create['username'] = username
#                
#         if email :
#             user_create['email'] = email
#            
#         if first_name :
#             user_create['first_name'] = first_name
#            
#         if memo :
#             user_create['memo'] = memo  
#              
#     context = {
#         'config'        : vars(config),
#         'user_create'   : user_create,
#         'isSuper'       : UserInfo.getUserInfo(request).isSuper()
#     }
#     return HttpResponse(render(request, "admin_user_new.html", context))
#  
# def administrator_etc(request, *args, **kwargs):
#     return HttpResponse(render(request, "admin_etc.html", {}))
# 
# """
# 디렉토리 모듈을 생성한다.
# """
# def module_directree(request, *args, **kwargs):
#     return HttpResponse(render(request, "module_directree.html", { "is_ajax" : request.is_ajax() }))
# 
# """
# 파일리스트 모듈을 생성한다
# """
# def module_filelist(request, *args, **kwargs):
#     return HttpResponse(render(request, "module_filelist.html", { "is_ajax" : request.is_ajax() }))
# 
# """
# 파일 업로드 모듈을 생성한다.
# """ 
# def module_upload(request, *args, **kwargs):
#     cwd = request.POST.get("cwd")
#     return HttpResponse(render(request, "module_upload.html", {"cwd" : cwd }))
# 
# 
# def browse(request, *args, **kwrags):
#     targetDir = request.POST.get('target')
#     filelist = util.getFileGroup(request, targetDir)
#     directree = util.getDirTree(request, targetDir, 2)
# 
#     userinfo = UserInfo.getUserInfo(request)
#     auth = Directory.getAuthority(userinfo, userinfo.getUserHome() + targetDir)
#         
#     context = {
#         'target'    : targetDir,
#         'filelist'  : {
#                         'directory' : filelist[0],
#                         'file'      : filelist[1],
#                         'readable'  : auth[0],
#                         'writeable' : auth[1],
#                         'deletable' : auth[2] 
#                        },
#         'directree' : {
#                         'node'      : directree
#                       }
#     }
#     
# #     for dirPath in directree :
# #         log.info("Browse " + dirPath[1] + " " + str(len(dirPath[1])))
#     log.info("browse " + targetDir)    
#     return HttpResponse(json.dumps(context))
# 
# def browse_filelist(request, *args, **kwrags):
#     targetDir = request.POST.get('target')
#     result = util.getFileGroup(request, targetDir)
#     
#     userinfo = UserInfo.getUserInfo(request)
#     auth = Directory.getAuthority(userinfo, userinfo.getUserHome() + targetDir)
#      
#     context = {
#         'target'    : targetDir,
#         'directory' : result[0],
#         'file'      : result[1],
#         'readable'  : auth[0],
#         'writeable' : auth[1],
#         'deletable' : auth[2]
#     }
#     
#     log.info("browse filelist of " + targetDir)
#     return HttpResponse(json.dumps(context))    
# 
# def browse_directory(request, *args, **kwrags):
#     targetDir = request.POST.get('target')
#     result = util.getDirTree(request, targetDir, 2)
#     
#     context = {
#         'target'    : targetDir,
#         'node'      : result 
#     }
#     
#     return HttpResponse(json.dumps(context))
# 
#  
# """
# 파일을 다운로드 한다.
# kwargs    
#     path     : 다운로드할 파일의 sub path ( /subpath/filename.ext )
# """
# def download(request, *args, **kwargs):
#     fullPath = os.path.join(UserInfo.getUserInfo(request).getUserHome(), kwargs['path'])
#      
#     # 권한 확인
#     
#     filename = (os.path.basename(fullPath))
#     response = StreamingHttpResponse(FileWrapper(open(fullPath, mode='rb')), content_type='application/octet-stream')
#     response['Content-Length'] = os.path.getsize(fullPath)    
#     response['Content-Disposition'] = 'attachment'
#     
#     return response
# 
# """
# 파일을 TAR 로 묶어서 다운받는다.
# POST
#     baseDir    : 파일들이 저장 된 디렉토리
#     files[]    : 다운 받을 대상
# """
# def tarload(request, *args, **kwargs):        
#     baseDir = request.POST.get('baseDir')
#     fullDir = UserInfo.getUserInfo(request).getUserHome() + baseDir 
#     files = request.POST.getlist('files[]')
#     
#     # 권한 확인
#     
#     dirs = baseDir.split("/");
#     while "" in dirs :
#         dirs.remove("")
#     dirs.reverse()
# 
#     tarStream = TarStream.open(fullDir, 128)
#     for file in files :
#         tarStream.add(file)
#     
#     response = StreamingHttpResponse(tarStream, content_type='application/x-tar')
#     response['Content-Length'] = tarStream.getTarSize() 
#     response['Content-Disposition'] = 'attachment'
#        
#     return response
#     
# """ 
# AJAX file util for THS
# 
# * Response
# {
#     ### Common    ###
#     "code"    : 0 is OK, others are for each error
#     "message" : Message. Must not be null. Can be empty 
# 
#     ### Additonal ###
#     Each functions provide additional information
# }
# """
#  
# def util_rename(request, *args, **kwargs):
#     """
#     * Common 
#     0 : "SUCCESS",
#     1 : "파일/경로를 찾을 수 없습니다",
#     2 : "변경하려는 대상이 존재합니다",
#     3 : "허용되지 않는 요청입니다",
#     4 : "오류가 발생하였습니다",
#     5 : "권한이 없습니다",
#     
#     * Additional 
#     dst     : New name. Not valid in error.
#     dstPath : New path. Not valid in error. 
#     """
#     if not request.is_ajax() :
#         log.error("File util for THS supports AJAX only")
#         return HttpResponseNotAllowed("Supports AJAX only")
#       
#     srcPath = request.POST.get('srcPath');
#     dst = request.POST.get('dst');
#     dstPath = os.path.normpath(srcPath + os.path.sep + os.pardir + os.path.sep + dst)
#     fileManager = THSFileManager(request) 
#     code = fileManager.rename(srcPath, dstPath)
#     if code == 0 and os.path.isdir(fileManager.getFullPath(dstPath)) :
#         dstPath += "/"
#         
#     message = {
#         0 : "SUCCESS",
#         1 : "파일/경로를 찾을 수 없습니다",
#         2 : "변경하려는 대상이 존재합니다",
#         3 : "허용되지 않는 요청입니다",
#         4 : "오류가 발생하였습니다",
#         5 : "권한이 없습니다",
#     }
#     response = {
#         "code"      : code,
#         "message"   : message[code],
#         "dst"       : dst,
#         "dstPath"   : dstPath
#     }
#     return HttpResponse(json.dumps(response))
# 
# def util_renameGroup(request, *args, **kwargs):
#     """
#     * Common 
#     0 : "SUCCESS",
#     1 : "파일을 찾을 수 없습니다",
#     2 : "변경하려는 대상이 존재합니다",
#     3 : "허용되지 않는 요청입니다",
#     4 : "오류가 발생하였습니다",
#     5 : "권한이 없습니다",
#     
#     * Additional 
#     dstGroup    : New group path. Not valid in error. 
#     result      : [ (ext, errno, dstPath), (ext, errno dstPath), ... ] 
#     """
#     if not request.is_ajax() :
#         log.error("File util for THS supports AJAX only")
#         return HttpResponseNotAllowed("Supports AJAX only")
#       
#     srcGroup = request.POST.get('srcGroup');
#     srcExts = request.POST.getlist('srcExts[]');
#     dst = request.POST.get('dst');
#     dstGroup = os.path.normpath(srcGroup + os.path.sep + os.pardir + os.path.sep + dst)
#     
#     fileManager = THSFileManager(request) 
#     result = []
#     code = 0
#     
#     for ext in srcExts :
#         newPath = ""
#         srcPath = srcGroup + ext
#         dstPath = dstGroup + ext
#         errno = fileManager.rename(srcPath, dstPath)
#         if errno :  code = errno
#         else : newPath = dstPath
#         
#         result.append([ext, errno, newPath])
#         
#     message = {
#         0 : "SUCCESS",
#         1 : "파일/경로를 찾을 수 없습니다",
#         2 : "변경하려는 대상이 존재합니다",
#         3 : "허용되지 않는 요청입니다",
#         4 : "오류가 발생하였습니다",
#         5 : "권한이 없습니다",
#     }
#     response = {
#         "code"      : code,
#         "message"   : message[code],
#         "dstGroup"  : dstGroup,
#         "result"    : result  
#     }
#     return HttpResponse(json.dumps(response))
# 
# 
# def util_move(request, *args, **kwargs):
#     """
#     * Common 
#     0 : "SUCCESS",
#     1 : "파일/경로를 찾을 수 없습니다",
#     2 : "이동하려는 위치가 파일입니다",
#     3 : "허용되지 않는 요청입니다",
#     4 : "오류가 발생하였습니다",
#     5 : "권한이 없습니다",
#     
#     * Additional 
#     dstPath : Destination path
#     result  : [ (target, errno, newPath), (target, errnom newPath), ... ] 
#     """
#     if not request.is_ajax() :
#         log.error("File util for THS supports AJAX only")
#         return HttpResponseNotAllowed("Supports AJAX only")
#     
#     targets = request.POST.getlist("targets[]")
#     dstPath = request.POST.get("dstPath")
#     fileManager = THSFileManager(request)
#     
#     result = []
#     code = 0
#     for target in targets :
#         newPath = ""
#         errno = fileManager.move(target, dstPath)
#         if errno :  code = errno
#         else : newPath = dstPath + os.path.basename(os.path.normpath(target))
#         
#         result.append([target, errno, newPath + "/"])
#     
#     message = {
#         0 : "SUCCESS",
#         1 : "파일/경로를 찾을 수 없습니다",
#         2 : "변경하려는 위치가 파일입니다",
#         3 : "허용되지 않는 요청입니다",
#         4 : "오류가 발생하였습니다",
#         5 : "권한이 없습니다",
#     }
#     response = {
#         "code"      : code,
#         "message"   : message[code],
#         "dstPath"   : dstPath,
#         "result"    : result  
#     }
#     return HttpResponse(json.dumps(response)) 
# 
# def util_upload(request, *args, **kwargs):
#     response = { "status" : "success", "message" : "" }
#     fileManager = THSFileManager(request)
#     filename = request.POST.get("name")
#     cwd = request.POST.get("cwd")
#     if not fileManager.isWriteable(cwd) :
#         response["status"] = "error"
#         response["message"] = "해당 경로에 쓰기 권한이 없습니다."
#         return HttpResponseServerError(json.dumps(response))
#     
#     file = request.FILES["file"]
#     if not file :
#         response["status"] = "error"
#         response["message"] = "파일이 정상적으로 업로드 되지 않았습니다."
#         return HttpResponseServerError(json.dumps(response))
#     
#     dstPath = fileManager._root_norm + cwd + filename
#     chunk = int(request.POST.get("chunk"))
#     chunks = int(request.POST.get("chunks"))
#     
#     log.info("Upload in  " + dstPath)
#     log.info("{0} / {1}".format(chunk + 1, chunks))
#     
#     if chunk == 0 :
#         mode = "wb"
#     else :
#         mode = "ab"
#     
#     with open(dstPath, mode) as destination:
#         destination.write(file.file.read())
#     file.file.close()
#     log.info("Upload out " + dstPath)
#     return HttpResponse(json.dumps(response)) 
# 
# def util_createDir(request, *args, **kwargs):
#     """
#     * Common 
#     0 : "SUCCESS",
#     1 : "생성 위치가 존재하지 않습니다",
#     2 : "생성 위치가 파일입니다",
#     3 : "허용되지 않는 요청입니다",
#     4 : "오류가 발생하였습니다",
#     5 : "권한이 없습니다",
#     
#     * Additional 
#     newPath : 생성된 새 경로 
#     """
#     
#     """ AJAX only """
#     if not request.is_ajax() :
#         return HttpResponseNotAllowed("Support AJAX only")
#     
#     parentPath = request.POST.get("parentPath")
#     dirName = request.POST.get("dirName")
#     newPath = parentPath + dirName + "/"
#     log.info("createDir " + type(newPath).__name__ + " " + str(len(newPath)))
#     
#     fileManager = THSFileManager(request) 
#     code = fileManager.mkdir(parentPath, dirName)
#          
#     message = {
#         0 : "SUCCESS",
#         1 : "생성 위치가 존재하지 않습니다",
#         2 : "생성 위치가 파일입니다",
#         3 : "허용되지 않는 요청입니다",
#         4 : "오류가 발생하였습니다",
#         5 : "권한이 없습니다",
#     }
#     response = {
#         "code"      : code,
#         "message"   : message[code],
#         "newPath"   : newPath,
#     }
#     return HttpResponse(json.dumps(response)) 
# 
# def util_deleteDir(request, *args, **kwargs):
#     """
#     0 : 성공
#     1 : 대상이 파일입니다
#     2 : -
#     3 : 허용되지 않은 요청입니다
#     4 : 오류가 발생하였습니다
#     5 : 권한 없음
#     """
#     
#     """ AJAX only """
#     if not request.is_ajax() :
#         return HttpResponseNotAllowed("Support AJAX only")
#     
#     dirPath = request.POST.get("dirPath")
#     log.info("deleteDir " + dirPath)
#     
#     fileManager = THSFileManager(request) 
#     code = fileManager.rmdir(dirPath)
#     
#     message = {
#         0 : "성공",
#         1 : "대상이 파일입니다",
#         2 : "",
#         3 : "허용되지 않은 요청입니다",
#         4 : "오류가 발생하였습니다",
#         5 : "권한 없음"
#     }
#     response = {
#         "code"      : code,
#         "message"   : message[code],
#         "dirPath"   : dirPath  
#     }
#     return HttpResponse(json.dumps(response))
#     
# def util_deleteFiles(request, *args, **kwargs): 
#     """
#     
#     return {
#         ...
#         exts : [(ext, errno), ...]
#     }
#     
#     0 : 성공
#     1 : 대상이 경로입니다
#     2 : -
#     3 : 허용되지 않은 요청입니다
#     4 : 오류가 발생하였습니다
#     5 : 권한 없음
#     """
#     
#     """ AJAX only """
#     if not request.is_ajax() :
#         return HttpResponseNotAllowed("Support AJAX only")
#     
#     groupPath = request.POST.get("groupPath")
#     exts = request.POST.getlist("exts[]")
#     log.info("deleteFileGroup " + groupPath + " (" + exts.__str__() + ")")
#     
#      
#     targetPath = os.path.normpath(os.path.dirname(groupPath)) + "/"
#     filegroup = os.path.basename(groupPath)
#     filenames = []
#     for ext in exts :
#         filenames.append(filegroup + ext)
#     
#     fileManager = THSFileManager(request)
#     resultSet = fileManager.rmfiles(targetPath, filenames)
#     result = []
#     code = 0
#     
#     for row in resultSet :
#         result.append((os.path.splitext(row[0])[1], row[1]))
#         if row[1] is not 0 :
#             code = row[1]
#     
#         
#     message = {
#         0 : "성공",
#         1 : "대상이 경로입니다",
#         2 : "",
#         3 : "허용되지 않은 요청입니다",
#         4 : "오류가 발생하였습니다",
#         5 : "권한 없음"
#     }
#     response = {
#         "code"      : code,
#         "message"   : message[code],
#         "groupPath" : groupPath,
#         "result"    : result  
#     }
#     return HttpResponse(json.dumps(response))
# 
# def authority_reset(request, *args, **kwargs) :
#     response = {
#         "code"      : 0,
#         "message"   : ""
#     }
#     if not request.user.is_superuser :
#         response['code'] = -1
#         response['message'] = "최고 관리자만이 설정을 변경할 수 있습니다."
#     else :
#         # DB 초기화    
#         FileDescriptor.objects.all().delete()
#         UserAuthority.objects.all().delete()
#         FileDescriptor(id=0, file="", reference=None).save()  # 이건 더미
#     
#         util_index.resetDirIndex()
#         
#     return HttpResponse(json.dumps(response))
# 
# def authority_manager(request, *args, **kwargs) :
#     """
#     auth_type 
#         4 : Read
#         2 : Write
#         1 : Delete
#     """    
#     cwd = request.POST.get("path")
#     auth_type = request.POST.get("auth_type")
#     if auth_type :
#         auth_type = int(auth_type)
#     else :
#         auth_type = 4 
#     
#     
#     return HttpResponse(render(request, "auth_manager.html", {'cwd' : cwd, 'auth_type' : auth_type}))
# 
# def authority_getDefault(request, *args, **kwargs):
#     path = request.POST.get("path")
#     response = {
#         "path"      : path,
#         "register"  : False,
#         "readable"  : config.DEFAULT_AUTH_DIR_READABLE,
#         "writeable" : config.DEFAULT_AUTH_DIR_WRITEABLE,
#         "deletable" : config.DEFAULT_AUTH_DIR_DELETABLE,
#         "inherit"   : config.DEFAULT_AUTH_DIR_INHERIT
#     }
#     
#     userinfo = UserInfo.getUserInfo(request)
#     fullpath = userinfo.getUserHome() + path
#     index = util_index.getDirIndex(fullpath)
#     if index is not None :
#         fileDescriptor = FileDescriptor.objects.get(id=index)
#         response['register'] = True
#         response['readable'] = fileDescriptor.readable
#         response['writeable'] = fileDescriptor.writeable
#         response['deletable'] = fileDescriptor.deletable
#         response['inherit'] = fileDescriptor.inherit
# #         
#     return HttpResponse(json.dumps(response))
# 
# def authority_setDefault(request, *args, **kwargs):
#     path = request.POST.get("path")
#     response = {
#         "code"      : 0,
#         "message"   : "",
#         "path"      : path,
#         "register"  : False,
#         "readable"  : config.DEFAULT_AUTH_DIR_READABLE,
#         "writeable" : config.DEFAULT_AUTH_DIR_WRITEABLE,
#         "deletable" : config.DEFAULT_AUTH_DIR_DELETABLE,
#         "inherit"   : config.DEFAULT_AUTH_DIR_INHERIT
#     }
#     
#     userinfo = UserInfo.getUserInfo(request)
#     fullpath = userinfo.getUserHome() + request.POST.get("path")
#       
#     inherit = request.POST.get("inherit")
#     if inherit is not None :
#         inherit = inherit == "1"
# 
#     readable = request.POST.get("readable")
#     if readable is not None :
#         readable = readable == "1"
#      
#     writeable = request.POST.get("writeable")
#     if writeable is not None :
#         writeable = writeable == "1"
#      
#     deletable = request.POST.get("deletable")
#     if deletable is not None :
#         deletable = deletable == "1"
# 
#     result = Directory.set(fullpath, inherit, readable, writeable, deletable)
#     if result[0] >= 0 :
#         response["code"] = 0
#         response["message"] = result[1]
#         response['register'] = True
#         response['inherit'] = inherit
#         response['readable'] = readable
#         response['writeable'] = writeable
#         response['deletable'] = deletable
#     
#     return HttpResponse(json.dumps(response))
# 
# def authority_getUser(request, *args, **kwargs):
#     path = request.POST.get("path")
#     fileManager = THSFileManager(request)
#     response = {
#         "code"      : 0,
#         "message"   : "",
#         "path"      : path,
#         "register"  : False,
#         "readable"  : fileManager.isReadable(path),
#         "writeable" : fileManager.isWriteable(path),
#         "deletable" : fileManager.isDeletable(path)
#     }
#     
#     return HttpResponse(json.dumps(response))
# 
# def authority_delDefault(request, *args, **kwargs):
#     path = request.POST.get("path")
#     response = {
#         "code"      : 0,
#         "message"   : "",
#         "path"      : path,
#         "register"  : False,
#         "readable"  : config.DEFAULT_AUTH_DIR_READABLE,
#         "writeable" : config.DEFAULT_AUTH_DIR_WRITEABLE,
#         "deletable" : config.DEFAULT_AUTH_DIR_DELETABLE,
#         "inherit"   : config.DEFAULT_AUTH_DIR_INHERIT
#     }
#     
#     userinfo = UserInfo.getUserInfo(request)
#     fullpath = userinfo.getUserHome() + request.POST.get("path")
#     
#     if userinfo.usertype != UserInfo.SUPER :
#         response['code'] = 1
#         response['message'] = "최고 관리자만 가능합니다"
#     elif not Directory.delete(fullpath) : 
#         response["code"] = -1
#         response["message"] = "디렉토리 식별자 삭제 실패"
#         
#     return HttpResponse(json.dumps(response))
# 
# def authority_getUsers(request, *args, **kwargs):
#     response = {
#         "code"      : 0,
#         "message"   : "",
#         "users"     : []
#     }
#     
#     userinfo = UserInfo.getUserInfo(request)
#     fullpath = userinfo.getUserHome() + request.POST.get("path")
#     type = int(request.POST.get("type"))
#     
#     if userinfo.usertype == UserInfo.SUPER :
#         index = util_index.getDirIndex(fullpath)
#         if index is not None :
#             for user in UserAuthority.objects.filter(file_id=index)  :
#                 if      type & 4 and not user.readable     : continue
#                 elif    type & 2 and not user.writeable    : continue
#                 elif    type & 1 and not user.deletable    : continue
#                 
#                 response['users'].append([user.username.username,
#                                           user.username.getName(),
#                                           user.username.usertype])
#     else :
#         response['code'] = 1
#         response['message'] = "최고 관리자만 가능합니다"
#         
#     return HttpResponse(json.dumps(response))
# 
# def authority_setUsers(request, *args, **kwargs):
#     response = {
#         "code"      : 0,
#         "message"   : "",
#         "users"     : []
#     }
#     
#     userinfo = UserInfo.getUserInfo(request)
#     fullpath = userinfo.getUserHome() + request.POST.get("path")
#     type = request.POST.get("type")
#     ids = request.POST.getlist("ids[]")
#     readable = request.POST.get('readable')
#     readable = (readable == "1", None)[readable == None]
#     writeable = request.POST.get('writeable')
#     writeable = (writeable == "1", None)[writeable == None]
#     deletable = request.POST.get('deletable')
#     deletable = (deletable == "1", None)[deletable == None]
#     if userinfo.usertype == UserInfo.SUPER :         
#         index = util_index.getDirIndex(fullpath) 
#         if index is None :
#             index = Directory.set(fullpath, config.DEFAULT_AUTH_DIR_INHERIT, config.DEFAULT_AUTH_DIR_READABLE, config.DEFAULT_AUTH_DIR_WRITEABLE, config.DEFAULT_AUTH_DIR_DELETABLE)[0]
#         try :
#             with transaction.atomic() :
#                 for userinfo in UserInfo.objects.filter(username__in=ids) :
#                     userAuthority = None
#                     try :
#                         userAuthority = UserAuthority.objects.get(username=userinfo, file_id=index)
#                         if (readable  is not None and userAuthority.readable == readable) or \
#                            (writeable is not None and userAuthority.writeable == writeable) or \
#                            (deletable is not None and userAuthority.deletable == deletable) :
#                             continue
#                          
#                     except Exception as err :
#                         userAuthority = UserAuthority(username=userinfo, file_id=index)
#                          
#                     if readable is not None :
#                         userAuthority.readable = readable
#                     if writeable is not None :
#                         userAuthority.writeable = writeable
#                     if deletable is not None :
#                         userAuthority.deletable = deletable
#                     userAuthority.save()
#                     response['users'].append([
#                                 userinfo.username,
#                                 userinfo.getName(),
#                                 userinfo.usertype,
#                                 userAuthority.readable,
#                                 userAuthority.writeable,
#                                 userAuthority.deletable])
#                      
#         except Exception as err :
#             response['code'] = -2
#             response['message'] = err.__str__()
#             response['users'].clear()
#                 
#     else :
#         response['code'] = 1
#         response['message'] = "최고 관리자만 가능합니다"
#         
#     return HttpResponse(json.dumps(response))
#     
# def user_register(request, *args, **kwargs):
#     context = {}
#       
#     if request.POST.get("user.create") :
#         is_group = request.POST.get('is_group')
#         username = request.POST.get('username')
#         password = request.POST.get("password")
#         email = request.POST.get("email")
#         first_name = request.POST.get("first_name")
#         memo = request.POST.get("memo")
#           
#         if is_group and not request.user.is_superuser :
#             context['message'] = '그룹 사용자는 관리자만이 추가할 수 있습니다.'
#         elif not re.match("[a-zA-Z0-9]{6,}|@[a-zA-Z0-9]{5,}", username) :
#             context['message'] = 'ID 는 6글자 이상의 영숫자로 작성해주세요.'
#         elif is_group and not re.match("@.*", username) :
#             context['message'] = '그룹 사용자의 아이디는 @로 시작해야합니다.'
#         elif username and password and email and first_name :
#             try :
#                 usertype = UserInfo.NORMAL
#                 if is_group :
#                     usertype = UserInfo.GROUP
#                        
#                 user = User.objects.create_user(username, email, password, first_name=first_name)
#                 userinfo = UserInfo(username=username, usertype=usertype, memo=memo)
#                 userinfo.save()
#                   
#                 if request.user.is_superuser :
#                     context['message'] = '사용자가 등록되었습니다.'
#                     return HttpResponse(render(request, "user_register.html", {'user_create' : context}))
#                 else :
#                     login(request, user) 
#                     return redirect("/")
#             except Exception as err :
#                 log.error(err.__str__())
#                 context['message'] = '이미 존재하는 아이디 입니다.'
#         else :
#             context['message'] = '필수 항목을 입력하여주십시오.'
#           
#         if request.user.is_superuser and is_group :
#             context['is_group'] = is_group
#           
#         if username :
#             context['username'] = username
#               
#         if email :
#             context['email'] = email
#           
#         if first_name :
#             context['first_name'] = first_name
#           
#         if memo :
#             context['memo'] = memo    
#             
#     context = {
#         'user_create'   : context,
#         'isSuper'       : UserInfo.getUserInfo(request).isSuper()
#     }
#     return HttpResponse(render(request, "user_register.html", context ))
# 
# def user_get(request, *args, **kwargs):
#     userid      = request.POST.get("userid")
#     sessionInfo = UserInfo.getUserInfo(request)
#     
#     response = {
#         "code"      : "",
#         "message"   : ""
#     }
#     
#     if sessionInfo.isSuper() or request.user.username == userid :
#         result = UserInfo.objects.filter(username__exact = userid)
#         if not result.exists() :
#             response["code"] = -1
#             response["message"] = "존재하지 않는 아이디 입니다."
#         else :
#             userinfo = result[0]
#             user = User.objects.get(username = userinfo.username )
#             
#             response["userid"]      = userinfo.username
#             response["name"]        = user.first_name
#             response["email"]       = user.email
#             response["usertype"]    = userinfo.usertype
#             response["home"]        = userinfo.home 
#             response["memo"]        = userinfo.memo
#             
#             response["code"]        = 0
#     else :
#         response["code"] = -4
#         response["message"] = "권한이 없습니다."
#     
#     return HttpResponse(json.dumps(response))
# 
# def user_myinfo(request, *args, **kwargs):
#     userinfo    = UserInfo.getUserInfo(request)
#     user        = User.objects.get(username = userinfo.username )
#     
#     context = {
#         "username"  : user.username,
#         "name"      : user.first_name,
#         "email"     : user.email,
#         "memo"      : userinfo.memo
#     }
#     return HttpResponse(render(request, "user_myinfo.html", context))
#     
# def user_update(request, *args, **kwargs):
#     response = {
#         "code"      : "",
#         "message"   : "" 
#     }
#     
#     userid          = request.POST.get("userid")
#     usertype        = request.POST.get("usertype")
#     home            = None
#     name            = request.POST.get("name")
#     email           = request.POST.get("email")
#     memo            = request.POST.get("memo")
#     password_new    = request.POST.get("password_new")
#     password_old    = request.POST.get("password_old")
#     if request.POST.__contains__("home") :
#         home = request.POST.get("home")
#     
#     if usertype : usertype = int(usertype) 
#     
#     # 권한 확인 - 공통
#     user        = User.objects.get(username = userid)
#     userinfo    = UserInfo.objects.get(username = userid)
#     sessionInfo = UserInfo.getUserInfo(request)
#     if not sessionInfo.isSuper() and sessionInfo.username != userid :
#         response["code"]    = -4
#         response["message"] = "권한이 없습니다."
#         return HttpResponse(json.dumps(response))
#     
#     # 권한 확인 - 관리자
#     if not sessionInfo.isSuper() and ( home is not None or usertype ) :
#         response["code"]    = -5
#         response["message"] = "관리자만이 변경 가능한 항목을 포함하고 있습니다."
#         return HttpResponse(json.dumps(response))
#     
#     # 시스템 관리자는 계정 유형 변경 불가
#     if user.is_superuser and usertype and usertype != UserInfo.SUPER :
#         response["code"]    = -6
#         response["message"] = "시스템 관리자의 계정 유형을 변경할 수 없습니다."
#         return HttpResponse(json.dumps(response))
#     
#     # 암호 변경 요청 시 사용자 암호 확인
#     if password_new :
#         if sessionInfo.isSuper() and not password_old :
#             pass
#         elif authenticate(username = userid, password = password_old) :
#             pass
#         else :
#             response["code"]    = -3
#             response["message"] = "입력한 기존 암호가 잘못되었습니다."
#             return HttpResponse(json.dumps(response))
#     
#     try :
#         with transaction.atomic() :
#             # 사용자 정보 갱신
#             if email :
#                 user.email = email
#             if name :
#                 user.first_name = name
#             if password_new :
#                 user.set_password(password_new)
#             user.save()
#             
#             if home is not None :
#                 userinfo.home = home
#             if usertype :
#                 userinfo.usertype = usertype
#             if memo :
#                 userinfo.memo = memo
#             userinfo.save()
#             
#             response['code']    = 0
#             response['message'] = "사용자 정보가 변경되었습니다."
#             
#             response['userid']      = userid
#             response['name']        = user.first_name
#             response['email']       = user.email
#             response['home']        = userinfo.home
#             response['memo']        = userinfo.memo
#             response['usertype']    = userinfo.usertype
#              
#     except Exception as err :
#         response['code'] = -2
#         response['message'] = err.__str__()
#     
#     return HttpResponse(json.dumps(response))
#       
# def user_login(request, *args, **kwargs):
#     redirectURL = None
#     context = {}
#     
#     if request.POST.get("user.login") :
#         username = request.POST.get('username')
#         password = request.POST.get("password")
#         redirectURL = request.POST.get("redirectURL", "index")
#           
#         if username and password :
#             user = authenticate(username=username, password=password)
#             if user is not None and user.is_active :
#                 login(request, user) 
#                   
#                 # django 에서 직접 만든 ID 의 경우 UserInfo 가 누락되어있으므로 생성해준다.
#                 if not UserInfo.objects.filter(username=username).exists() :
#                     if user.is_superuser :
#                         usertype = UserInfo.SUPER 
#                     else  :
#                         usertype = UserInfo.NORMAL
#                       
#                     userInfo = UserInfo(username=username, usertype=usertype)
#                     userInfo.save()
#                     
#                 if request.POST.get("auto_login") : 
#                     request.session.set_expiry(86400 * 365 * 10)
#                 return redirect(reverse(redirectURL))
#             else :
#                 context['message'] = '아이디 또는 암호가 잘못 되었습니다.'
#         else :
#             context['message'] = '아이디와 암호를 입력하여 주십시오.'
#           
#         if username :
#             context['username'] = username
#           
#     else :
#         log.info(kwargs)
#         redirectURL = kwargs.get("redirect") 
#             
#     if redirectURL :
#         context['redirectURL'] = redirectURL
#             
#     return HttpResponse(render(request, "user_login.html", {'user_login' : context}))
#       
# def uesr_logout(request, *args, **kwargs):
#     logout(request)
#     return redirect("/")
#       
# def user_group(request, *args, **kwargs): 
#     context = { 'group' : [], 'user' : []}
#     users = []
#     if request.POST.get('user.group.update') :
#         username = request.POST.get('username')
#         groupname = request.POST.get('groupname')
#         assign = request.POST.get('assign') == 'True' or request.POST.get('assign') == 'true'
#           
#         if assign :
#             user = UserInfo.objects.get(username=username)
#             group = UserInfo.objects.get(username=groupname)
#             userGroup = UserGroups(user=user, group=group)
#             userGroup.save()
#         else :
#             userGroup = UserGroups.objects.get(user=username, group=groupname)
#             userGroup.delete()
#           
#         if request.is_ajax() :
#             return HttpResponse({"username" : username, "groupname" : groupname, "assign" : assign })
#         else :
#             users = UserInfo.objects.filter(username=username)
#     else :
#         search_term = request.POST.get("user.group.search.term")
#         if search_term and request.POST.get('user.group.search') :
#             users = UserInfo.objects.filter(username__contains=search_term, usertype__in=[UserInfo.NORMAL])
#         else :
#             users = UserInfo.objects.filter(usertype__in=[UserInfo.NORMAL])
#           
#     index = 0
#     groupIndex = {}
#     groups = list(UserInfo.objects.filter(usertype=UserInfo.GROUP))
#     for group in groups :
#         groupIndex[group.username] = index
#         index = index + 1
#         context['group'].append([index, group.username])
#           
#     for userinfo in users :
#         auth_user = User.objects.get(username=userinfo.username)
#         user = {'username' : userinfo.username, 'first_name' : auth_user.first_name, 'last_name' : auth_user.last_name, 'assign' : [] }
#         for group in groups :
#             user['assign'].append([group.username, False])
#           
#         userGroups = UserGroups.objects.filter(user=userinfo.username)
#         for userGroup in userGroups :
#             user['assign'][groupIndex[userGroup.group.username]][1] = True
#           
#         context['user'].append(user)
#     return render(request, "user_group.html", {'user_group' : context})        
# 
# def user_delete(request, *args, **kwargs):
#     response = {
#         "code"      : "",
#         "message"   : ""
#     }
#     
#     userid      = request.POST.get("userid")
#     user        = User.objects.get(username = userid)
#     sessionInfo = UserInfo.getUserInfo(request)
#     if not ( sessionInfo.isSuper() or request.user.username == userid ) :
#         response["code"] = -4
#         response["message"] = "권한이 없습니다."
#         return HttpResponse(json.dumps(response))
#     
#     if user.is_superuser :
#         response["code"] = -3
#         response["message"] = "시스템 관리자 계정은 삭제할 수 없습니다."
#         return HttpResponse(json.dumps(response))
#         
#     try :
#         with transaction.atomic() :
#             User.objects.get(username__exact = userid ).delete()
#             UserInfo.objects.get(username__exact = userid ).delete()
#     except IntegrityError :
#         response["code"] = -1
#         response["message"] = "사용자 계정을 삭제하는 도중에 오류가 발생했습니다."
#         return HttpResponse(json.dumps(response))
#                 
#     response["code"] = 0
#     response["message"] = "사용자 계정이 삭제 되었습니다."
#     return HttpResponse(json.dumps(response))
#     
def isChecked(request, param): 
    return (True, False)[request.POST.get(param) == None]

def restart(userinfo) :
    if not userinfo.isSuper() :
        error("Only super user can reatart CELLAR.")
        return False
     
    info("CELLAR is being restarted by " + userinfo.username)
    call(["uwsgi", "--reload", "uwsgi.pid"])
