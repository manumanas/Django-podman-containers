from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse

# def members(request):     #members -- this name can be different
#     return HttpResponse("Hello world!")
from django.template import loader

def members(request):
  template = loader.get_template('myfirst.html')
  return HttpResponse(template.render())