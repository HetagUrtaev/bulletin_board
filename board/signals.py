from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from .models import Response


@receiver(post_save, sender=Response)
def my_handler(sender, instance, created, update_fields, **kwargs):



    if instance.status == 'pending':
        return

    send_mail(
        subject='Изменение статуса отклика',
        message=f'Ваш отклик на публикацию - {instance.ad.title} - получил статус: {instance.get_status_display()}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[instance.author.email],
        fail_silently=False
    )


