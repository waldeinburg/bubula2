# -*- coding: utf-8 -*-
import re
from django.conf import settings
from django import http
from django.utils.html import strip_spaces_between_tags

# http://djangosnippets.org/snippets/744/
class AllowedIpMiddleware(object):
    def process_request(self, request):
        if not request.META['HTTP_X_FORWARDED_FOR'] in settings.DEBUG_IPS: # REMOTE_ADDR useless on WebFaction (proxy)
            return http.HttpResponseForbidden(u'''<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8"/>
        <title>𝔅𝔲𝔟𝔲𝔩𝔞²</title>
    </head>
    <body>
        <h1>𝔅𝔲𝔟𝔲𝔩𝔞² is blocked while under development</h1>
    </body>
</html>''')
        return None



# http://www.soyoucode.com/2011/minify-html-output-django
RE_MULTISPACE = re.compile(r'\s{2,}')
RE_NEWLINE = re.compile(r'\n')

class MinifyHTMLMiddleware(object):
    def process_response(self, request, response):
        if 'text/html' in response['Content-Type'] and getattr(settings, 'COMPRESS_HTML', False):
            response.content = strip_spaces_between_tags(response.content.strip())
            response.content = RE_NEWLINE.sub(" ", response.content)
            response.content = RE_MULTISPACE.sub(" ", response.content)
        return response
    
    
    
class XUACompatibleMiddleware(object):
    def process_response(self, request, response):
        response['X-UA-Compatible'] = 'IE=edge,chrome=1';
        return response
