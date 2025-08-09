
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Reservation

@receiver(post_save, sender=Reservation)
def handle_reservation_update(sender, instance, created, **kwargs):
    today_date = timezone.now().date()
    old_reservations = Reservation.objects.filter(date_emprunt__lt=today_date)
    old_reservations.delete()
