import datetime
from django.db import models
from django.utils import timezone

# Create your models here.

class Questions(models.Model):
    question_text =  models.CharField(max_length=200)
    pub_date = models.DateTimeField("Date Published")

    def __str__(self):
        return self.question_text
    # def was_published_recently(self):
    #     return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    # for testing purpose
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    question = models.ForeignKey(Questions , on_delete=models.CASCADE )
    choice_text =  models.CharField(max_length=200)
    votes = models.IntegerField(default=0) 

    def __str__(self):
        return self.choice_text
