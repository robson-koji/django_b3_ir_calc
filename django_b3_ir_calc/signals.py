import threading

from django.dispatch import receiver
from allauth.account.signals import user_logged_in

class LikeThread(threading.Thread):
    def __init__(self, user, **kwargs):
        self.user = user
        super(LikeThread, self).__init__(**kwargs)

    def run(self):
        # long running code here
        pass


@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    LikeThread(request.user).start()
