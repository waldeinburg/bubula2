from django.utils import simplejson
from django.conf import settings
from dajaxice.decorators import dajaxice_register
from copyhvadfilefield.register import models
from django.http import HttpResponseForbidden

@dajaxice_register
def copy_from_other(request, curLang, modelStr, field, objId):
    if not request.user.is_staff:
        return HttpResponseForbidden
    try:
        model = models[modelStr]
    except KeyError:
        return simplejson.dumps({
            'success': False,
            'errorMsg': 'The model with the name "{0}" is not registered!'.format(modelStr)
        })
    newFile = ''
    doesNotExistException = getattr(model, 'DoesNotExist')
    # get first available other file and set to this
    # curLang is the selected tab, not necessarily equal to django.utils.translation.get_language()
    for lang in settings.LANGUAGES:
        if lang[0] != curLang:
            try:
                otherFile = getattr( model.objects.language(lang[0]).get(id=objId), field )
                if otherFile:
                    newFile = otherFile
                    # get the object in the selected language or create it
                    try:
                        obj = model.objects.language(curLang).get(id=objId)
                    except doesNotExistException:
                        obj = model.objects.get(id=objId)
                        obj.translate(curLang)
                    setattr(obj, field, newFile)
                    obj.save()
                    break
            except doesNotExistException: # no field in that language
                pass
    if not newFile:
        return simplejson.dumps({
            'success': False,
            'errorMsg': 'None of the other languages has specified this field!'
        })            
    return simplejson.dumps({
        'success': True,
        'newFile': str(newFile),
        'newUrl': '{0}{1}'.format(settings.MEDIA_URL, newFile)
    })
