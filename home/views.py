from datetime import datetime

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from .models import Institute, Registration, Status, Contact
from .paytm import Checksum


def index(request):
    return render(request, 'index.html')

@csrf_exempt
def search(request):
    if request.method == "POST":
        keyword = request.POST['keyword']
        if keyword == "":
            return render(request, 'search.html', {'length': 0})
        institutes = Institute.objects.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword) |
                                              Q(city__icontains=keyword) | Q(address__icontains=keyword) |
                                              Q(mobile__icontains=keyword) | Q(map__icontains=keyword) |
                                              Q(category__icontains=keyword))
        return render(request, 'search.html', {'institutes': institutes, 'length': len(institutes)})
    institutes = Institute.objects.all()
    return render(request, 'search.html', {'institutes': institutes, 'length': len(institutes)})

def institute(request, name):
    institute = Institute.objects.get(name=name)
    return render(request, 'institute.html', {'institute': institute})


def register(request, name):
    institute = Institute.objects.get(name=name)
    return render(request, 'register.html', {'institute': institute})

@csrf_exempt
def checkout(request, name):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        mobile = request.POST['mobile']
        email = request.POST['email']
        city = request.POST['city']
        state = request.POST['state']
        zip = request.POST['zip']
        coupon = request.POST['coupon']
        institute = Institute.objects.get(name=name)
        fees = float(institute.fees)
        if fees == 0:
            now = datetime.now()
            registration_id = str(now.year) + str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(
                now.second)
            registration = Registration(first_name=first_name, last_name=last_name, email=email, mobile=mobile,
                                        city=city, state=state, zip=zip, institute=institute,
                                        fees=str(fees), registration_id=registration_id)
            registration.save()
            status = Status(registration_status="Zero Fee Succcessfull", user=registration)
            status.save()
            response = {'RESPCODE': '01', 'ORDERID': registration_id, "TXNAMOUNT": "0", "TXNID": "N/A", "TXNDATE":
                datetime.today(), "STATUS": "Successfull", "RESPMSG": "N/A"}
            return render(request, 'paymentstatus.html',
                          {'registration': registration, "response": response})
        else:
            if coupon == "DISC10":
                fees = fees - fees / 10
            elif coupon == "ONLINE5":
                fees = fees - fees * 5 / 100
        fees = str(fees)
        now = datetime.now()
        registration_id = str(now.year) + str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(
            now.second)
        registration = Registration(first_name=first_name, last_name=last_name, email=email, mobile=mobile,
                                    city=city, state=state, zip=zip, institute=institute,
                                    fees=str(fees), registration_id=registration_id)
        registration.save()
        status = Status(registration_status="Awaiting Payment", user=registration)
        status.save()

        param_dict = {

            'MID': 'glNfxl71290944876196',
            'ORDER_ID': str(registration.registration_id),
            'TXN_AMOUNT': str(fees),
            'CUST_ID': email,
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL': 'http://127.0.0.1:8000/payment',

        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, 'SF&LjNr51tyW0fHD')
        return render(request, 'paytm.html', {'param_dict': param_dict})

    return render(request, 'register.html')


@csrf_exempt
def handlerequest(request):
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    registration = Registration.objects.get(registration_id=response_dict['ORDERID'])
    status = Status.objects.get(user=registration)

    verify = Checksum.verify_checksum(response_dict, "SF&LjNr51tyW0fHD", checksum)
    if verify:
        registration.txn_id = str(response_dict['TXNID'])
        registration.txn_date = str(response_dict['TXNDATE'])
        registration.txn_amount = str(response_dict['TXNAMOUNT'])
        registration.txn_status = str(response_dict['STATUS'])
        registration.txn_msg = str(response_dict['RESPMSG'])
        registration.save()
        filename = "media/reciepts/" + response_dict['ORDERID'] + '.txt'
        file1 = open(filename, 'w')
        content = "Order ID : " + str(response_dict['ORDERID']) + "\n" + "Name : " + str(
            registration.first_name) + " " + str(registration.last_name) + "\n" + "Institute : " + str(
            registration.institute.name) + "\n" + "TXNID : " + str(
            response_dict['TXNID']) + "\n" + "TXNAMOUNT : Rs. " + str(
            response_dict['TXNAMOUNT']) + "\n" + "TXNDATE : " + str(
            response_dict['TXNDATE']) + "\n" + "Status : " + str(
            response_dict['STATUS']) + "\n" + "Response Message : " + str(response_dict['RESPMSG']) + "\n"
        file1.write(content)
        file1.close()
        if response_dict['RESPCODE'] == '01':
            status.registration_status = "Payment Successfull"
            status.save()
        else:
            status.registration_status = "Payment Failed"
            status.save()
        return render(request, 'paymentstatus.html',
                      {'response': response_dict, 'reciept': filename, 'registration': registration})
    return render(request, 'index.html')


def filter(request, keyword):
    institutes = Institute.objects.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword) |
                                          Q(city__icontains=keyword) | Q(address__icontains=keyword) |
                                          Q(mobile__icontains=keyword) | Q(map__icontains=keyword) |
                                          Q(category__icontains=keyword))
    return render(request, 'search.html', {'institutes': institutes, 'length': len(institutes)})

@csrf_exempt
def filters(request):
    if request.method == "POST":
        nagpur = request.POST.get('nagpur', "off")
        amravati = request.POST.get('amravati', "off")
        arts = request.POST.get('arts', "off")
        science = request.POST.get('science', "off")
        commerce = request.POST.get('commerce', "off")
        others = request.POST.get('others', "off")
        free = request.POST.get('free', "off")
        choices = [nagpur, amravati, arts, science, commerce, others, free]
        if nagpur == "on" and free == "on" and science == "on":
            institutes = Institute.objects.filter(city="Nagpur", fees="0", category="Science")
        elif nagpur == "on" and free == "on" and arts == "on":
            institutes = Institute.objects.filter(city="Nagpur", fees="0", category="Arts")
        elif nagpur == "on" and free == "on" and commerce == "on":
            institutes = Institute.objects.filter(city="Nagpur", fees="0", category="Commerce")
        elif nagpur == "on" and free == "on" and others == "on":
            institutes = Institute.objects.filter(city="Nagpur", fees="0", category="Others")
        elif nagpur == "on" and free == "off" and science == "on":
            institutes = Institute.objects.filter(city="Nagpur", category="Science")
        elif nagpur == "on" and free == "off" and arts == "on":
            institutes = Institute.objects.filter(city="Nagpur", category="Arts")
        elif nagpur == "on" and free == "off" and commerce == "on":
            institutes = Institute.objects.filter(city="Nagpur", category="Commerce")
        elif nagpur == "on" and free == "off" and others == "on":
            institutes = Institute.objects.filter(city="Nagpur", category="Others")
        elif amravati == "on" and free == "on" and science == "on":
            institutes = Institute.objects.filter(city="Amravati", fees="0", category="Science")
        elif amravati == "on" and free == "on" and arts == "on":
            institutes = Institute.objects.filter(city="Amravati", fees="0", category="Arts")
        elif amravati == "on" and free == "on" and commerce == "on":
            institutes = Institute.objects.filter(city="Amravati", fees="0", category="Commerce")
        elif amravati == "on" and free == "on" and others == "on":
            institutes = Institute.objects.filter(city="Amravati", fees="0", category="Others")
        elif amravati == "on" and free == "off" and science == "on":
            institutes = Institute.objects.filter(city="Amravati", category="Science")
        elif amravati == "on" and free == "off" and arts == "on":
            institutes = Institute.objects.filter(city="Amravati", category="Arts")
        elif amravati == "on" and free == "off" and commerce == "on":
            institutes = Institute.objects.filter(city="Amravati", category="Commerce")
        elif amravati == "on" and free == "off" and others == "on":
            institutes = Institute.objects.filter(city="Amravati", category="Others")
        elif amravati == "on" and nagpur == "on":
            institutes = Institute.objects.filter(Q(address__icontains="Amravati") | Q(address__icontains="Nagpur"))
        elif amravati == "on":
            institutes = Institute.objects.filter(city="Amravati")
        elif nagpur == "on":
            institutes = Institute.objects.filter(city="Nagpur")
        elif free == "on":
            institutes = Institute.objects.filter(fees="0")
        elif arts == "on":
            institutes = Institute.objects.filter(category="Arts")
        elif commerce == "on":
            institutes = Institute.objects.filter(category="Commerce")
        elif science == "on":
            institutes = Institute.objects.filter(category="Science")
        elif others == "on":
            institutes = Institute.objects.filter(category="Others")
        else:
            institutes = Institute.objects.all()

        return render(request, 'search.html', {'institutes': institutes, 'length': len(institutes)})
    institutes = Institute.objects.all()
    return render(request, 'search.html', {'institutes': institutes, 'length': len(institutes)})

@csrf_exempt
def contact(request):
    if request.method =="POST":
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
        new_contact = Contact(name=name, email=email, subject=subject, message=message)
        new_contact.save()
        return render(request, 'contact.html', {'msg': 'Submitted Successfully'})
    return render(request, 'contact.html')
