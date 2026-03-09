from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .mongo import user_collection


@receiver(post_delete, sender=User)
def delete_user_from_mongo(sender, instance, **kwargs):

    user_collection.delete_one({
        "email": instance.email
    })