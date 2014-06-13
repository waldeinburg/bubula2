from bubula2 import release, releaseTS #@UnresolvedImport
from django.conf import settings
from datetime import datetime

def page_extra(request):
    subtitle = None
    try:
        subtitle = request.current_page.subtitle
    except:
        pass
    return {
        'page_extra':
            {'subtitle':subtitle},
        'RELEASE': release,
        'RELEASE_TIME': datetime.fromtimestamp(releaseTS)
    }
    
    
# def is_debug_ip(request)
    
    
def settings_for_template(request):
    return {
        'DEBUG': settings.DEBUG,
    }