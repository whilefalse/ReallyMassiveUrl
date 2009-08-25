from django.http import HttpResponse, HttpResponseForbidden, HttpResponsePermanentRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.template import defaultfilters
import random,string,os, codecs
from models import Url

def home(request):
    if request.method == "POST":
        url = request.POST['url']
        captcha = request.POST['captcha']
        
        if captcha != "If you're a person then ignore this":
            return HttpResponseForbidden("Go away bot")

        if int(request.POST['length']) > 50:
            length =  50
        else:
            length = int(request.POST['length'])

        ok=False
        while not ok:
            random_words = randomwords(length)
            slug = defaultfilters.slugify("-".join(random_words))
            
            if len(slug) >255:
                slug = slug[:254]
            
            try:
                url = Url.objects.get(slug__exact=slug)
                print "Exists"
                ok=False
            except ObjectDoesNotExist:
                ok=True
        
        Url.objects.create(slug=slug, redirect_to=request.POST['url'])
        
        return render_to_response('home.html', {'url':current_host(request)+slug}, context_instance=RequestContext(request))
        
    
    return render_to_response('home.html', context_instance=RequestContext(request))


def redirect(request, slug):
    url = get_object_or_404(Url,slug__exact=slug)
    url = url.redirect_to
    
    if url[0:4] != "http":
        url = "http://"+url
    
    return HttpResponsePermanentRedirect(url)


def randomwords(num):
    stat = os.stat('/usr/share/dict/words')
    # the filesize if the 7th element of the array
    flen = stat[6]
    f = open('/usr/share/dict/words','r')
    words = []
    while len(words) < num:
    # seek to a random offset in the file
        f.seek(int(random.random() * flen))
    # do a single read with sufficient characters
        chars = f.read(50)

    # split it on white space
        wrds = string.split(chars)
    # the first element may be only a partial word so use the second
    # you can also make other tests on the word here
    
        if len(wrds) > 1:
            word = unicode(wrds[1], 'Latin-1')
        else:
            continue
    
        words.append(word)
        
    return words



def current_host(request):
    url = 'http://%s' % request.META['SERVER_NAME']
    if request.META['SERVER_PORT'] != 80 and request.META['SERVER_NAME'] == 'localhost':
        url = url + ':%s' % request.META['SERVER_PORT']
    url = url + '/'
    return url
