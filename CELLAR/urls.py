from django.conf.urls           import patterns, include, url
from django.contrib             import admin

from CELLAR                     import settings, views


admin.autodiscover()

urlpatterns = patterns('', 
    url(r'^admin/'                      , include(admin.site.urls)),
    
    url(r'^$'                           , views.cellar.main, name="cellar"),
    url(r'^copyright$'                  , views.cellar.copyrightPage),
    url(r'^administrator$'              , views.administrator.general, name="administrator"),
    url(r'^administrator/user/edit$'    , views.administrator.userEdit),
    url(r'^administrator/user/new$'     , views.administrator.userNew),
    url(r'^administrator/etc$'          , views.administrator.etc),
     
    url(r'^module/directree$'           , views.cellar.directree),
    url(r'^module/filelist$'            , views.cellar.filelist),
    url(r'^module/upload$'              , views.cellar.upload),
    url(r'^myinfo$'                     , views.cellar.myinfo),
    url(r'^signup$'                     , views.cellar.signup),  
    
    url(r'^browse/directory$'           , views.util.browseDirectory),
    url(r'^browse/filelist$'            , views.util.browseFilelist),
    url(r'^browse$'                     , views.util.browse),
    url(r'^upload$'                     , views.util.upload),  
#     url(r'^util/renamegroup$'   , views.util_renameGroup),
#     url(r'^util/rename$'        , views.util_rename),
#     url(r'^util/move$'          , views.util_move),
    url(r'^util/createdir$'             , views.util.createDir),
    url(r'^util/deletedir$'             , views.util.deleteDir),
    url(r'^util/deletefiles$'           , views.util.deleteFiles), 
    
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
#     
    url(r'^user/login$'                 , views.util.userLogin),
    url(r'^user/login/(?P<redirect>.*)$', views.util.userLogin),
    url(r'^user/logout$'                , views.util.uesrLogout), 
#     url(r'^user/group$'         , views.user_group), 
    url(r'^user/delete$'                , views.util.userDelete),
    url(r'^user/get$'                   , views.util.userGet),
    url(r'^user/update$'                , views.util.userUpdate), 
  
    url(r'^tarload/(?P<filename>.*)$'   , views.util.tarload),
    url(r'^tarload$'                    , views.util.tarload),
    url(r'^download/(?P<filepath>.*)$'  , views.util.download), 
    url(r'^libs/(?P<path>.*)$'          , 'django.views.static.serve', {'document_root' : settings.BASE_DIR + '/CELLAR/libs'}),
    url(r'^static/(?P<path>.*)$'        , 'django.views.static.serve', {'document_root' : settings.BASE_DIR + '/CELLAR/static'}),
    url(r'^templates/(?P<path>.*)$'     , 'django.views.static.serve', {'document_root' : settings.BASE_DIR + '/CELLAR/templates'}),    
)
