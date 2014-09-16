from os.path import os

from django.contrib.auth.models import User
from django.db import models, transaction

from SonienStudio import log
from CELLAR import config

  
# class FileDescriptor(models.Model): 
#     default = [True, False, False]
#     
#     """ 파일 식별자 아이디 """
#     id          = models.AutoField(primary_key = True)
#     
#     """ 대상 구분자 : unique-key """
#     file        = models.TextField()
#     reference   = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE, db_index = True) 
#     
#     """ 파일 기본 권한 """
#     inherit     = models.BooleanField(default = True)
#     readable    = models.BooleanField(default = default[0])
#     writeable   = models.BooleanField(default = default[1])
#     deletable   = models.BooleanField(default = default[2])
#     
#     class Meta:
#         unique_together = ("file", "reference")
#     
#     def __str__(self):
#         return "(%10d) %s" % (self.id, os.path.join(self.path, self.name))
# 
# class UserInfo(models.Model):
#     """ 사용자 타입 """
#     GUEST       = 0
#     NORMAL      = 1
#     GROUP       = 2
#     ADMIN       = 8
#     SUPER       = 9
#     
#     """ 사용자 아이디 """
#     username    = models.TextField(primary_key = True)
#     
#     
#     """ 사용자 기본 정보 """
#     memo        = models.TextField(default = "")
#     usertype    = models.IntegerField(default = GUEST, db_index = True)
#     home        = models.TextField(default = config.HOME_USER)
#     welcome     = models.TextField(default = "")
#     
#     """ 사용자 추가 권한 """
# #     readable    = models.BooleanField(default = True)
# #     writeable   = models.BooleanField(default = False)
# #     deletable   = models.BooleanField(default = False)
#     
#     def isGuest(self):
#         return self.usertype == UserInfo.GUEST
#     
#     def isSuper(self): 
#         return self.usertype == UserInfo.SUPER
#     
#     def getName(self): 
#         return User.objects.get(username = self.username ).first_name
#     
#     def getUserHome(self): 
#         log.info((config.ROOT, config.ROOT + "/" + self.home)[self.home != ""])
#         return (config.ROOT, config.ROOT + "/" + self.home)[self.home != ""]
#         
#     @staticmethod
#     def getUserInfo(request):
#         if request.user.is_authenticated() :
#             userInfo = UserInfo.objects.get(username = request.user.get_username());
#             if request.user.is_superuser :
#                 userInfo.usertype = UserInfo.SUPER 
#                 
#             return userInfo 
#         else :
#             guest           = UserInfo(username = 'guest')
#             guest.home      = config.HOME_GUEST
#             guest.welcome   = ""
#             return guest
# 
# class UserGroups(models.Model):
#     """ 사용자 아이디 """
#     user    = models.ForeignKey(UserInfo, related_name = "UserGroups_username", on_delete=models.CASCADE, db_index = True)
#     group   = models.ForeignKey(UserInfo, related_name = "UserGroups_groupname", on_delete=models.CASCADE, db_index = True)
#     
#     class Meta:
#         unique_together = ("user", "group")
#     
# class UserAuthority(models.Model):
#     username    = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
#     file        = models.ForeignKey(FileDescriptor, on_delete=models.CASCADE, db_index = True)
#     
#     """ 사용자 권한 """
#     readable    = models.BooleanField(default = True)
#     writeable   = models.BooleanField(default = False)
#     deletable   = models.BooleanField(default = False)
#     
#     class Meta:
#         unique_together = ("username", "file")
# # 
# # def isReadable(request, dirname, basename):
# #     if request.user.is_super() :
# #         return True;
