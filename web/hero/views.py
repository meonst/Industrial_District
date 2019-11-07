from django.shortcuts import render, get_object_or_404, render
from django.http import HttpResponse, Http404, JsonResponse
import json
def index(request):
    with open("/Users/smh21/Desktop/prog/silvercity/json/herodata_75589_enus.json", encoding = 'utf-8') as json_file:
        herodata = json.load(json_file)
    herolist = list()
    for herolink in herodata:
        herolist.append([herodata[herolink]['name'], herolink])
    return render(request, 'hero/hero.html', {'herolist' : herolist})


def heropage(request, herolink):
    with open("/Users/smh21/Desktop/prog/silvercity/json/herodata_75589_enus.json", encoding = 'utf-8') as json_file:
        herodata = json.load(json_file)
        context = {
            'herodata' : herodata[herolink]
        }
        return JsonResponse(context)

            #return render(request, 'hero/heropage.html', context)

def herotalentshare(request, herolink, share):
    talenttier = [1, 4, 7, 10, 13, 16, 20]
    talentlist = list(share)

    with open("/Users/smh21/Desktop/prog/silvercity/json/herodata_75589_enus.json", encoding = 'utf-8') as json_file:
        herodata = json.load(json_file)
        talents = {
            'talents' : herodata[herolink]['talents']
        }
    context = {}
    for i in range(7):
        for j in talents['talents']['level{}'.format(talenttier[i])]:
            if int(talentlist[i]) == int(j['sort']):
                context.update({'level{}'.format(talenttier[i]) : j})


    return JsonResponse(context, safe=False)



# Create your views here.
