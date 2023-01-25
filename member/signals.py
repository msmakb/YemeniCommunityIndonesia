import os

from .models import FamilyMembersChild, FamilyMembersWife, Person, Membership


def cleanUpPersonData(sender: Person, instance: Person, *args, **kwargs):
    if instance.photograph and os.path.isfile(instance.photograph.path):
        os.remove(instance.photograph.path)
    if instance.residency_photo and os.path.isfile(instance.residency_photo.path):
        os.remove(instance.residency_photo.path)
    if instance.passport_photo and os.path.isfile(instance.passport_photo.path):
        os.remove(instance.passport_photo.path)
    if instance.membership and instance.membership.membership_card and os.path.isfile(instance.membership.membership_card.path):
        os.remove(instance.membership.membership_card.path)
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


def deleteMembershipCard(sender: Membership, instance: Membership, *args, **kwargs):
    if instance.membership_card and os.path.isfile(instance.membership_card.path):
        os.remove(instance.membership_card.path)


def onUpdatePerson(sender: Person, instance: Person, raw: bool, **kwargs):
    try:
        if not raw:
            this: Person = Person.get(id=instance.id)
            if this.photograph != instance.photograph:
                try:
                    os.remove(this.photograph.path)
                except FileNotFoundError:
                    pass
            if this.passport_photo != instance.passport_photo:
                try:
                    os.remove(this.passport_photo.path)
                except FileNotFoundError:
                    pass
            if this.residency_photo != instance.residency_photo:
                try:
                    os.remove(this.residency_photo.path)
                except FileNotFoundError:
                    pass
    except Person.DoesNotExist:
        pass
