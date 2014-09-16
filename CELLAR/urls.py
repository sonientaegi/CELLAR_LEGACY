from django.conf.urls import patterns, include, url
from django.contrib import admin

from CELLAR import settings
from CELLAR import views


admin.autodiscover()

urlpatterns = patterns('', 
    url(r'^admin/'              , include(admin.site.urls)),
    url(r'^copyright$'          , views.copyright), 
#     
#     
#     
#     
#     url(r'^administrator$'              , views.administrator, name="administrator"),
#     url(r'^administrator/user/edit$'    , views.administrator_user_edit),
#     url(r'^administrator/user/new$'     , views.administrator_user_new),
#     
#     url(r'^administrator/etc$'  , views.administrator_etc), 
#     url(r'^module/directree$'   , views.module_directree),
#     url(r'^module/filelist$'    , views.module_filelist),
#     url(r'^module/upload$'      , views.module_upload),
#     url(r'^browse/directory$'   , views.browse_directory),
#     url(r'^browse/filelist$'    , views.browse_filelist),
#     url(r'^browse$'             , views.browse),
#     
#     
#     url(r'^util/renamegroup$'   , views.util_renameGroup),
#     url(r'^util/rename$'        , views.util_rename),
#     url(r'^util/move$'          , views.util_move),
#     url(r'^util/createdir$'     , views.util_createDir),
#     url(r'^util/deletedir$'     , views.util_deleteDir),
#     url(r'^util/deletefiles$'   , views.util_deleteFiles), 
#     url(r'^util/upload$'        , views.util_upload),
#     
#     url(r'^auth/reset$'         , views.authority_reset), 
#     url(r'^auth/manager$'       , views.authority_manager),
#     url(r'^auth/default/get$'   , views.authority_getDefault),   
#     url(r'^auth/default/set$'   , views.authority_setDefault),
#     url(r'^auth/default/del$'   , views.authority_delDefault),
#     url(r'^auth/user/check$'    , views.authority_getUser),  
#     url(r'^auth/user/get$'      , views.authority_getUsers), 
#     url(r'^auth/user/set$'      , views.authority_setUsers),
# #  
#     url(r'^user/register$'      , views.user_register),  
#     url(r'^user/login$'                 , views.user_login),
#     url(r'^user/login/(?P<redirect>.*)$', views.user_login),
#     url(r'^user/logout$'        , views.uesr_logout), 
#     url(r'^user/group$'         , views.user_group), 
#     url(r'^user/delete$'        , views.user_delete),
#     url(r'^user/get$'           , views.user_get),
#     url(r'^user/update$'        , views.user_update), 
#     url(r'^user/myinfo$'        , views.user_myinfo), 
# 
#     url(r'^$'                           , views.index, name="index"),
# 
#     url(r'^tarload/(?P<filename>.*)$'   , views.tarload),
#     url(r'^tarload$'                    , views.tarload),
#     url(r'^download/(?P<path>.*)$'      , views.download), 
    url(r'^libs/(?P<path>.*)$'          , 'django.views.static.serve', {'document_root' : settings.BASE_DIR + '/CELLAR/libs'}),
    url(r'^static/(?P<path>.*)$'        , 'django.views.static.serve', {'document_root' : settings.BASE_DIR + '/CELLAR/static'}),
    url(r'^templates/(?P<path>.*)$'     , 'django.views.static.serve', {'document_root' : settings.BASE_DIR + '/CELLAR/templates'}),    
)
