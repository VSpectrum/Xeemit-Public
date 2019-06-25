from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from django.utils import timezone as datetime
from django.utils.translation import ugettext as _
# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    phoneNumber = models.CharField(max_length=18)  # strip dashes and spaces
    isVerified = models.BooleanField(default=False)
    isPayoutPartner = models.BooleanField(default=False)
    dateCreated = models.DateTimeField(default=datetime.now, blank=False)
    pendingPayment = models.BooleanField(default=False)  # this will be toggled true if they are within 4 days of payment, prevents them from being assigned pickups, set false otherwise

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return str(self.user)


def create_user_profile(sender, instance, created, **kwargs):
    profile, created = UserProfile.objects.get_or_create(user=instance)
    UserVerification.objects.get_or_create(userprofile=profile)
post_save.connect(create_user_profile, sender=User) 


class PayoutPartnerDetails(models.Model):
    userprofile = models.ForeignKey(UserProfile)
    lat = models.DecimalField(_('Latitude'), max_digits=10, decimal_places=8, default=0, blank=False)
    lng = models.DecimalField(_('Longitude'), max_digits=11, decimal_places=8, default=0, blank=False)
    bank_account = models.CharField(max_length=30)
    street = models.CharField(max_length=30)
    area = models.CharField(max_length=30)
    country = models.CharField(max_length=5)


    class Meta:
        verbose_name = 'PayoutPartner Details'
        verbose_name_plural = 'PayoutPartner Details'

    def __unicode__(self):
        return self.userprofile.user.username


class UserVerification(models.Model):
    userprofile = models.ForeignKey(UserProfile)
    pinNumberSent = models.CharField(max_length=7)
    trialAttempts = models.IntegerField(blank=False, default=0)
    emailCodeSent = models.CharField(max_length=7, default="")

    # If more than 10 trials attempted change the pinNumberSent and wait until next day at 0:00 to remove block
    isBlocked = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'User Verification'
        verbose_name_plural = 'User Verification'

    def __unicode__(self):
        return self.userprofile.user.username


class Request(models.Model):  # delete user requests older than a week
    requestID = models.AutoField(primary_key=True)
    requestUser = models.ForeignKey(UserProfile)
    lat = models.DecimalField(_('Latitude'), max_digits=10, decimal_places=8, default=0, blank=False)
    lng = models.DecimalField(_('Longitude'), max_digits=11, decimal_places=8, default=0, blank=False)
    street = models.CharField(max_length=30)
    area = models.CharField(max_length=70)
    country = models.CharField(max_length=5)
    amount = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    status = models.CharField(max_length=50)
    isAssigned = models.BooleanField(default=False)
    dateCreated = models.DateTimeField(default=datetime.now, blank=False)
    phone = models.CharField(max_length=20, blank=False)
    code = models.CharField(max_length=6, blank=False)
    currency = models.CharField(max_length=6, blank=False)

    class Meta:
        verbose_name = 'Request'
        verbose_name_plural = 'Requests'

    def __str__(self):
        return str(self.requestID)


class CashPickup(models.Model):  # delete user requests older than a week
    requestID = models.AutoField(primary_key=True)
    requestUser = models.ForeignKey(UserProfile, related_name='Requester')
    lat = models.DecimalField(_('Latitude'), max_digits=10, decimal_places=8, default=0, blank=False)
    lng = models.DecimalField(_('Longitude'), max_digits=11, decimal_places=8, default=0, blank=False)
    street = models.CharField(max_length=30)
    area = models.CharField(max_length=70)
    country = models.CharField(max_length=5)
    amount = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    status = models.CharField(max_length=50, blank=False)
    phone = models.CharField(max_length=20, blank=False)
    assignedTo = models.ForeignKey(UserProfile, related_name='Payout_Partner')
    dateCreated = models.DateTimeField(default=datetime.now, blank=False)
    code = models.CharField(max_length=6, blank=False)
    currency = models.CharField(max_length=6, blank=False)

    class Meta:
        verbose_name = 'Cash Pickup'
        verbose_name_plural = 'Cash Pickup'

    def __str__(self):
        return str(self.requestID)


class Transfers(models.Model):  # Transfers created when status is delivered
    transferID = models.AutoField(primary_key=True)
    assignedTo = models.ForeignKey(UserProfile, related_name='PayoutPartner')
    amount = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    due = models.DateTimeField(blank=False)  # set two weeks from current date, do a daily task: if current date is within 4 days of payment, assign pendingPayment True
    
    class Meta:
        verbose_name = 'Transfers'
        verbose_name_plural = 'Transfers'

    def __str__(self):
        return str(self.transferID)


class RequestAssigned(models.Model):  
    requestID = models.OneToOneField(Request)
    PayoutPartner = models.ForeignKey(UserProfile)
    dateCreated = models.DateTimeField(default=datetime.now, blank=False)  # gen in backend

    class Meta:
        verbose_name = 'Request Assigned'
        verbose_name_plural = 'Requests Assigned'

    def __str__(self):
        return str(self.requestID)


class CurrencyData(models.Model):
    currencyID = models.AutoField(primary_key=True)
    currency_code = models.CharField(max_length=4)
    currency_rate = models.DecimalField(default=0, max_digits=12, decimal_places=6)
    dateUpdated = models.DateTimeField(default=datetime.now, blank=False)

    class Meta:
        verbose_name = 'Currency Mid-Market Rates'
        verbose_name_plural = 'Currency Mid-Market Rates'

    def __str__(self):
        return str(self.currencyID)
