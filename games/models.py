import uuid

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.postgres.fields import JSONField
from django.urls import reverse

from model_utils.models import TimeStampedModel


def generate_token():
    return uuid.uuid4().hex


class HuntingOfSnarkGame(TimeStampedModel):
    token = models.CharField(
        max_length=255,
        unique=True,
        default=generate_token,
    )
    player_name = models.CharField(
        verbose_name='Juego para',
        max_length=255,
        blank=True,
        help_text='Su nombre o el nombre de su amigo con el que quiere jugar'
    )
    total_points = models.IntegerField(
        verbose_name='Cantidad de puntos',
        validators=[MinValueValidator(1), MaxValueValidator(50)],
    )
    criteria = models.ManyToManyField('games.HuntingOfSnarkCriteria')
    extra = JSONField(default=dict())

    def get_absolute_url(self):
        return reverse('games:hunting_of_snark_detail', args=[self.token])


class HuntingOfSnarkCriteria(TimeStampedModel):
    RANDOM_LETTER_CRITERIA_ID = 240

    public_id = models.PositiveIntegerField(
        unique=True,
    )
    name = models.CharField(
        max_length=500,
        unique=True,
    )
    category = models.ForeignKey(
        'games.HuntingOfSnarkCategory',
        related_name='criteria',
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('public_id',)


class HuntingOfSnarkCategory(TimeStampedModel):
    name = models.CharField(
        max_length=500,
        unique=True,
    )
    order = models.FloatField(
        null=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Hunting Of Snark Category'
        verbose_name_plural = 'Hunting Of Snark Categories'
        ordering = ('order',)
