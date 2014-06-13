from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

class ComicsApp(CMSApp):
    name = 'Comics App'
    urls = ['comics.urls']
apphook_pool.register(ComicsApp)



class ComicsIndexApp(CMSApp):
    name = 'Comics Index App'
    urls = ['comics.index_urls']
apphook_pool.register(ComicsIndexApp)
