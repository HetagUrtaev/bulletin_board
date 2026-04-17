from Bulletin_Board.celery import app  # правильный импорт экземпляра
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from .models import Ad
from django.contrib.auth.models import User


@app.task
def send_recent_ads_hourly(hours=1):
    email_list = list(
        User.objects
        .exclude(email__in=[None, ''])
        .values_list('email', flat=True)
    )
    time_ago = timezone.now() - timezone.timedelta(hours=hours)
    recent_ads = Ad.objects.filter(created_at__gte=time_ago)


    if not recent_ads:
        send_mail(
            subject=f'За последний час нет публикаций',
            message='за последний час публикаций нет',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=email_list,
            fail_silently=False,
        )
        print('Отправлены сообщения')
        return
    send_mail(
        subject=f'За последний час было {len(recent_ads)} публикаций',
        message=f'За последний час было {len(recent_ads)} публикаций',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=email_list,
        fail_silently=False,
    )
    return
