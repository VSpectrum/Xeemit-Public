from django.contrib import admin

# Register your models here.
from django.contrib.auth.models import User
from Xeemit.models import *


class UserProfileDisplay(admin.ModelAdmin):
    def time_seconds(self, obj):
        return obj.Timestamp.strftime("%d-%b-%Y | %H:%M:%S")
    time_seconds.short_description = 'Precise Time'
    list_display = ('user', 'phoneNumber', 'isVerified', 'isPayoutPartner', 'pendingPayment', 'dateCreated')


class UserVerificationDisplay(admin.ModelAdmin):
    list_display = ('userprofile', 'pinNumberSent', 'emailCodeSent', 'trialAttempts', 'isBlocked')


class RequestDisplay(admin.ModelAdmin):
    def time_seconds(self, obj):
        return obj.Timestamp.strftime("%d-%b-%Y | %H:%M:%S")
    time_seconds.short_description = 'Precise Time'
    list_display = ('requestID', 'requestUser', 'lat', 'lng', 'street', 'area' , 'country', 'amount', 'currency', 'status', 'phone', 'isAssigned', 'dateCreated', 'code')


class RequestAssignedDisplay(admin.ModelAdmin):
    def time_seconds(self, obj):
        return obj.Timestamp.strftime("%d-%b-%Y | %H:%M:%S")
    time_seconds.short_description = 'Precise Time'
    list_display = ('requestID', 'PayoutPartner', 'dateCreated')


class PayoutPartnerDetailsDisplay(admin.ModelAdmin):
    def time_seconds(self, obj):
        return obj.Timestamp.strftime("%d-%b-%Y | %H:%M:%S")
    time_seconds.short_description = 'Precise Time'
    list_display = ('userprofile', 'lat', 'lng', 'bank_account', 'street', 'area', 'country')


class TransfersDisplay(admin.ModelAdmin):
    def time_seconds(self, obj):
        return obj.Timestamp.strftime("%d-%b-%Y | %H:%M:%S")
    time_seconds.short_description = 'Precise Time'
    list_display = ('transferID', 'assignedTo', 'amount', 'due')


class CashPickupDisplay(admin.ModelAdmin):
    def time_seconds(self, obj):
        return obj.Timestamp.strftime("%d-%b-%Y | %H:%M:%S")
    time_seconds.short_description = 'Precise Time'
    list_display = ('requestID', 'requestUser', 'lat', 'lng', 'street', 'area' , 'country', 'amount', 'currency', 'status', 'phone', 'assignedTo', 'dateCreated', 'code')


class CurrencyDataDisplay(admin.ModelAdmin):
    def time_seconds(self, obj):
        return obj.Timestamp.strftime("%d-%b-%Y | %H:%M:%S")
    time_seconds.short_description = 'Precise Time'
    list_display = ('currency_code', 'currency_rate', 'dateUpdated')

admin.site.register(UserProfile, UserProfileDisplay)
admin.site.register(UserVerification, UserVerificationDisplay)
admin.site.register(Request, RequestDisplay)
admin.site.register(RequestAssigned, RequestAssignedDisplay)
admin.site.register(PayoutPartnerDetails, PayoutPartnerDetailsDisplay)
admin.site.register(Transfers, TransfersDisplay)
admin.site.register(CashPickup, CashPickupDisplay)
admin.site.register(CurrencyData, CurrencyDataDisplay)
