
class MyBackend(object):
    def authenticate(self, username=None, password=None):
        # Check the username/password and return a User.
        ...

class MyBackend(object):
    def authenticate(self, token=None):
        print('Hello')