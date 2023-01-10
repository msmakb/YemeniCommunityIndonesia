import os

from .models import FamilyMembersChild, FamilyMembersWife, Person


def cleanUpPersonData(sender: Person, instance: Person, *args, **kwargs):
    if instance.photograph:
        os.remove(instance.photograph.path)
    if instance.residency_photo:
        os.remove(instance.residency_photo.path)
    if instance.passport_photo:
        os.remove(instance.passport_photo.path)
    if instance.account:
        temp = instance.account
        temp.delete()
    if instance.membership:
        temp = instance.membership
        temp.delete()
    for temp in FamilyMembersWife.filter(family_members=instance.family_members):
        temp.delete()
    for temp in FamilyMembersChild.filter(family_members=instance.family_members):
        temp.delete()
    temp = instance.family_members
    temp.delete()
    temp = instance.address
    temp.delete()
    temp = instance.academic
    temp.delete()
