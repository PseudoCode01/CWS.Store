from django.shortcuts import render
from django.http import HttpResponse
from .models import Product,Contact,Orders,OrderUpdate
from math import ceil
import json
from PayTm import Checksum
from django.views.decorators.csrf import csrf_exempt
MERCHANT_KEY = '0K5Uhk4At%X1t80Q'

# Create your views here.
def index(request):
    allProds=[]
    catprods=Product.objects.values('category','id')
    #print(catprods)
    cats={item['category'] for item in catprods}
    for cat in cats:
        prod=Product.objects.filter(category=cat)
        n=len(prod)
        nslides=ceil(n/4)
       
        allProds.append([prod,range(1,nslides),nslides])
    #allprods=[[products,range(1,nslides),nslides],[products,range(1,nslides),nslides]]
    params={'allprods':allProds}
    print(type(allProds))
    return render(request,'shop/index.html',params)
def searchMatch(query,item):
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False
def search(request):
    query=request.GET.get('search').lower()
    allProds=[]
    catprods=Product.objects.values('category','id')
    #print(catprods)
    cats={item['category'] for item in catprods}
    for cat in cats:
        proditem=Product.objects.filter(category=cat)
        prod=[item for item in proditem if searchMatch(query,item)]
        n=len(prod)
        nslides=ceil(n/4)
        if len(prod)!=0:
            allProds.append([prod,range(1,nslides),nslides])
    #allprods=[[products,range(1,nslides),nslides],[products,range(1,nslides),nslides]]
    params={'allprods':allProds,"msg":""}
    if len(allProds)==0 or len(query)<4:
        params={'msg':"Please make sure to enter relevent search query"}
    
    return render(request,'shop/search.html',params)
def about(request):
    return render(request,'shop/about.html')
def contact(request):
    if request.method=="POST":
        print(request)
        name=request.POST.get('name',' ')
        email=request.POST.get('email',' ')
        phone=request.POST.get('phone',' ')
        desc=request.POST.get('desc',' ')
        contact=Contact(name=name,email=email,phone=phone,desc=desc)
        contact.save()
    return render(request,'shop/contact.html')
def tracker(request):
    if request.method=="POST":
        orderId=request.POST.get('orderId','')
        email=request.POST.get('email','')
        
        try:
            order=Orders.objects.filter(order_id=orderId,email=email)
            if(len(order)>0):
                update=OrderUpdate.objects.filter(order_id=orderId)
                updates=[]
                for item in update:
                    updates.append({'text':item.update_desc,'time':item.timestamp})
                    response=json.dumps({"status":"success","updates":updates,"itemJson":order[0].items_json},default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')
    return render(request,'shop/tracker.html')
def product(request,myid):
    product=Product.objects.filter(id=myid)
    
    return render(request,'shop/prodview.html',{'product':product[0]})


def checkout(request):
    if request.method=="POST":
        items_json=request.POST.get('itemsJson','')
        amount=request.POST.get('amount',' ')
        name=request.POST.get('name',' ')
        email=request.POST.get('email',' ')
        phone=request.POST.get('phone',' ')
        address=request.POST.get('address',' ')+" "+request.POST.get('address2',' ')
        city=request.POST.get('city',' ')
        state=request.POST.get('state',' ')
        zip_code=request.POST.get('zip_code',' ')
        order=Orders(items_json=items_json,name=name,email=email,phone=phone,address=address,city=city,state=state,zip_code=zip_code,amount=amount)
        order.save()
        update=OrderUpdate(order_id=order.order_id,update_desc="The order has been placed")
        update.save()
        id=order.order_id
        thanks=True
        
        param_dict = {

                'MID': 'RLUAjJ34588862174269',
                'ORDER_ID': str(order.order_id),
                'TXN_AMOUNT': str(amount),
                'CUST_ID': email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/',

        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'shop/paytm.html', {'param_dict': param_dict})

    return render(request,'shop/checkout.html')

@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})