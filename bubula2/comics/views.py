from datetime import datetime
from django.template import loader
from django.template.context import RequestContext
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from comics.models import Comic
from comics.shared import get_published_comics

def get_latest_comic():
    return get_published_comics().order_by('-id')[0] # this assumes we have comics


def render_single_to_response(request, comic, template='comics/single.html', contextDict=None):
    t = loader.get_template(template)
    c = RequestContext(request)
    thisId = comic.id
    # The out-commented alternatives should not be necessary because a webcomic should follow a strict id sequence
    firstId = 1
#    firstId = Comic.objects.order_by('dateTime')[0].id
    if firstId == thisId:
        firstId = 0
    latestId = get_published_comics().order_by('-dateTime')[0].id
    if latestId == thisId:
        latestId = 0
    prevId = 0
    if firstId:
        prevId = thisId - 1
#        prevId = Comic.objects.filter(dateTime__lt=comic.dateTime).order_by('-dateTime')[0].id
    nextId = 0
    if latestId:
        nextId = thisId + 1
#        nextId = Comic.objects.filter(datetime__gt=comic.dateTime).order_by('dateTime')[0].id
    c.update({
        'baseUrl': request.build_absolute_uri('/')[:-1],
        'comic': comic,
        'comicTemplate': 'comics/types/{0}.html'.format( comic.type.lower() ),
        'title': comic.title,
        'subtitle': comic.get_comic_obj().pageSubtitle,
        'firstId': firstId,
        'latestId': latestId,
        'prevId': prevId,
        'nextId': nextId
    })
    if contextDict:
        c.update(contextDict)
    return HttpResponse( t.render(c) )


# index is basically the same as the latest view, except that the template includes content from another page
def index(request):
    latestComic = get_latest_comic()
    return render_single_to_response(request, latestComic, template='comics/index.html')


# TODO: get_published_comic_or_404
def single(request, comicId):
    cDict = None
    try:
        comic = Comic.objects.get(id=comicId)
    except Comic.DoesNotExist:
        raise Http404
    if not comic.is_published():
        if request.user.is_staff:
            cDict = {'comicPreview':True}
        else:
            raise Http404
    return render_single_to_response(request, comic, contextDict=cDict)


def single_by_date(request, dateStr):
    try:
        date = datetime.strptime(dateStr, '%d-%m-%Y')
    except ValueError: # invalid date
        raise Http404
    comics = get_published_comics().filter(dateTime__year=date.year,
                                           dateTime__month=date.month,
                                           dateTime__day=date.day)
    if not len(comics):
        raise Http404
    # TODO: implement multiple comics view
    # If, for some reason, we posted several comics in one day, only one is returned
    return redirect( comics[0] )


def latest(request):
    return redirect( get_latest_comic(), False )


def random(request):
    return redirect( get_published_comics().order_by('?')[0], False )


def single_redirect(request, comicId):
    try:
        comic = get_published_comics().get(id=comicId)
    except Comic.DoesNotExist:
        raise Http404
    return redirect(comic, False)