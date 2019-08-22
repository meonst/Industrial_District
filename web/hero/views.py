from django.shortcuts import render, get_object_or_404, render
from django.http import HttpResponse, Http404
import json
def index(request):
    with open("/Users/smh21/Desktop/prog/silvercity/json/herodata_75589_enus.json", encoding = 'utf-8') as json_file:
        herodata = json.load(json_file)
    herolist = list()
    for i in herodata:
        herolist.append(herodata[i]['name'])

    return render(request, 'hero/hero.html', {'herolist' : herolist})


def heropage(request, heroname):
    with open("/Users/smh21/Desktop/prog/silvercity/json/herodata_75589_enus.json", encoding = 'utf-8') as json_file:
        herodata = json.load(json_file)
    for i in herodata:
        if herodata[i]['name'].lower() == heroname.lower():
            context = {
                'herodata' : herodata[i]
            }
            
            return render(request, 'hero/heropage.html', context)

# Create your views here.
