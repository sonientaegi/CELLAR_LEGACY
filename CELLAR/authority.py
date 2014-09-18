from os.path            import os

from django.db          import transaction

from SonienStudio import log
from SonienStudio.file import FileManager
from THS                import config
from THS.models         import UserInfo, FileDescriptor, UserGroups, UserAuthority
from THS.util_index     import *


"""
권한 개념 정의

경로
R : 하위 항목 조회 권한 & 상위에서 조회 가능 여부 
W : 해당 경로에 파일을 생성하거나 이동한 파일을 붙여넣을 수 있는 권한
D : 해당 경로에서 하위 파일이나 경로를 삭제할 수 있는 권한

파일
R : 해당 파일을 읽을 수 있는 권한.
"""

class Directory :
    @staticmethod
    def set(fullPath, inherit = None, readable = None, writeable = None, deletable = None) :
        """
        Directory 권한 설정
        성공 시
            경로 식별자 ID
            ""
        실패 시
            -1 
            예외 메시지
        """
    
        index   = dir_get(fullPath)
        message = ""
        
        if index is None :
            params = {}
            if inherit is not None :
                params["inherit"] = inherit
            
            if readable is not None :
                params["readable"] = readable
            
            if writeable is not None :
                params["writeable"] = writeable
                
            if deletable is not None :
                params["deletable"] = deletable
            
            try :
                with transaction.atomic() :
                    descriptor = FileDescriptor(file = fullPath, reference_id = 0, **params)
                    descriptor.save()
                    dir_set(fullPath, descriptor.id)
                    index = descriptor.id
            except Exception as err :
                log.error("Directory.set " + err.__str__())
                index   = -1
                message = err.__str__()        
    
        else :
            try : 
                descriptor = FileDescriptor.objects.get(id = index)
                index = descriptor.id
                if inherit  is not None :
                    descriptor.inherit = inherit
                if readable is not None :
                    descriptor.readable = readable
                if writeable is not None :
                    descriptor.writeable = writeable
                if deletable is not None :
                    descriptor.deletable = deletable
                descriptor.save()
                 
            except Exception as err :
                index   = -2
                message = err.__str__()
        
        return (index, message)    
    
    @staticmethod
    def delete(fullPath) :
        """
        Directory 권한 삭제
        """
        index = dir_get(fullPath)
        if index is None :
            return True
        elif dir_del(fullPath):
            FileDescriptor.objects.filter(id = index).delete()
            FileDescriptor.objects.filter(reference_id = index).delete()
            return True
        else :
            return False
    
    @staticmethod
    def getAuthority(userinfo, fullPath):
        """
        조회 대상에 대하여 소유한 권한을 RWD 튜플로 반환한다.
        """
        if userinfo.isSuper() :    
            return (True, True, True)
        
        readable    = False
        writeable   = False
        deletable   = False
        
        normFullPath = os.path.normpath(fullPath)
                
        fileDescriptor  = None
        index = dir_get(fullPath)
             
        # 재귀적으로 권한 추출 시 사용자 홈 이상으로는 올라갈 수 없음.
        log.info("ROOT : " + userinfo.getUserHome())
        log.info("COMP : " + normFullPath)
        if normFullPath == userinfo.getUserHome() :
            inheritable = False
        else :
            inheritable = True
         
        if index is not None and index >= 0 :
            try :
                fileDescriptor  = FileDescriptor.objects.get(id = index)
                 
                readable    |= fileDescriptor.readable
                writeable   |= fileDescriptor.writeable
                deletable   |= fileDescriptor.deletable
                 
                if not ( readable and writeable and deletable ) :
                    users = []
                    users.append(userinfo)
                    for user in UserGroups.objects.filter(user = userinfo) :
                        users.append(user.group)
             
                    for userAuthority in UserAuthority.objects.filter(username__in = users, file_id = index) :    
                        readable    |= userAuthority.readable
                        writeable   |= userAuthority.writeable
                        deletable   |= userAuthority.deletable
                         
                        if readable and writeable and deletable :
                            break
                 
                if not ( readable and writeable and deletable ) and inheritable and fileDescriptor.inherit :
                    auth_inherit =  Directory.getAuthority(userinfo, FileManager.getParent(fullPath))
                    readable    |= auth_inherit[0]
                    writeable   |= auth_inherit[1]
                    deletable   |= auth_inherit[2]
 
            except Exception as err:
                pass
        elif not userinfo.isGuest() or config.USING_GUEST :
            readable    = config.DEFAULT_AUTH_DIR_READABLE
            writeable   = config.DEFAULT_AUTH_DIR_WRITEABLE
            deletable   = config.DEFAULT_AUTH_DIR_DELETABLE
             
            # 상속받는 경우        
            if not( readable and writeable and deletable ) and inheritable and config.DEFAULT_AUTH_DIR_INHERIT :
                auth_inherit =  Directory.getAuthority(userinfo, FileManager.getParent(fullPath))
             
                readable    |= auth_inherit[0]
                writeable   |= auth_inherit[1]
                deletable   |= auth_inherit[2]
                
        # 만약 guest 활성화 되어있다면 GUEST HOME 에 대한 파일 조회 권한만 부여 한다.            
        if userinfo.isGuest() and normFullPath == config.getPathHomeGuest() :
            readable = True 
    
        return (readable, writeable, deletable)
    
    @staticmethod
    def isAuthorized(userinfo, fullPath, mode):
        """
        mode     : RWD 를 나타내는 3자리 숫자 배열 (111 ~ 000)
        조회 대상 권한 모두 보유 시 참 반환. 그 외에는 거짓
        """
        auth = Directory.getAuthority(userinfo, fullPath)
        isValid = True
        if isValid and mode & 0x04 and not auth[0] :
            isValid = False
        if isValid and mode & 0x02 and not auth[1] :
            isValid = False
        if isValid and mode & 0x01 and not auth[2] :
            isValid = False
        
        return isValid 
    
#         if userinfo.usertype == UserInfo.SUPER :    
#             return True
#         
#         fileDescriptor  = None
#         index = dir_get(fullPath)
#             
#         # 재귀적으로 권한 추출 시 사용자 홈 이상으로는 올라갈 수 없음.
#         log.info("ROOT : " + userinfo.dir_home)
#         log.info("COMP : " + os.path.normpath(fullPath))
#         if os.path.normpath(fullPath) == userinfo.dir_home :
#             inheritable = False
#         else :
#             inheritable = True
#         
#         if index is not None and index >= 0 :
#             readable    = False
#             writeable   = False
#             deletable   = False
#             
#             try :
#                 if fileDescriptor is None :
#                     fileDescriptor  = FileDescriptor.objects.get(id = index)
#                     
#                 if fileDescriptor.inherit :
#                     return Directory.isAuthorizedDir(userinfo, FileManager.getParent(fullPath), mode)
#                 else :
#                     readable    |= fileDescriptor.readable
#                     writeable   |= fileDescriptor.writeable
#                     deletable   |= fileDescriptor.deletable
#                     
#                     isValid = True
#                     if isValid and mode & 0x04 and not readable :
#                         isValid = False
#                     if isValid and mode & 0x02 and not writeable :
#                         isValid = False
#                     if isValid and mode & 0x01 and not deletable :
#                         isValid = False
#                     if isValid : return True
#             except Exception :
#                 pass
#             
#             users = []
#             users.append(userinfo)
#             for user in UserGroups.objects.filter(user = userinfo) :
#                 users.append(user.group)
#     
#             for userAuthority in UserAuthority.objects.filter(username__in = users, file_id = index) :    
#                 readable    |= userAuthority.readable
#                 writeable   |= userAuthority.writeable
#                 deletable   |= userAuthority.deletable
#                 
#                 isValid = True
#                 if isValid and mode & 0x04 and not readable :
#                     isValid = False
#                 if isValid and mode & 0x02 and not writeable :
#                     isValid = False
#                 if isValid and mode & 0x01 and not deletable :
#                     isValid = False
#                 if isValid : return True 
#             
#             return False
#         else :
#             # 상속받는 경우        
#             if inheritable and config.DEFAULT_AUTH_DIR_INHERIT :
#                 return Directory.isAuthorized(userinfo, FileManager.getParent(fullPath), mode)
#             else :
#                 readable    = config.DEFAULT_AUTH_DIR_READABLE
#                 writeable   = config.DEFAULT_AUTH_DIR_WRITEABLE
#                 deletable   = config.DEFAULT_AUTH_DIR_DELETABLE
#                 isValid = True
#                 if isValid and mode & 0x04 and not readable :
#                     isValid = False
#                 if isValid and mode & 0x02 and not writeable :
#                     isValid = False
#                 if isValid and mode & 0x01 and not deletable :
#                     isValid = False
#                 if isValid : return True
