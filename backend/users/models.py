from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class CustomUser(AbstractUser):
    '''Кастомная модель юзера.'''
    email = models.EmailField('Email', unique=True)
    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()])
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    password = models.CharField('Пароль', max_length=150, unique=True)
    is_subscribed = models.BooleanField('Подписка', default=False)

    REQUIRED_FIELDS = ('first_name', 'last_name', 'username')
    USERNAME_FIELD = 'email'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)


class Subscription(models.Model):
    '''Модель Подписки на автора.'''
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Подписчик',
        related_name='follow',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор',
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_following'
            ),
        ]

    def __str__(self):
        return f'{self.user} subscribed to {self.author}'
