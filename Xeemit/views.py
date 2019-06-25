from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, JsonResponse, HttpResponseServerError, HttpResponseBadRequest
from django.contrib.sessions.models import Session
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from Xeemit.models import *
from ChatServer.models import ChatKey, RequestChat

from collections import Counter, defaultdict, OrderedDict
import hashlib, random, json, datetime
from decimal import Decimal
from sms import *
from emailer import *
import random, json, re

from password_required.decorators import password_required

from math import radians, cos, sin, asin, sqrt
from ratelimit.decorators import ratelimit
from workdays import *

from tasks import set_request_expiry

REQUEST_EXPIRY_TIME = 60*60  # 60*60*3  # seconds request expires after being taken by payout partner
PROFIT_PERCENT = 115  # 115% made on each transaction
from ProjXeemit.settings import SERVER_ADDRESS

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the distance between two points on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km

@password_required
def homepage(request):
    if request.user.is_authenticated():
        loggeduser = UserProfile.objects.get(user=request.user)
        data = {
            'isVerified': loggeduser.isVerified,
            'isPayoutPartner': loggeduser.isPayoutPartner,
            'user': User.objects.get(username=request.user),
            'serverAddress': SERVER_ADDRESS
        }
        return render_to_response('home.html', data, context_instance=RequestContext(request))
    else:
        return render_to_response('index.html', context_instance=RequestContext(request))


@login_required(login_url='/')
def userhome(request):
    return render_to_response('home.html')


@login_required
@ratelimit(key='post:ADD', rate='1/10s', method=ratelimit.UNSAFE, block=True)
def requesthandler(request):
    requestUser = UserProfile.objects.get(user=request.user)
    data = ''
    if request.method == 'POST':  # handler for when request is first made

        if request.POST.get('DELETE', 0):
            requestID = int(request.POST.get('requestID', 0))
            pprint(requestID)
            Request.objects.filter(requestID=requestID).filter(requestUser=requestUser).delete() #can only be deleted by creator
            return HttpResponse('Ok')

        elif request.POST.get('ADD', 0): #user adding transaction to be made
            lat = Decimal(request.POST.get('lat', 0))
            lng = Decimal(request.POST.get('lng', 0))
            street = str(request.POST.get('street', ''))
            area = str(request.POST.get('area', ''))
            country = str(request.POST.get('country', ''))
            amount = Decimal(request.POST.get('amount', 0))
            status = "Unpaid | Needs Payout Partner Approval"
            phone = str(request.POST.get('recip_phone_number', ''))
            email = str(request.POST.get('recip_email', ''))
            currency = str(request.POST.get('currency', ''))
            code = ''.join(random.choice('23456789abcdefghijkmnpqrstuvwxyz') for i in range(6))
            isAssigned = False

            msg = "-Do Not Delete-\nShow to XEEMIT Partner only IN PERSON\nCODE: "+code+"\nCURRENCY: "+str(currency)+"\nRECEIVE: $"+str(amount)
            if not textmsg(phone, msg, country):
                return HttpResponse('Request Cannot be made. Invalid Phone Number.')

            if request.POST.get('pickup_amount', 0): #CASH PICKUP!
                mylat = Decimal(request.POST.get('my_lat', 0))
                mylng = Decimal(request.POST.get('my_lng', 0))
                mystreet = str(request.POST.get('my_street', ''))
                myarea = str(request.POST.get('my_area', ''))
                mycountry = str(request.POST.get('my_country', ''))
                myamount = Decimal(request.POST.get('pickup_amount', 0))
                phone_number = str(request.POST.get('phone_number', ''))
                myemail = str(request.POST.get('pickup_email', ''))
                mycurrency = str(request.POST.get('pickup_currency', ''))
                mycode = ''.join(random.choice('23456789abcdefghijkmnpqrstuvwxyz') for i in range(6))

                payoutpartner_list = UserProfile.objects.filter(isPayoutPartner=True, pendingPayment=False)
                pp_bycountry = []
                for user in payoutpartner_list:
                    pp_bycountry.append(PayoutPartnerDetails.objects.get(country=mycountry, userprofile=user))

                transfers_list = {}
                today = datetime.datetime.today()
                for user in pp_bycountry:
                    summed = sum(y.amount for y in Transfers.objects.filter(assignedTo=user.userprofile, due__gt=today))
                    if summed >= myamount:
                        transfers_list[user.userprofile] = summed

                # transfers_list contains users who are owed above the required amount. Now to find the nearest one!

                nearest_qualified_pp = {}
                for userprof in transfers_list.keys():
                    x = PayoutPartnerDetails.objects.get(userprofile=userprof)
                    distance = haversine(x.lng, x.lat, mylng, mylat)
                    if distance < 30:
                        nearest_qualified_pp[userprof] = distance

                if nearest_qualified_pp:
                    nearest_pp = min(nearest_qualified_pp, key=nearest_qualified_pp.get)

                    # reduce transfers up until amount is met

                    pp_transfers = Transfers.objects.filter(assignedTo=nearest_pp, due__gt=today)
                    tempamt = myamount
                    for transfer in pp_transfers: # sorting pp_transfers to determine which payments are negated can be a future development
                        if tempamt < transfer.amount:
                            transfer.amount -= tempamt
                        else:
                            tempamt -= transfer.amount
                            transfer.amount = 0
                        transfer.save()

                    msg = "-Do Not Delete-\nShow to XEEMIT PARTNER\nCODE: "+code+"\nCURRENCY: "+str(mycurrency)+"\nGIVE: $"+str(myamount)
                    if not textmsg(phone, msg, mycountry):
                        return HttpResponse('Request Cannot be made. Invalid Phone Number.')

                    CashPickup.objects.create(requestUser=requestUser, lat=mylat, lng=mylng, street=mystreet, area=myarea, country=mycountry, amount=myamount, phone=phone_number, assignedTo=nearest_pp, code=mycode, currency=mycurrency)

                else:
                    return HttpResponse('Request Cannot be made. No active Payout Partners in proximity.')

            reqobj = Request.objects.create(requestUser=requestUser, lat=lat, lng=lng, street=street, area=area, country=country, amount=amount, status=status, isAssigned=isAssigned, phone=phone, code=code, currency=currency)

            chatkey = pin = ''.join(random.choice('123456789qwertyuip') for i in range(55))
            ChatKey.objects.create(request=reqobj, key=chatkey)

            data = {
                'userRequests': [reqobj],
            }


            return render_to_response('yourrequests.html', data, context_instance=RequestContext(request))

        elif request.POST.get('REQUEST', 0): #payment partner requesting this transaction
            if requestUser.isPayoutPartner:
                requestID = int(request.POST.get('requestID', 0))

                reqobj = Request.objects.get(requestID=requestID, isAssigned=False)
                req_assigned = RequestAssigned.objects.create(PayoutPartner=requestUser, requestID=reqobj)
                reqobj.isAssigned = True
                reqobj.status = "Unpaid | Payout Partner Assigned"
                reqobj.save()

                #Request expires after x amount of time --
                set_request_expiry.apply_async(args=[requestID], countdown=REQUEST_EXPIRY_TIME)
                #set_request_expiry.delay(requestID)

                return HttpResponse('Ok')

    if request.method == 'GET':
        if request.GET['hash'] == "sendrequests":
            userRequests = Request.objects.filter(requestUser=requestUser).exclude(status__contains="Delivered|Completed")
            data = {
                'userRequests': userRequests,
            }
            return render_to_response('yourrequests.html', data, context_instance=RequestContext(request))

        if request.GET['hash'] == "requests":
            if requestUser.isPayoutPartner:
                userRequests = Request.objects.filter(isAssigned=False).exclude(requestUser=requestUser).exclude(status__contains="Delivered|Completed")
                pprint(userRequests)
                data = {
                    'userRequests': userRequests,
                }
                return render_to_response('yourrequests.html', data, context_instance=RequestContext(request))

        if request.GET['hash'] == "deliveries":
            if requestUser.isPayoutPartner:
                userRequests = [x.requestID for x in RequestAssigned.objects.filter(PayoutPartner=requestUser) if x.requestID.status != "Delivered|Completed"]
                pprint(userRequests)
                data = {
                    'userRequests': userRequests,
                }
                return render_to_response('deliveries.html', data, context_instance=RequestContext(request))
        
        if request.GET['hash'] == "pickups":
            if requestUser.isPayoutPartner:
                userRequests = CashPickup.objects.filter(assignedTo=requestUser).exclude(status__contains="Delivered|Completed")
                pprint(userRequests)
                data = {
                    'userRequests': userRequests,
                }
                return render_to_response('pickups.html', data, context_instance=RequestContext(request))
    return render_to_response('home.html', data, context_instance=RequestContext(request))

def registration(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']

        #check if email unique, check if username unique

        user = User.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)

        #send email verification ?

        return redirect('/')

def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth_login(request, user)
            return redirect("/")
            # requestUser = UserProfile.objects.get(user=user)
            # if requestUser.isVerified:
            #     auth_login(request, user)
            #     return redirect("/")
            # else:
            #     return HttpResponse('User is not verified via email')
        else:
            return HttpResponse('User is disabled.')
    else:
        return HttpResponse('Username does not exist.')


@login_required
def phonevalidation(request):
    if request.method == 'POST':
        phonenumber = request.POST['phoneNumber']
        userobj = UserProfile.objects.get(user=request.user)
        userobj.phoneNumber = phonenumber
        userobj.save()

        userverificationobj = UserVerification.objects.get(userprofile=userobj)
        userverificationobj.trialAttempts += 1

        if userverificationobj.trialAttempts <= 10 and not userverificationobj.isBlocked:
            pin = ''.join(random.choice('123456789qwertyuip') for i in range(6))
            userverificationobj.pinNumberSent = pin
            userverificationobj.save()
            try:
                verification_textmsg(phonenumber, pin)
                return HttpResponse('ok')
            except ValueError:
                return HttpResponse('Error sending message! - '+str(ValueError))
        else:
            return HttpResponse('Trial attempts exceeded allowed amount. Wait until next day.')

    return HttpResponse('Error')

@login_required
def emailvalidation(request):
    if request.method == 'POST':
        useremail = request.POST['email']
        userobj = UserProfile.objects.get(user=request.user)
        userobj.email = useremail
        userobj.save()

        userverificationobj = UserVerification.objects.get(userprofile=userobj)

        if userverificationobj.trialAttempts <= 10 and not userverificationobj.isBlocked:
            pin = ''.join(random.choice('1234567890qwertyuiop') for i in range(6))
            userverificationobj.emailCodeSent = pin
            userverificationobj.save()
            try:
                send_email(useremail, "Xeemit Verification Email", "Your Xeemit verification code is: <strong>"+pin+"</strong>", False)
                return HttpResponse('ok')
            except ValueError:
                return HttpResponse('Error sending email! - '+ValueError)
        else:
            return HttpResponse('Trial attempts exceeded allowed amount. Wait until next day.')

    return HttpResponse('Error')

@login_required
@ratelimit(key='user', rate='40/h', block=True)
def partnerregistrationvalidation(request):
    if request.method == 'POST':
        emailcode = request.POST['emailcode']
        phonecode = request.POST['phonecode']
        userobj = UserProfile.objects.get(user=request.user)


        userverificationobj = UserVerification.objects.get(userprofile=userobj)
 
        if userverificationobj.emailCodeSent == emailcode and userverificationobj.pinNumberSent == phonecode:
            userobj.isVerified = True
            userobj.isPayoutPartner = True
            userobj.save()

            country = str(request.POST.get('country', ''))
            street = str(request.POST.get('street', ''))
            area = str(request.POST.get('area', ''))
            lat = Decimal(request.POST.get('lat', 0))
            lng = Decimal(request.POST.get('lng', 0))
            bank_account = str(request.POST.get('bank_account', ''))

            pp_details_obj, created = PayoutPartnerDetails.objects.get_or_create(userprofile=userobj)
            pp_details_obj.lat = lat
            pp_details_obj.lng = lng
            pp_details_obj.bank_account = bank_account
            pp_details_obj.country = country
            pp_details_obj.street = street
            pp_details_obj.area = area
            pp_details_obj.save()

            return HttpResponse('Ok')
    else:
        return HttpResponse('Account is Blocked. Wait until next day.')
    return HttpResponse('Error')

@login_required
def cashpaymentconversion(request):
    if request.method == 'POST':
        pickup_curr = CurrencyData.objects.get(currency_code=(request.POST.get('pickup_currency', ''))).currency_rate
        deliv_curr = CurrencyData.objects.get(currency_code=str(request.POST.get('currency', ''))).currency_rate
        print pickup_curr
        print deliv_curr
        if 'pickup_amount' in request.POST and request.POST['pickup_amount']:
            pickup_amount = Decimal(request.POST['pickup_amount'])
            conversion_amount = pickup_amount*Decimal(100.0/PROFIT_PERCENT)
            conversion_amount = conversion_amount/pickup_curr*deliv_curr
            print conversion_amount
            return HttpResponse('{0:.2f}'.format(conversion_amount))
        elif 'amount' in request.POST and request.POST['amount']:
            amount = Decimal(request.POST['amount'])
            conversion_amount = amount*Decimal(PROFIT_PERCENT/100.0)
            conversion_amount = conversion_amount/deliv_curr*pickup_curr
            return HttpResponse('{0:.2f}'.format(conversion_amount))
        else:
            return HttpResponse('0.00');
    return HttpResponse('0')

@login_required
def chatsystem(request):
    requestUser = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        requestID = int(request.POST.get('requestID', 0))
        RequestObj = Request.objects.get(requestID=requestID)

        if 'LOAD' in request.POST:
            if RequestObj.requestUser == requestUser:
                ReqChatJson = []
                try:
                    ReqChat = RequestChat.objects.filter(request=RequestObj)
                    for msg in ReqChat:
                        obj = {}
                        obj['FromUser'] = msg.fromUser.user.username
                        obj['ToUser'] = msg.toUser.user.username
                        obj['message'] = msg.message
                        obj['status'] = msg.statusRead
                        obj['date'] = msg.dateCreated.strftime('%Y-%m-%d %H:%M:%S')
                        ReqChatJson.append(obj)
                except RequestChat.DoesNotExist:
                    ReqChat = []

                try:
                    ReqAssd = RequestAssigned.objects.get(requestID=RequestObj)
                    obj = {}
                    obj['FromUser'] = ReqAssd.PayoutPartner.user.username
                    obj['isPayoutPartner'] = True
                    ReqChatJson.append(obj)
                except RequestAssigned.DoesNotExist:
                    ReqAssd = []

                chatppl = list(set([x['FromUser'] for x in ReqChatJson]))
                try:
                    chatppl.remove(str(request.user))
                except ValueError:
                    pass
                ReqChatJson.append({'chatppl': chatppl, 'RequestID': requestID})

                pprint("owner")
                pprint(ReqChatJson)
            else:
                pprint("not owner")
                ReqChatJson = []
                try:
                    ReqChat = RequestChat.objects.filter(request=RequestObj).filter(toUser=requestUser)
                    for msg in ReqChat:
                        obj = {}
                        obj['FromUser'] = msg.fromUser.user.username
                        obj['ToUser'] = msg.toUser.user.username
                        obj['message'] = msg.message
                        obj['status'] = msg.statusRead
                        obj['date'] = msg.dateCreated.strftime('%Y-%m-%d %H:%M:%S')
                        ReqChatJson.append(obj)
                except RequestChat.DoesNotExist:
                    ReqChat = []
                try:
                    ReqChat = RequestChat.objects.filter(request=RequestObj).filter(fromUser=requestUser)
                    for msg in ReqChat:
                        obj = {}
                        obj['FromUser'] = msg.fromUser.user.username
                        obj['ToUser'] = msg.toUser.user.username
                        obj['message'] = msg.message
                        obj['status'] = msg.statusRead
                        obj['date'] = msg.dateCreated.strftime('%Y-%m-%d %H:%M:%S')
                        ReqChatJson.append(obj)
                except RequestChat.DoesNotExist:
                    ReqChat = []

                if not ReqChatJson:
                    obj = {}
                    obj['FromUser'] = RequestObj.requestUser.user.username
                    ReqChatJson.append(obj)

                chatppl = list(set([x['FromUser'] for x in ReqChatJson]))
                try:
                    chatppl.remove(str(request.user))
                except ValueError:
                    pass
                ReqChatJson.append({'chatppl': chatppl, 'RequestID': requestID})

            Assignees = RequestAssigned.objects.filter(requestID=RequestObj).values_list('PayoutPartner', flat=True)
            key = ['']
            if requestUser.id in Assignees or requestUser == RequestObj.requestUser:
                ChatKey.objects.all()
                key = ChatKey.objects.filter(request=RequestObj).values_list('key', flat=True)
            ReqChatJson.append({'key': key[0]})

            return JsonResponse(ReqChatJson, safe=False)

        elif 'SEND' in request.POST:
            message = request.POST['message']
            toUser = ''
            if re.search('\w+', message):
                if RequestObj.requestUser == requestUser:
                    toUser = request.POST['toUser']
                    userobj = User.objects.get(username=toUser)
                    toUser = UserProfile.objects.get(user=userobj)
                else:
                    toUser = RequestObj.requestUser
                RequestChat.objects.create(request=RequestObj, fromUser=requestUser, toUser=toUser, message=message,
                                           statusRead=False)
                return HttpResponse('OK')

    return None


def logout(request):
    auth_logout(request)
    return redirect('/')

@login_required
@ratelimit(key='user', rate='40/h', block=True)
def delivery(request):
    requestUser = UserProfile.objects.get(user=request.user)
    requestID = int(request.POST.get('requestID', 0))

    RequestObj = Request.objects.get(requestID=requestID)
    Req_info = RequestAssigned.objects.get(requestID=RequestObj)

    code = str(request.POST.get('code', 0))

    if code==RequestObj.code:
        RequestObj.status = 'Delivered|Completed'
        RequestObj.save()

        paymentdue = workday(datetime.datetime.today().date(), 14, [])  # holidays not taken into account yet

        Transfers.objects.create(assignedTo=Req_info.PayoutPartner, amount=RequestObj.amount, due=paymentdue)

        return HttpResponse('OK')
    else:
        return HttpResponseBadRequest('Wrong Code')

    #add amount to Transfers