import base64
import socket
from django.contrib.auth.models import User

class LDAPBackend:
    def authenticate(self, username=None, password=None):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('www.princeton.edu', 443))

        ssl_sock = socket.ssl(s)

        # Set a simple HTTP request -- use httplib in actual code.
        ssl_sock.write("GET /~point/validate/validate.html HTTP/1.0\r\nAuthorization: Basic " + base64.b64encode(username+":"+password) + "\r\nHost: www.princeton.edu\r\nConnection: close\r\n\r\n")

        # Read a chunk of data.  Will not necessarily
        # read all the data returned by the server.
        data = ssl_sock.read()

        # Note that you need to close the underlying socket, not the SSL object.
        del ssl_sock
        s.close()

        if data.startswith('HTTP/1.1 200 OK'):
            u = User.objects.get_or_create(username=username, defaults={'is_staff':False,'is_active':True,'is_superuser':False,'email':username+'@princeton.edu'})
            u = u[0]
            u.set_password(password)
            u.save()
            return u
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
