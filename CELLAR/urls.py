from django.conf.urls           import patterns, include, url
from django.contrib             import admin
import django.shortcuts

from CELLAR                     import settings, views


admin.autodiscover()

urlpatterns = patterns('',  
    # External libraries
    url(r'^libs/(?P<path>.*)$'          , 'django.views.static.serve', {'document_root' : settings.BASE_DIR + '/CELLAR/libs'}),
                           
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
    url(r'^util/renamegroup$'           , views.util.renameGroup),
    url(r'^util/rename$'                , views.util.rename),
    url(r'^util/move$'                  , views.util.move), 
    url(r'^util/createdir$'             , views.util.createDir),
    url(r'^util/deletedir$'             , views.util.deleteDir),
    url(r'^util/deletefiles$'           , views.util.deleteFiles), 
        
    url(r'^auth/manager$'               , views.cellar.authorityManager),
    url(r'^auth/reset$'                 , views.util.resetAllAuthority),
    url(r'^auth/default/get$'           , views.util.getDefaultAuthority),   
    url(r'^auth/default/set$'           , views.util.setDefaultAuthority),
    url(r'^auth/default/del$'           , views.util.delDefaultAuthority),
    url(r'^auth/user/check$'            , views.util.getUserAuthority),  
    url(r'^auth/user/get$'              , views.util.getAuthorizedUsers), 
    url(r'^auth/user/set$'              , views.util.setAuthorizedUsers),
 
    url(r'^user/login$'                 , views.util.userLogin),
    url(r'^user/login/(?P<redirect>.*)$', views.util.userLogin),
    url(r'^user/logout$'                , views.util.uesrLogout), 
    url(r'^user/delete$'                , views.util.userDelete),
    url(r'^user/get$'                   , views.util.userGet),
    url(r'^user/update$'                , views.util.userUpdate), 
  
    url(r'^tarload/(?P<filename>.*)$'   , views.util.tarload),
    url(r'^tarload$'                    , views.util.tarload),
    url(r'^download/(?P<filepath>.*)$'  , views.util.download), 
    
    url(r'^(?P<path>.+\.js)$'           , views.simple_response, {'type' : 'scripts'}),
    url(r'^(?P<path>.+\.css)$'          , 'django.views.static.serve', {'document_root' : settings.BASE_DIR + '/CELLAR/templates'}),
    url(r'^static/(?P<path>.*)$'        , 'django.views.static.serve', {'document_root' : settings.BASE_DIR + '/CELLAR/static'}),    
)