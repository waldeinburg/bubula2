from bubula2 import version
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
        'VERSION': version,
    }
    
    
# def is_debug_ip(request)
    
    
def settings_for_template(request):
    return {
        'DEBUG': settings.DEBUG,
    }
