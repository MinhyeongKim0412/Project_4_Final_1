#김민형_0930

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth.models import User
# from .models import Profile, Inventory

# @receiver(post_save, sender=User)
# def create_profile_inventory(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#         Inventory.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_profile_inventory(sender, instance, **kwargs):
#     instance.profile.save()
#     instance.inventory.save()
