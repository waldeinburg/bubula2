from django import template
from datetime import datetime, date, timedelta
from comics.models import Comic

register = template.Library()

class ComingComicDateNode(template.Node):
    def __init__(self, varName):
        self.varName = varName
        
    def render(self, context):
        comingComics = Comic.objects.filter( dateTime__gt=datetime.now() ).order_by('dateTime')
        if not len(comingComics):
            value = ''
        else:
            value = comingComics[0].dateTime
            if datetime.date(value) == date.today():
                value = 1
            elif datetime.date(value) == date.today() + timedelta(1):
                value = 2
        if self.varName:
            context[self.varName] = value
            return ''
        return value



@register.tag('coming_comic_date')
def do_coming_comic_date(parser, token):
    tokenList = token.split_contents()
    if (not len(tokenList) == 1
        and not (len(tokenList) == 3
                 and tokenList[1] == 'as')):
        raise template.TemplateSyntaxError("{!r} takes no arguments or \"as <variable>\"".format( token.contents.split()[0] ))
    if len(tokenList) == 3:
        varName = tokenList[2]
    else:
        varName = None
    
    return ComingComicDateNode(varName)