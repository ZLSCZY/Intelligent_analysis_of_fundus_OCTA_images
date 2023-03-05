from django.db import models


# Create your models here.


class User(models.Model):
    account = models.CharField(primary_key=True, max_length=64)
    password = models.CharField(max_length=64)
    identity = models.CharField(max_length=2, blank=True, null=True)
    case_number = models.PositiveIntegerField(db_column='case-number', blank=True,
                                              null=True)  # Field renamed to remove unsuitable characters.

    class Meta:
        managed = True
        db_table = 'User'
