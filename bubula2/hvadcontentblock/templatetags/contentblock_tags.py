import re
from django import template
#from django.utils.safestring import mark_safe
from hvadcontentblock.models import ContentBlock

register = template.Library()

class ContentBlockNode(template.Node):
    def __init__(self, code, varName):
        self.code = code
        self.varName = varName
    
    def render(self, context):
        try:
            cb = ContentBlock.objects.get(code=self.code)
        except ContentBlock.DoesNotExist:
            return ''
        if not cb.raw:# and not cb.content:
            return ''
        if cb.raw:
            value = cb.raw
#        else:
#            placeholder = cb.content
#            value = mark_safe(placeholder.render(context, None))
        if self.varName:
            context[self.varName] = value
            return ''
        return value




def do_contentblock(parser, token):
    '''
    parses the parameters of the templatetag
    {% contentblock 'my_block_name' %}
    {% contentblock 'my_block_name' as my_varname %}
    '''
    try:
        tagName, arg = token.split_contents()
    except:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])

    m = re.search(r'(.*?) as (\w+)$', arg)
    m2 = re.search(r'(.*?)$', arg)
    if m:
        codeString, varName = m.groups()
    elif m2 and len(m2.groups())==1:
        codeString = m2.groups()[0]
        varName = None
    else:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tagName
    if not (codeString[0] == codeString[-1] and codeString[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tagName)
    return ContentBlockNode(codeString[1:-1], varName)

register.tag('contentblock', do_contentblock)