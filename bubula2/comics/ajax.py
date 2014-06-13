from datetime import datetime
from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from comics.shared import get_published_comics

@dajaxice_register
def get_comic_list(request):
    comics = get_published_comics().order_by('-dateTime')
    comicList = []
    for comic in comics:
        comicList.append({
            'id': comic.id,
            'date': datetime.date(comic.dateTime).strftime('%d-%m-%Y'),
            'title': comic.title
        })
    return simplejson.dumps({'comics': comicList})


# TODO: implement this if needed. Probably it's overkill
def get_some_comics_list(request, baseId, direction='init', number=1):
    comicList = []
    if direction == 'up':
        pass
    elif direction == 'down':
        pass
    else:
        pass
    return simplejson.dumps({'comics': comicList})