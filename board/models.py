from ckeditor_uploader.fields import RichTextUploadingField
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
import random
import string
from django.utils import timezone
from datetime import timedelta


CATEGORY_CHOICES = [
    ('tanks', 'Танки'),
    ('healers', 'Хилы'),
    ('dd', 'ДД'),
    ('traders', 'Торговцы'),
    ('guildmasters', 'Гилдмастеры'),
    ('questgivers', 'Квестгиверы'),
    ('smiths', 'Кузнецы'),
    ('leatherworkers', 'Кожевники'),
    ('alchemists', 'Зельевары'),
    ('spellmasters', 'Мастера заклинаний'),
]

RESPONSE_STATUSES = [
    ('pending', 'Ожидает'),
    ('accepted', 'Принят'),
    ('rejected', 'Отклонён'),
]


# пользователь
class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    game_nickname = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
        verbose_name="Игровой ник"
    )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return self.game_nickname or self.user.username


# категории
class Category(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        choices=CATEGORY_CHOICES,
        verbose_name="Категория"
    )

    def clean(self):
        super().clean()
        valid_choices = [choice[0] for choice in CATEGORY_CHOICES]
        if self.name not in valid_choices:
            raise ValidationError({
                'name': f"Выберите допустимое значение. '{self.name}' не разрешено."
            })

    def save(self, *args, **kwargs):
        self.clean()  # Вызов валидации перед сохранением
        super().save(*args, **kwargs)


    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.get_name_display()


# объявления
class Ad(models.Model):
    """
    нужно ли добавить поле типа FileField?
    """
    title = models.CharField(
        max_length=250,
        verbose_name='Заголовок'
    )
    content = RichTextUploadingField(
        'Содержимое статьи',
        config_name='default',
        blank=True,
        null=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        verbose_name="Категория",

    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Последнее обновление'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'

    def __str__(self):
        return self.title


# отклики
class Response(models.Model):
    ad = models.ForeignKey(
        Ad, on_delete=models.CASCADE,
        related_name='responses',
        verbose_name="Объявление"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор отклика"
    )
    content =  models.TextField(
        max_length=2000,
        verbose_name="Текст отклика"
    )
    status = models.CharField(
        max_length=10,
        choices=RESPONSE_STATUSES,
        default='pending', verbose_name="Статус"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        unique_together = ('author', 'ad') # для уникальности отклика и поста
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'

    def __str__(self):
        return f'Отклик на {self.ad.title} от {self.author.username}'


# одноразовый пароль
class OneTimeCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.code:

            self.code = ''.join(random.choices(string.digits, k=6))
        super().save(*args, **kwargs)

    @classmethod
    def is_code_valid(cls, user, code):
        try:
            otp = cls.objects.get(user=user, code=code, is_used=False)

            if timezone.now() - otp.created_at <= timedelta(minutes=15):
                return True
            return False
        except cls.DoesNotExist:
            return False

    @classmethod
    def mark_as_used(cls, user, code):
        otp = cls.objects.get(user=user, code=code)
        otp.is_used = True
        otp.save()