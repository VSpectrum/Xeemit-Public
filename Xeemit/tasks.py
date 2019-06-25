from celery import shared_task
from models import *
from django.core.management import call_command


@shared_task
def set_request_expiry(requestID):
    reqobj = Request.objects.get(requestID=requestID, isAssigned=True)
    req_assigned_obj = RequestAssigned.objects.get(requestID=reqobj)
    if reqobj.status == "Unpaid | Payout Partner Assigned":
        reqobj.isAssigned = False
        reqobj.status = "Unpaid Expired | Needs Payout Partner Approval"
        reqobj.save()
        req_assigned_obj.delete()
        return True
    return False

@shared_task
def update_currency_rates():
    call_command('currency_rates')
    return True