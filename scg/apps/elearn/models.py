from django.db import models

# Create your models here.
class TestFile(models.Model):
    file = models.FileField(upload_to='test/%Y/%m/%d')
    added = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return self.get_file_url()

    class Admin:
        pass
