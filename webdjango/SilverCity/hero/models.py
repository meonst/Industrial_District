from django.db import models

class Hero(models.Model):
    Hero_name = models.CharField(max_length = 100)
    pub_date = models.DateTimeField('Date Realeased')
    def __str__(self):
        return self.Hero_name
# Create your models here.
