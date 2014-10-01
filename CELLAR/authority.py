"""
경로 권한 개념 정의

R : 하위 항목 조회 권한 & 상위에서 조회 가능 여부 
W : 해당 경로에 파일을 생성하거나 이동한 파일을 붙여넣을 수 있는 권한
D : 해당 경로에서 하위 파일이나 경로를 삭제할 수 있는 권한
"""

from os.path                import os

from django.db              import transaction

from CELLAR                 import config, index
from CELLAR.models          import FileDescriptor, UserGroups, UserAuthority
from SonienStudio.file      import FileManager
from SonienStudio.log       import error

class Directory :
    @staticmethod
    def setAuth(fullPath, inherit=None, readable=None, writeable=None, deletable=None) :
        """
        Directory 권한 설정
        성공 시
            경로 식별자 ID
            ""
        실패 시
            -1 
            예외 메시지
        """
    
        file_id = index.dir_get(fullPath)
        message = ""
        
        if file_id is None :
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
                    descriptor = FileDescriptor(file=fullPath, reference_id=0, **params)
                    descriptor.save()
                    index.dir_set(fullPath, descriptor.file_id)
                    file_id = descriptor.file_id
            except Exception as err :
                error("auth.dir.set : " + err.__str__())
                file_id = -1
                message = err.__str__()        
    
        else :
            try : 
                descriptor = FileDescriptor.objects.get(file_id=file_id)
                file_id = descriptor.file_id
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
                error("auth.dir.set : " + err.__str__())
                file_id = -2
                message = err.__str__()
        
        return (file_id, message)    
    
    @staticmethod
    def delAuth(fullPath) :
        """
        Directory 권한 삭제
        """
        file_id = index.dir_get(fullPath)
        if file_id is None :
            return True
        elif index.dir_del(fullPath):
            FileDescriptor.objects.filter(file_id=file_id).delete()
            FileDescriptor.objects.filter(reference_id=file_id).delete()
            return True
        else :
            return False
    
    @staticmethod
    def getAuth(userinfo, fullPath, mode = 0x07):
        """
        조회 대상에 대하여 소유한 권한을 RWD 튜플로 반환한다.
        """
        if userinfo.isYeoman() or mode == 0x04 and userinfo.isMetic() : 
            return (True, True, True)
        
        readable    = not (mode & 0x04) | userinfo.isMetic()
        writeable   = not (mode & 0x02)
        deletable   = not (mode & 0x01)
        
        normFullPath = os.path.normpath(fullPath)
                
        descriptor  = None
        file_id     = index.dir_get(fullPath)
             
        # 재귀적으로 권한 추출 시 사용자 홈 이상으로는 올라갈 수 없음.
        # info("ROOT : " + userinfo.getHomePath())
        # info("COMP : " + normFullPath)
        if normFullPath == userinfo.getHomePath() :
            inheritable = False
        else :
            inheritable = True
         
        if file_id is not None and file_id >= 0 :
            try :
                descriptor = FileDescriptor.objects.get(file_id=file_id)
                 
                readable    |= descriptor.readable
                writeable   |= descriptor.writeable
                deletable   |= descriptor.deletable
                 
                if not (readable and writeable and deletable) :
                    users = []
                    users.append(userinfo)
                    for user in UserGroups.objects.filter(user=userinfo) :
                        users.append(user.group)
             
                    for userAuthority in UserAuthority.objects.filter(username__in=users, file_id=file_id) :    
                        readable    |= userAuthority.readable
                        writeable   |= userAuthority.writeable
                        deletable   |= userAuthority.deletable
                         
                        if readable and writeable and deletable :
                            break
                 
                if not (readable and writeable and deletable) and inheritable and descriptor.inherit :
                    auth_inherit = Directory.getAuth(userinfo, FileManager.getParent(fullPath))
                    readable    |= auth_inherit[0]
                    writeable   |= auth_inherit[1]
                    deletable   |= auth_inherit[2]
 
            except Exception as err:
                error("auth.dir.get : " + err.__str__())
                pass
            
        elif not userinfo.isGuest() or config.USING_GUEST :
            readable    = config.DEFAULT_AUTH_DIR_READABLE
            writeable   = config.DEFAULT_AUTH_DIR_WRITEABLE
            deletable   = config.DEFAULT_AUTH_DIR_DELETABLE
             
            # 상속받는 경우        
            if not(readable and writeable and deletable) and inheritable and config.DEFAULT_AUTH_DIR_INHERIT :
                auth_inherit = Directory.getAuth(userinfo, FileManager.getParent(fullPath))
             
                readable    |= auth_inherit[0]
                writeable   |= auth_inherit[1]
                deletable   |= auth_inherit[2]
                
        # 만약 guest 활성화 되어있다면 GUEST HOME 에 대한 파일 조회 권한만 부여 한다.            
        if userinfo.isGuest() and normFullPath == config.getHomeGuest() :
            readable = True 
    
        return (readable, writeable, deletable)
    
    @staticmethod
    def isAuthorized(userinfo, fullPath, mode):
        """
        mode     : RWD 를 나타내는 3자리 숫자 배열 (111 ~ 000)
        조회 대상 권한 모두 보유 시 참 반환. 그 외에는 거짓
        """
        auth = Directory.getAuth(userinfo, fullPath, mode)
        isValid = True
        if isValid and mode & 0x04 and not auth[0] :
            isValid = False
        if isValid and mode & 0x02 and not auth[1] :
            isValid = False
        if isValid and mode & 0x01 and not auth[2] :
            isValid = False
        
        return isValid 
