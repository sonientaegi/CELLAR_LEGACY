from os.path import os

from django.contrib.auth.models     import User
from django.core.exceptions         import ObjectDoesNotExist
from django.db                      import models, transaction

from CELLAR                         import config
from SonienStudio.log               import *


global config

class FileDescriptor(models.Model): 
    default = [True, False, False]
     
    """ 파일 또는 경로 식별자 """
    file_id    = models.AutoField(primary_key = True)
     
    """ 대상 구분자 : unique-key """
    file        = models.TextField()
    reference   = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE, db_index = True) 
     
    """ 파일 기본 권한 """
    inherit     = models.BooleanField(default = True)
    readable    = models.BooleanField(default = default[0])
    writeable   = models.BooleanField(default = default[1])
    deletable   = models.BooleanField(default = default[2])
     
    class Meta:
        unique_together = ("file", "reference")
        
class UserInfo(models.Model):
    """ 사용자 타입 """
    GUEST       = 0
    NORMAL      = 1
    GROUP       = 2
    ADMIN       = 8
    SUPER       = 9
     
    """ 사용자 아이디 """
    username    = models.TextField(primary_key = True)
     
    """ 사용자 기본 정보 """
    memo        = models.TextField(default = "")
    usertype    = models.IntegerField(default = GUEST, db_index = True)
    home        = models.TextField(default = config.HOME_USER)
    welcome     = models.TextField(default = "")
     
    """ 사용자 추가 권한 """     
    def isGuest(self):
        return self.usertype == UserInfo.GUEST
     
    def isSuper(self): 
        return self.usertype == UserInfo.SUPER
     
    def getName(self): 
        return User.objects.get(username = self.username ).first_name
     
    def getHomePath(self): 
        return (config.ROOT, config.ROOT + "/" + self.home)[self.home != ""]

    def __str__(self):
        return "%s (%s)" % (self.username, self.getName())
    
         
    @staticmethod
    def getUserInfo(request):
        if request.user.is_authenticated() :
            userInfo = None
            username = request.user.get_username()
            try :
                userInfo = UserInfo.objects.get(username = username);
                # django 관리자는 자동적으로 SUPER USER 권한 부여
                if request.user.is_superuser :
                    userInfo.usertype = UserInfo.SUPER
                    
            except ObjectDoesNotExist as err :
                error("%s : %s" % (username, err.__str__()))
                # Userinfo 미 존재 시, 관리자에 한하여 자동 생성
                if request.user.is_superuser :
                    userinfo = UserInfo(username=username, usertype=UserInfo.SUPER)
                    userinfo.save()
                 
            return userInfo 
        else :
            guest           = UserInfo(username = 'guest')
            guest.home      = config.HOME_GUEST
            guest.welcome   = ""
            return guest

class UserGroups(models.Model):
    """ 사용자 아이디 """
    user    = models.ForeignKey(UserInfo, related_name = "UserGroups_username", on_delete=models.CASCADE, db_index = True)
    group   = models.ForeignKey(UserInfo, related_name = "UserGroups_groupname", on_delete=models.CASCADE, db_index = True)
     
    class Meta:
        unique_together = ("user", "group")
     
class UserAuthority(models.Model):
    username    = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    file_id     = models.ForeignKey(FileDescriptor, on_delete=models.CASCADE, db_index = True)
     
    """ 사용자 권한 """
    readable    = models.BooleanField(default = True)
    writeable   = models.BooleanField(default = False)
    deletable   = models.BooleanField(default = False)
     
    class Meta:
        unique_together = ("username", "file_id")
