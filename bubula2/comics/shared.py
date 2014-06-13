# Code that is shared by plugin and app
from datetime import datetime
from comics.models import Comic

def get_published_comics():
    return Comic.objects.filter(dateTime__lte=datetime.now())