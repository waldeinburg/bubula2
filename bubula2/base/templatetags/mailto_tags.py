import re
from django import template

register = template.Library()

rEmail = re.compile(r'^([A-Z0-9._%+-]+)@([A-Z0-9.-]+)\.([A-Z]{2,4})$', re.IGNORECASE)

class MailtoNode(template.Node):
    def __init__(self, user, hostSub, hostTop):
        self.user = user
        self.hostSub = hostSub
        self.hostTop = hostTop
        
    def render(self, context):        
        return '<span title="Email" class="postbud"><span class="p-u">{user}</span><span class="transmogrifyAffenschwanz"></span><span class="p-s">{hostSub}</span><span class="transmogrifyDaDot"></span><span class="p-t">{hostTop}</span></span>'.format(
            user = self.user,
            hostSub = self.hostSub,
            hostTop = self.hostTop
        )
    


@register.tag('mailto')
def do_mailto(parser, token):
    tokenList = token.split_contents()
    if len(tokenList) < 2:
        raise template.TemplateSyntaxError( '{!r} takes 1 argument'.format( token.contents.split()[0] ) )
    email = tokenList[1]
    mEmail = rEmail.match(email)
    if not mEmail:
        raise template.TemplateSyntaxError( 'First argument for {!r} must be an email-address'.format( token.contents.split()[0] ) )
        
    return MailtoNode( mEmail.group(1), mEmail.group(2), mEmail.group(3) )