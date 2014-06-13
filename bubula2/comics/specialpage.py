class SpecialPage(object):
    def view(self, request):
        raise NotImplementedError
    
    def get_image(self):
        raise NotImplementedError
    
    def get_mouseover_text(self):
        raise NotImplementedError