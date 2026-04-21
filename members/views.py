from django.http import HttpResponse
from django.template import loader
from .models import Member
from .models import Person, p1
from django.shortcuts import render

def members(request):
  mymembers = Member.objects.all().values()
  template = loader.get_template('all_members.html')
  context = {
    'mymembers':mymembers,
  }
  
  return HttpResponse(template.render(context, request))

def main(request):
  return render(request, 'main.html')

def details(request, id):
  mymember = Member.objects.get(id=id)
  return render(request, 'details.html', {'mymember': mymember})

def myfirst(request):
  return render(request, 'myfirst.html', {'person':p1})

def testing(request):
  data = Member.objects.all()
  return render(request, 'testing.html', {'members':data})