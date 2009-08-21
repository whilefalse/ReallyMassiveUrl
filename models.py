from django.db import models

class Url(models.Model):
    slug = models.TextField(default="", max_length=1000)
    redirect_to = models.TextField(default="", max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.redirect_to
