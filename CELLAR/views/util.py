from _sqlite3                   import IntegrityError
import json
from os.path                    import os
import re
from subprocess                 import call
from wsgiref.util               import FileWrapper

from django.contrib.auth        import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.views  import login, logout
from django.core.exceptions     import PermissionDenied
from django.core.urlresolvers   import reverse
from django.db                  import transaction
from django.http.response       import HttpResponse, HttpResponseServerError, StreamingHttpResponse, HttpResponseNotAllowed
from django.shortcuts           import redirect, render

from CELLAR                     import util, index, config
from CELLAR.authority           import Directory
from CELLAR.models              import UserInfo, FileDescriptor, UserAuthority
from CELLAR.util                import CELLAR_FileManager
from SonienStudio.log           import error, info, ok
from SonienStudio.tarstream     import TarStream


def browseFilelist(request, *args, **kwrags):
    targetDir   = request.POST.get('target')
    result      = util.getFileGroup(request, targetDir)
     
    userinfo    = UserInfo.getUserInfo(request)
    auth        = Directory.getAuth(userinfo, userinfo.getHomePath() + targetDir)
      
    context = {
        'target'    : targetDir,
        'directory' : result[0],
        'file'      : result[1],
        'readable'  : auth[0],
        'writeable' : auth[1],
        'deletable' : auth[2]
    }
     
    # info("browse.filelist : " + targetDir)
    return HttpResponse(json.dumps(context))    

def browseDirectory(request, *args, **kwrags):
    targetDir   = request.POST.get('target')
    result      = util.getDirTree(request, targetDir, 2)
     
    context = {
        'target'    : targetDir,
        'node'      : result 
    }
    
    # info("browse.directory : " + targetDir) 
    return HttpResponse(json.dumps(context))

def browse(request, *args, **kwrags):
    targetDir   = request.POST.get('target')
    filelist    = util.getFileGroup(request, targetDir)
    directree   = util.getDirTree(request, targetDir, 2)
 
    userinfo    = UserInfo.getUserInfo(request)
    auth        = Directory.getAuth(userinfo, userinfo.getHomePath() + targetDir)
         
    context = {
        'target'    : targetDir,
        'filelist'  : {
            'directory' : filelist[0],
            'file'      : filelist[1],
            'readable'  : auth[0],
            'writeable' : auth[1],
            'deletable' : auth[2] 
        },
        'directree' : {
            'node'      : directree
        }
    }
     
    # info("browse.all : " + targetDir)    
    return HttpResponse(json.dumps(context))
 
def upload(request, *args, **kwargs):
    response = { 
        "status"    : "success", 
        "message"   : "" 
    }
    
    fileManager = CELLAR_FileManager(request)
    filename    = request.POST.get("name")
    cwd         = request.POST.get("cwd")
    if cwd is None or not fileManager.isWriteable(cwd) :
        response["status"] = "error"
        response["message"] = "해당 경로에 쓰기 권한이 없습니다."
        return HttpResponseServerError(json.dumps(response))
     
    file = request.FILES["file"]
    if not file :
        response["status"] = "error"
        response["message"] = "파일이 정상적으로 업로드 되지 않았습니다."
        return HttpResponseServerError(json.dumps(response))
     
    dstPath = fileManager._root_norm + cwd + filename
    chunk   = int(request.POST.get("chunk"))
    chunks  = int(request.POST.get("chunks"))
     
    if chunk == 0 :
        info("Upload : " + dstPath + " start")
        mode = "wb"
    else :
        mode = "ab"
    
    info("Upload : " + dstPath + " ({0} / {1})".format(chunk + 1, chunks)) 
    with open(dstPath, mode) as destination:
        destination.write(file.file.read())
    file.file.close()
    
    if chunk + 1 == chunks :
        info("Upload : " + dstPath + " finished")
        
    return HttpResponse(json.dumps(response)) 

def download(request, *args, **kwargs):
    """
    Download a file
    @param kwargs:    
        filepath    : Relative file path of target file. Root is user home.
    """
    
    target = kwargs['filepath']
    
    # Authority Check
    fileManager = CELLAR_FileManager(request)
    if target is None or not fileManager.isReadable(os.path.dirname(target)) :
        raise PermissionDenied
    
    fullPath = UserInfo.getUserInfo(request).getHomePath() + "/" + target
    response = StreamingHttpResponse(FileWrapper(open(fullPath, mode='rb')), content_type='application/octet-stream')
    response['Content-Length'] = os.path.getsize(fullPath)    
    response['Content-Disposition'] = 'attachment'
     
    return response

def tarload(request, *args, **kwargs):
    """
    Download group of files in TAR format
    @param path    : Relative path of target files  
    @param files[] : List of files
    """        
    path        = request.POST.get('path')
    files       = request.POST.getlist('files[]')
    
    # 권한 확인
    fileManager = CELLAR_FileManager(request)
    if path is None or not fileManager.isReadable(path) :
        raise PermissionDenied
     
    dirs = path.split("/");
    while "" in dirs :
        dirs.remove("")
    dirs.reverse()
 
    tarStream = TarStream.open(fileManager.getFullPath(path), 128)
    for file in files :
        tarStream.add(file)
     
    response = StreamingHttpResponse(tarStream, content_type='application/x-tar')
    response['Content-Length'] = tarStream.getTarSize() 
    response['Content-Disposition'] = 'attachment'
        
    return response

# * Response for file transaction
# {
#     ### Common    ###
#     "code"    : 0 is OK, others are for each error
#     "message" : Message. Must not be null. Can be empty 
# 
#     ### Additonal ###
#     Each functions provide additional information
# }
# """
 
def createDir(request, *args, **kwargs):
    """
    * Common 
    0 : "SUCCESS",
    1 : "생성 위치가 존재하지 않습니다",
    2 : "생성 위치가 파일입니다",
    3 : "허용되지 않는 요청입니다",
    4 : "오류가 발생하였습니다",
    5 : "권한이 없습니다",
     
    * Additional 
    newPath : 생성된 새 경로 
    """
    
    parentPath  = request.POST.get("parentPath")
    dirName     = request.POST.get("dirName")
    newPath     = parentPath + dirName + "/"
    
    fileManager = CELLAR_FileManager(request) 
    code = fileManager.mkdir(parentPath, dirName)
          
    message = {
        0 : "SUCCESS",
        1 : "생성 위치가 존재하지 않습니다",
        2 : "생성 위치가 파일입니다",
        3 : "허용되지 않는 요청입니다",
        4 : "오류가 발생하였습니다",
        5 : "권한이 없습니다",
    }
    response = {
        "code"      : code,
        "message"   : message[code],
        "newPath"   : newPath,
    }
    
    if code == 0 :
        ok("dir.create : {0}".format(fileManager.getFullPath(newPath)))
    else :
        error("dir.create : E{0} {1}".format(code, fileManager.getFullPath(newPath)))
    return HttpResponse(json.dumps(response)) 
            
def deleteDir(request, *args, **kwargs):
    """
    0 : 성공
    1 : 대상이 파일입니다
    2 : -
    3 : 허용되지 않은 요청입니다
    4 : 오류가 발생하였습니다
    5 : 권한 없음
    """
     
    dirPath = request.POST.get("dirPath")
    
     
    fileManager = CELLAR_FileManager(request) 
    code = fileManager.rmdir(dirPath)
     
    message = {
        0 : "성공",
        1 : "대상이 파일입니다",
        2 : "",
        3 : "허용되지 않은 요청입니다",
        4 : "오류가 발생하였습니다",
        5 : "권한 없음"
    }
    response = {
        "code"      : code,
        "message"   : message[code],
        "dirPath"   : dirPath  
    }
    
    if code == 0 :
        ok("dir.delete : {0}".format(fileManager.getFullPath(dirPath)))
    else :
        error("dir.delete : E{0} {1}".format(code, fileManager.getFullPath(dirPath)))
        
    return HttpResponse(json.dumps(response))    

def deleteFiles(request, *args, **kwargs): 
    """
    return {
        ...
        exts : [(ext, errno), ...]
    }
     
    0 : 성공
    1 : 대상이 경로입니다
    2 : -
    3 : 허용되지 않은 요청입니다
    4 : 오류가 발생하였습니다
    5 : 권한 없음
    """     
    groupPath   = request.POST.get("groupPath")
    exts        = request.POST.getlist("exts[]")
     
      
    targetPath  = os.path.normpath(os.path.dirname(groupPath)) + "/"
    filegroup   = os.path.basename(groupPath)
    filenames   = []
    for ext in exts :
        filenames.append(filegroup + ext)
     
    fileManager = CELLAR_FileManager(request)
    resultSet   = fileManager.rmfiles(targetPath, filenames)
    result      = []
    code        = 0
    
    info("file.delete : {0}".format(fileManager.getFullPath(groupPath))) 
    for row in resultSet :
        ext = os.path.splitext(row[0])[1]
        result.append((ext, row[1]))
        if row[1] == 0 :
            ok("file.delete : {0}".format(ext))
        else :
            error("dir.delete : E{0} {1}".format(code, ext))
        
        if row[1] is not 0 :
            code = row[1]
     
    message = {
        0 : "성공",
        1 : "대상이 경로입니다",
        2 : "",
        3 : "허용되지 않은 요청입니다",
        4 : "오류가 발생하였습니다",
        5 : "권한 없음"
    }
    response = {
        "code"      : code,
        "message"   : message[code],
        "groupPath" : groupPath,
        "result"    : result  
    }
    return HttpResponse(json.dumps(response))

def rename(request, *args, **kwargs):
    """
    * Common 
    0 : "SUCCESS",
    1 : "파일/경로를 찾을 수 없습니다",
    2 : "변경하려는 대상이 존재합니다",
    3 : "허용되지 않는 요청입니다",
    4 : "오류가 발생하였습니다",
    5 : "권한이 없습니다",
     
    * Additional 
    dst     : New name. Not valid in error.
    dstPath : New path. Not valid in error. 
    """
    
    srcPath = request.POST.get('srcPath');
    dst     = request.POST.get('dst');
    dstPath = os.path.normpath(srcPath + os.path.sep + os.pardir + os.path.sep + dst)
    fileManager = CELLAR_FileManager(request) 
    code = fileManager.rename(srcPath, dstPath)
    if code == 0 and os.path.isdir(fileManager.getFullPath(dstPath)) :
        dstPath += "/"
         
    message = {
        0 : "SUCCESS",
        1 : "파일/경로를 찾을 수 없습니다",
        2 : "변경하려는 대상이 존재합니다",
        3 : "허용되지 않는 요청입니다",
        4 : "오류가 발생하였습니다",
        5 : "권한이 없습니다",
    }
    response = {
        "code"      : code,
        "message"   : message[code],
        "dst"       : dst,
        "dstPath"   : dstPath
    }
    return HttpResponse(json.dumps(response))
# 
def renameGroup(request, *args, **kwargs):
    """
    * Common 
    0 : "SUCCESS",
    1 : "파일을 찾을 수 없습니다",
    2 : "변경하려는 대상이 존재합니다",
    3 : "허용되지 않는 요청입니다",
    4 : "오류가 발생하였습니다",
    5 : "권한이 없습니다",
     
    * Additional 
    dstGroup    : New group path. Not valid in error. 
    result      : [ (ext, errno, dstPath), (ext, errno dstPath), ... ] 
    """
       
    srcGroup = request.POST.get('srcGroup');
    srcExts = request.POST.getlist('srcExts[]');
    dst = request.POST.get('dst');
    dstGroup = os.path.normpath(srcGroup + os.path.sep + os.pardir + os.path.sep + dst) 
     
    fileManager = CELLAR_FileManager(request) 
    result = []
    code = 0
     
    for ext in srcExts :
        newPath = ""
        srcPath = srcGroup + ext
        dstPath = dstGroup + ext
        errno = fileManager.rename(srcPath, dstPath)
        if errno :  code = errno
        else : newPath = dstPath
         
        result.append([ext, errno, newPath])
         
    message = {
        0 : "SUCCESS",
        1 : "파일/경로를 찾을 수 없습니다",
        2 : "변경하려는 대상이 존재합니다",
        3 : "허용되지 않는 요청입니다",
        4 : "오류가 발생하였습니다",
        5 : "권한이 없습니다",
    }
    response = {
        "code"      : code,
        "message"   : message[code],
        "dstGroup"  : dstGroup,
        "result"    : result  
    }
    return HttpResponse(json.dumps(response))

def move(request, *args, **kwargs):
    """
    * Common 
    0 : "SUCCESS",
    1 : "파일/경로를 찾을 수 없습니다",
    2 : "이동하려는 위치가 파일입니다",
    3 : "허용되지 않는 요청입니다",
    4 : "오류가 발생하였습니다",
    5 : "권한이 없습니다",
     
    * Additional 
    dstPath : Destination path
    result  : [ (target, errno, newPath), (target, errnom newPath), ... ] 
    """
    
    targets = request.POST.getlist("targets[]")
    dstPath = request.POST.get("dstPath")
    fileManager = CELLAR_FileManager(request)
     
    result = []
    code = 0
    for target in targets :
        newPath = ""
        errno = fileManager.move(target, dstPath)
        if errno :  code = errno
        else : newPath = dstPath + os.path.basename(os.path.normpath(target))
         
        result.append([target, errno, newPath + "/"])
     
    message = {
        0 : "SUCCESS",
        1 : "파일/경로를 찾을 수 없습니다",
        2 : "변경하려는 위치가 파일입니다",
        3 : "허용되지 않는 요청입니다",
        4 : "오류가 발생하였습니다",
        5 : "권한이 없습니다",
    }
    response = {
        "code"      : code,
        "message"   : message[code],
        "dstPath"   : dstPath,
        "result"    : result  
    }
    return HttpResponse(json.dumps(response)) 
 
def resetAllAuthority(request, *args, **kwargs) :
    response = {
        "code"      : 0,
        "message"   : ""
    }
    
    if not UserInfo.getUserInfo(request).isAdmin() :
        response['code']    = -1
        response['message'] = "권한 초기화는 최고 관리자만 가능합니다"
    else :
        # DB 초기화    
        FileDescriptor.objects.all().delete()
        UserAuthority.objects.all().delete()
        FileDescriptor(file_id=0, file="", reference=None).save()  # 이건 더미
     
        index.dir_reset()
         
    return HttpResponse(json.dumps(response))

def getDefaultAuthority(request, *args, **kwargs):
    path = request.POST.get("path")
    response = {
        "path"      : path,
        "register"  : False,
        "readable"  : config.DEFAULT_AUTH_DIR_READABLE,
        "writeable" : config.DEFAULT_AUTH_DIR_WRITEABLE,
        "deletable" : config.DEFAULT_AUTH_DIR_DELETABLE,
        "inherit"   : config.DEFAULT_AUTH_DIR_INHERIT
    }
     
    userinfo = UserInfo.getUserInfo(request)
    fullpath = userinfo.getHomePath() + path
    file_id = index.dir_get(fullpath)
    if file_id is not None :
        fileDescriptor = FileDescriptor.objects.get(file_id=file_id)
        response['register']    = True
        response['readable']    = fileDescriptor.readable
        response['writeable']   = fileDescriptor.writeable
        response['deletable']   = fileDescriptor.deletable
        response['inherit']     = fileDescriptor.inherit
        
    return HttpResponse(json.dumps(response))
 
def setDefaultAuthority(request, *args, **kwargs):
    path = request.POST.get("path")
    response = {
        "code"      : 0,
        "message"   : "",
        "path"      : path,
        "register"  : False,
        "readable"  : config.DEFAULT_AUTH_DIR_READABLE,
        "writeable" : config.DEFAULT_AUTH_DIR_WRITEABLE,
        "deletable" : config.DEFAULT_AUTH_DIR_DELETABLE,
        "inherit"   : config.DEFAULT_AUTH_DIR_INHERIT
    }
     
    userinfo = UserInfo.getUserInfo(request)
    fullpath = userinfo.getHomePath() + request.POST.get("path")

    if not userinfo.isAdmin() :
        response['code']    = -1
        response['message'] = "권한 초기화는 최고 관리자만 가능합니다"
    else :     
        inherit = request.POST.get("inherit")
        if inherit is not None :
            inherit = inherit == "1"
     
        readable = request.POST.get("readable")
        if readable is not None :
            readable = readable == "1"
          
        writeable = request.POST.get("writeable")
        if writeable is not None :
            writeable = writeable == "1"
          
        deletable = request.POST.get("deletable")
        if deletable is not None :
            deletable = deletable == "1"
     
        result = Directory.setAuth(fullpath, inherit, readable, writeable, deletable)
        if result[0] >= 0 :
            response["code"]        = 0
            response["message"]     = result[1]
            response['register']    = True
            response['inherit']     = inherit
            response['readable']    = readable
            response['writeable']   = writeable
            response['deletable']   = deletable
     
    return HttpResponse(json.dumps(response))

def delDefaultAuthority(request, *args, **kwargs):
    path = request.POST.get("path")
    response = {
        "code"      : 0,
        "message"   : "",
        "path"      : path,
        "register"  : False,
        "readable"  : config.DEFAULT_AUTH_DIR_READABLE,
        "writeable" : config.DEFAULT_AUTH_DIR_WRITEABLE,
        "deletable" : config.DEFAULT_AUTH_DIR_DELETABLE,
        "inherit"   : config.DEFAULT_AUTH_DIR_INHERIT
    }
     
    userinfo = UserInfo.getUserInfo(request)
    fullpath = userinfo.getHomePath() + request.POST.get("path")
     
    if not userinfo.isAdmin() :
        response['code'] = 1
        response['message'] = "최고 관리자만 가능합니다"
    elif not Directory.delAuth(fullpath) : 
        response["code"] = -1
        response["message"] = "디렉토리 식별자 삭제 실패"
         
    return HttpResponse(json.dumps(response))

def getUserAuthority(request, *args, **kwargs):
    path = request.POST.get("path")
    fileManager = CELLAR_FileManager(request)
    response = {
        "code"      : 0,
        "message"   : "",
        "path"      : path,
        "register"  : False,
        "readable"  : fileManager.isReadable(path),
        "writeable" : fileManager.isWriteable(path),
        "deletable" : fileManager.isDeletable(path)
    }
     
    return HttpResponse(json.dumps(response))

def getAuthorizedUsers(request, *args, **kwargs):
    response = {
        "code"      : 0,
        "message"   : "",
        "users"     : []
    }
     
    userinfo = UserInfo.getUserInfo(request)
    fullpath = userinfo.getHomePath() + request.POST.get("path")
    authType = int(request.POST.get("type"))
     
    if userinfo.isAdmin() :
        file_id = index.dir_get(fullpath)
        if file_id is not None :
            for user in UserAuthority.objects.filter(file_id=file_id)  :
                if      authType & 4 and not user.readable     : continue
                elif    authType & 2 and not user.writeable    : continue
                elif    authType & 1 and not user.deletable    : continue
                 
                response['users'].append([user.username.username,
                                          user.username.getName(),
                                          user.username.usertype])
    else :
        response['code'] = 1
        response['message'] = "최고 관리자만 가능합니다"
         
    return HttpResponse(json.dumps(response))

def setAuthorizedUsers(request, *args, **kwargs):
    response = {
        "code"      : 0,
        "message"   : "",
        "users"     : []
    }
     
    userinfo = UserInfo.getUserInfo(request)
    fullpath = userinfo.getHomePath() + request.POST.get("path")
    
    ids         = request.POST.getlist("ids[]")
    readable    = request.POST.get('readable')
    readable    = (readable == "1", None)[readable == None]
    writeable   = request.POST.get('writeable')
    writeable   = (writeable == "1", None)[writeable == None]
    deletable   = request.POST.get('deletable')
    deletable   = (deletable == "1", None)[deletable == None]
    if userinfo.isAdmin() :         
        file_id = index.dir_get(fullpath) 
        if file_id is None :
            file_id = Directory.setAuth(fullpath, config.DEFAULT_AUTH_DIR_INHERIT, config.DEFAULT_AUTH_DIR_READABLE, config.DEFAULT_AUTH_DIR_WRITEABLE, config.DEFAULT_AUTH_DIR_DELETABLE)[0]
            
        fileDescriptor = FileDescriptor.objects.get(file_id=file_id)
        try :
            with transaction.atomic() :
                for authUser in UserInfo.objects.filter(username__in=ids) :
                    userAuthority = None
                    try :
                        userAuthority = UserAuthority.objects.get(username=authUser, file_id=fileDescriptor)
                        if (readable  is not None and userAuthority.readable == readable) or \
                           (writeable is not None and userAuthority.writeable == writeable) or \
                           (deletable is not None and userAuthority.deletable == deletable) :
                            continue
                          
                    except Exception as err :
                        userAuthority = UserAuthority(username=authUser, file_id=fileDescriptor)
                          
                    if readable is not None :
                        userAuthority.readable = readable
                    if writeable is not None :
                        userAuthority.writeable = writeable
                    if deletable is not None :
                        userAuthority.deletable = deletable
                    userAuthority.save()
                    response['users'].append([
                                authUser.username,
                                authUser.getName(),
                                authUser.usertype,
                                userAuthority.readable,
                                userAuthority.writeable,
                                userAuthority.deletable])
                      
        except Exception as err :
            response['code'] = -2
            response['message'] = err.__str__()
            response['users'].clear()
                 
    else :
        response['code'] = 1
        response['message'] = "최고 관리자만 가능합니다"
         
    return HttpResponse(json.dumps(response))

def userCreate(params, isAdmin = False) :
    response = {
        "code"  : 0,
    }
              
    is_group    = params.get('is_group')
    username    = params.get('username')
    password    = params.get("password")
    email       = params.get("email")
    first_name  = params.get("first_name")
    memo        = params.get("memo")
          
    # 최고 관리자에 의해 등록되는 ID 는 E-MAIL 은 필요 없음
    if not email and isAdmin :
        email = "" 
            
    if is_group and not isAdmin :
        response["code"]    = -2
        response["message"] = "그룹 사용자는 관리자만이 추가할 수 있습니다."
    elif not re.match("[a-zA-Z0-9]{6,}|@[a-zA-Z0-9]{5,}", username) :
        response["code"]    = -3
        response["message"] = "ID 는 6글자 이상의 영숫자로 작성해주세요."
    elif is_group and not re.match("@.*", username) :
        response["code"]    = -4
        response["message"] = "그룹 사용자의 아이디는 @로 시작해야합니다."
    elif username and password and first_name and ( email or isAdmin ) :
        try :
            usertype = UserInfo.NORMAL
            if is_group :
                usertype = UserInfo.GROUP
                     
            user        = User.objects.create_user(username, email, password, first_name=first_name)
            userinfo    = UserInfo(username=username, usertype=usertype, memo=memo)
            userinfo.save()
              
            response["code"]    = 0
            response["message"] = "사용자가 등록되었습니다."
            response["user"]    = user
            
            ok("user.create : " + username)
        except Exception as err :
            error("user.create : " + err.__str__())
            response["code"]    = 1
            response['message'] = "이미 존재하는 아이디 입니다."
    else :
        response["code"]    = -1
        response["message"] = "필수 항목을 모두 입력하여 주십시오."
        
    if isAdmin and is_group :
        response["is_group"] = is_group
        
    if username :
        response["username"] = username
            
    if email :
        response["email"] = email
        
    if first_name :
        response["first_name"] = first_name
        
    if memo :
        response["memo"] = memo
        
    return response  

def userGet(request, *args, **kwargs):
    username    = request.POST.get("username")
    sessionInfo = UserInfo.getUserInfo(request)
     
    response = {
        "code"      : "",
        "message"   : ""
    }
     
    if sessionInfo.isAdmin() or request.user.username == username :
        result = UserInfo.objects.filter(username__exact = username)
        if not result.exists() :
            response["code"] = -1
            response["message"] = "존재하지 않는 아이디 입니다."
        else :
            userinfo    = result[0]
            user        = User.objects.get(username = userinfo.username )
             
            response["username"]    = userinfo.username
            response["name"]        = user.first_name
            response["email"]       = user.email
            response["usertype"]    = userinfo.usertype
            response["home"]        = userinfo.home 
            response["memo"]        = userinfo.memo
             
            response["code"]        = 0
    else :
        response["code"]    = -4
        response["message"] = "권한이 없습니다."
     
    return HttpResponse(json.dumps(response))

def userUpdate(request, *args, **kwargs):
    response = {
        "code"      : "",
        "message"   : "" 
    }
     
    username        = request.POST.get("username")
    usertype        = request.POST.get("usertype")
    home            = None
    name            = request.POST.get("name")
    email           = request.POST.get("email")
    memo            = request.POST.get("memo")
    password_new    = request.POST.get("password_new")
    password_old    = request.POST.get("password_old")
    if request.POST.__contains__("home") :
        home = request.POST.get("home")
     
    if usertype : usertype = int(usertype) 
     
    # 권한 확인 - 공통
    user        = User.objects.get(username = username)
    userinfo    = UserInfo.objects.get(username = username)
    sessionInfo = UserInfo.getUserInfo(request)
    if not sessionInfo.isAdmin() and sessionInfo.username != username :
        response["code"]    = -4
        response["message"] = "권한이 없습니다."
        return HttpResponse(json.dumps(response))
     
    # 권한 확인 - 관리자
    if not sessionInfo.isAdmin() and ( home is not None or usertype ) :
        response["code"]    = -5
        response["message"] = "관리자만이 변경 가능한 항목을 포함하고 있습니다."
        return HttpResponse(json.dumps(response))
     
    # 시스템 관리자는 계정 유형 변경 불가
    if user.is_superuser and usertype and usertype != UserInfo.SUPER :
        response["code"]    = -6
        response["message"] = "시스템 관리자의 계정 유형을 변경할 수 없습니다."
        return HttpResponse(json.dumps(response))
     
    # 암호 변경 요청 시 사용자 암호 확인
    if password_new :
        if sessionInfo.isAdmin() and not password_old :
            pass
        elif authenticate(username = username, password = password_old) :
            pass
        else :
            response["code"]    = -3
            response["message"] = "입력한 기존 암호가 잘못되었습니다."
            return HttpResponse(json.dumps(response))
     
    try :
        with transaction.atomic() :
            # 사용자 정보 갱신
            if email :
                user.email = email
            if name :
                user.first_name = name
            if password_new :
                user.set_password(password_new)
            user.save()
             
            if home is not None :
                userinfo.home = home
            if usertype :
                userinfo.usertype = usertype
            if memo :
                userinfo.memo = memo
            userinfo.save()
             
            response['code']    = 0
            response['message'] = "사용자 정보가 변경되었습니다."
             
            response['username']    = username
            response['name']        = user.first_name
            response['email']       = user.email
            response['home']        = userinfo.home
            response['memo']        = userinfo.memo
            response['usertype']    = userinfo.usertype
              
    except Exception as err :
        response['code'] = -2
        response['message'] = err.__str__()
     
    return HttpResponse(json.dumps(response))

       
def userLogin(request, *args, **kwargs):
    redirectURL = None
    context = {}
     
    if request.POST.get("user.login") :
        username = request.POST.get('username')
        password = request.POST.get("password")
        
        redirectURL = request.POST.get("redirectURL", "cellar")
        
        if username and password :
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active :
                login(request, user) 
                   
                # django 에서 직접 만든 ID 의 경우 UserInfo 가 누락되어있으므로 생성해준다.
                if not UserInfo.objects.filter(username=username).exists() :
                    if user.is_superuser :
                        usertype = UserInfo.SUPER 
                    else  :
                        usertype = UserInfo.NORMAL
                       
                    userinfo = UserInfo(username=username, usertype=usertype)
                    userinfo.save()
                     
                if request.POST.get("auto_login") : 
                    request.session.set_expiry(86400 * 365 * 10)
                return redirect(reverse(redirectURL))
            else :
                context['message'] = '아이디 또는 암호가 잘못 되었습니다.'
        else :
            context['message'] = '아이디와 암호를 입력하여 주십시오.'
           
        if username :
            context['username'] = username
           
    else :
        info(kwargs)
        redirectURL = kwargs.get("redirect") 
             
    if redirectURL :
        context['redirectURL'] = redirectURL
             
    return HttpResponse(render(request, "user_login.html", {'userLogin' : context}))
       
def uesrLogout(request, *args, **kwargs):
    logout(request)
    return redirect("/")

def userDelete(request, *args, **kwargs):
    response = {
        "code"      : "",
        "message"   : ""
    }
     
    username    = request.POST.get("username")
    user        = User.objects.get(username = username)
    sessionInfo = UserInfo.getUserInfo(request)
    if not ( sessionInfo.isAdmin() or request.user.username == username ) :
        response["code"] = -4
        response["message"] = "권한이 없습니다."
        return HttpResponse(json.dumps(response))
     
    if user.is_superuser :
        response["code"] = -3
        response["message"] = "시스템 관리자 계정은 삭제할 수 없습니다."
        return HttpResponse(json.dumps(response))
         
    try :
        with transaction.atomic() :
            User.objects.get(username__exact = username ).delete()
            UserInfo.objects.get(username__exact = username ).delete()
    except IntegrityError :
        response["code"] = -1
        response["message"] = "사용자 계정을 삭제하는 도중에 오류가 발생했습니다."
        return HttpResponse(json.dumps(response))
                 
    response["code"] = 0
    response["message"] = "사용자 계정이 삭제 되었습니다."
    return HttpResponse(json.dumps(response))
     
def isChecked(request, param): 
    return (True, False)[request.POST.get(param) == None]

def restart(userinfo) :
    if not userinfo.isAdmin() :
        error("Only super user can reatart CELLAR.")
        return False
     
    info("CELLAR is being restarted by " + userinfo.username)
    call(["uwsgi", "--reload", "uwsgi.pid"])
