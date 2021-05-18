from django.conf import settings
from django.db import models
from django.urls import reverse


class List(models.Model):
    """список"""
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL)

    @property
    def name(self):
        """имя"""
        return self.item_set.first().text

    def get_absolute_url(self):
        """получить абсолютный url"""
        return reverse('view_list', args=[self.id])


class Item(models.Model):
    """элемент списка"""
    text = models.TextField(default='')
    list = models.ForeignKey(List, default=None, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

    class Meta:
        unique_together = ('list', 'text')
        ordering = ('pk',)
