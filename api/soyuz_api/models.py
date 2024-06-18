from django.db import models


class ExpeditorCheckouts(models.Model):
    ExpeditorId = models.CharField(max_length=1000)
    CustomerId = models.CharField(max_length=1000)
    TimeStamp = models.DateTimeField()
    ServerTimeStamp = models.DateTimeField()
    Status = models.CharField(max_length=1000)

    class Meta:
        managed = False
        db_table = 'ExpeditorCheckouts'
