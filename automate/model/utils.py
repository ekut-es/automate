class Templateable(object):

    def __init__(self):
        template_dict = {}

    def __getattr__(self, name):
        template_dict = {}
