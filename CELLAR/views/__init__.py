from django.http.response import HttpResponse
from django.shortcuts import render_to_response, render

from CELLAR.views import cellar, administrator


def simple_response(request, *args, **kwargs):
    template_name = kwargs["path"]
    if kwargs["type"] :
        template_name = kwargs["type"] + "/" + template_name
        
    return HttpResponse(render(request, template_name))