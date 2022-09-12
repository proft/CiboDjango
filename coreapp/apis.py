import json
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from coreapp.models import Customer, Driver, OrderDetails, Restaurant, Meal, Order
from coreapp.serializers import OrderDriverSerializer, OrderSerializer, RestaurantSerializer, MealSerializer, OrderStatusSerializer

import stripe
from cibo.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY

# RESTAURANT

def restaurant_order_notification(request, last_request_time):
    notification = Order.objects.filter(restaurant=request.user.restaurant, created_at__gt=last_request_time).count()
    return JsonResponse({'notification': notification})

# CUSTOMER

def customer_get_restaurans(request):
    restaurents = RestaurantSerializer(Restaurant.objects.all().order_by("-id"), many = True).data
    return JsonResponse({'restaurants': restaurents})

def customer_get_meals(request, restaurant_id):
    meals = MealSerializer (
        Meal.objects.filter(restaurant_id=restaurant_id).order_by("-id"),
        many=True
    ).data
    return JsonResponse({'meals': meals})

@csrf_exempt
def customer_add_order(request):
    if request.method == "POST":
        # profile
        customer_id = request.POST.get('cid')
        try:
            customer = Customer.objects.get(user__id=customer_id)
        except Customer.DoesNotExist:
          return JsonResponse({'status': 'failed', 'error': 'Customer dosn\'t exist.'})
        
        # outstanding order
        if Order.objects.filter(customer=customer).exclude(status=Order.DELIVERED): 
            return JsonResponse({'status': 'failed', 'error': 'Your last order must be completed.'})
        
        # address
        if not request.POST['address']:
            return JsonResponse({'status': 'failed', 'error': 'a'})
        
        # details
        order_details = json.loads(request.POST['order_details'])
        
        # total
        order_total = 0
        for meal in order_details:
            if not Meal.objects.filter(id=meal['meal_id'], restaurant_id=request.POST['restaurant_id']):
                return JsonResponse({'status': 'failed', 'error': 'Meals must be in only one restaurant.'})
            else:
                order_total += Meal.objects.get(id=meal['meal_id']).price * meal['quantity']

        # create order
        if len(order_details) > 0:
            order = Order.objects.create(
                customer=customer,
                restaurant_id = request.POST['restaurant_id'],
                total = order_total,
                status = Order.COOKING,
                address = request.POST['address'])

            for meal in order_details:
                OrderDetails.objects.create(
                    order=order,
                    meal_id = meal['meal_id'],
                    quantity = meal['quantity'],
                    sub_total = Meal.objects.get(id=meal['meal_id']).price * meal['quantity']
                )
            return JsonResponse({'status': 'success'})


    return JsonResponse({})

def customer_get_latest_order(request):
    # profile
    customer_id = request.GET.get('cid')
    try:
        customer = Customer.objects.get(user__id=customer_id)
    except Customer.DoesNotExist:
        return JsonResponse({'status': 'failed', 'error': 'Customer dosn\'t exist.'})

    order = OrderSerializer(
        Order.objects.filter(customer=customer).last()
    ).data

    return JsonResponse({
        'last_order': order
    })

def customer_get_latest_order_status(request):
    # profile
    customer_id = request.GET.get('cid')
    try:
        customer = Customer.objects.get(user__id=customer_id)
    except Customer.DoesNotExist:
        return JsonResponse({'status': 'failed', 'error': 'Customer dosn\'t exist.'})

    order_status = OrderStatusSerializer(
        Order.objects.filter(customer=customer).last()
    ).data

    return JsonResponse({
        'last_order_status': order_status
    })

def customer_get_driver_location(request):
    customer_id = request.GET.get('cid')
    try:
        customer = Customer.objects.get(user__id=customer_id)
    except Customer.DoesNotExist:
        return JsonResponse({'status': 'failed', 'error': 'Customer dosn\'t exist.'})

    order = Order.objects.filter(customer=customer, status=Order.ONTHEWAY).last()
    if order:
        location = order.driver.location
    else:
        location = None

    return JsonResponse({"location": location})

def create_payment_intent(request):
    customer_id = request.POST.get('cid')
    try:
        customer = Customer.objects.get(user__id=customer_id)
    except Customer.DoesNotExist:
        return JsonResponse({'status': 'failed', 'error': 'Customer dosn\'t exist.'})

    total = request.POST["total"]

    if request.method == "POST":
        try:
            intent = stripe.PaymentIntent.create(
                amount = int(total) * 100, # cents
                currency = "usd",
                description = "FoodTasker Order"
            )

            if intent:
                client_secret = intent.client_secret
                return JsonResponse({"client_secret": client_secret})

        except stripe.error.StripeError as e:
            return JsonResponse({'status': 'failed', 'error': str(e)})

        except Exception as e:
            return JsonResponse({'status': 'failed', 'error': str(e)})

    return JsonResponse({'status': 'failed', 'error': "Failed to create Payment Intent"})

# DRIVER

def driver_get_ready_orders(request):
    orders = OrderSerializer(
        Order.objects.filter(status=Order.READY, driver=None).order_by('-id'),
        many=True
    ).data

    return JsonResponse({
        'orders': orders
    })

@csrf_exempt
def driver_pick_order(request):
    if request.method == 'POST':
        driver_id = request.POST.get('did')
        try:
            driver = Driver.objects.get(user__id=driver_id)
        except Driver.DoesNotExist:
            return JsonResponse({'status': 'failed', 'error': 'Driver dosn\'t exist.'})
        
        if Order.objects.filter(driver=driver, status=Order.ONTHEWAY):
            return JsonResponse({'status': 'failed', 'error': 'Your outstanding order is not delivered yet.'})
        
        try: 
            order = Order.objects.get(
                id=request.POST['order_id'],
                driver=None,
                status=Order.READY)

            order.driver = driver
            order.status = Order.ONTHEWAY
            order.picked_at = timezone.now()
            order.save()

            return JsonResponse({
                'status': 'success'
            })

        except Order.DoesNotExist:
            return JsonResponse({
                'status': 'failed',
                'error': 'This order has been picked up by another'
            })

def driver_get_latest_order(request):
    driver_id = request.POST.get('did')
    try:
        driver = Driver.objects.get(user__id=driver_id)
    except Driver.DoesNotExist:
        return JsonResponse({'status': 'failed', 'error': 'Driver dosn\'t exist.'})
    
    order = OrderSerializer(
        Order.objects.filter(driver=driver, status=Order.ONTHEWAY).last()
    ).data

    return JsonResponse({'order': order})

@csrf_exempt
def driver_complete_order(request):
    if request.method == "POST":
        driver_id = request.POST.get('did')
        try:
            driver = Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            return JsonResponse({'status': 'failed', 'error': 'Driver dosn\'t exist.'})
        
        order = Order.objects.id(id=request.POST["order_id"], driver=driver)
        order.status = Order.DELIVERED
        order.save()

    return JsonResponse({"status": "success"})

def driver_get_revenue(request):
    driver_id = request.GET.get('did')
    try:
        driver = Driver.objects.get(id=driver_id)
    except Driver.DoesNotExist:
        return JsonResponse({'status': 'failed', 'error': 'Driver dosn\'t exist.'})
    
    from datetime import timedelta

    revenue = {}
    today = timezone.now()
    current_weekdays = [today + timedelta(days=i) for i in range(0 - today.weekday(), 7 - today.weekday())]

    for day in current_weekdays:
        orders = Order.objects.filter(
            driver=driver, 
            status=Order.DELIVERED, 
            created_at__year=day.year,
            created_at__month=day.month,
            created_at__day=day.day)

        revenue[day.strftime("%a")] = sum(order.total for order in orders)

    return JsonResponse({"revenue": revenue})                

@csrf_exempt
def driver_update_location(request):
    if request.method == "POST":
        driver_id = request.POST.get('did')
        try:
            driver = Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            return JsonResponse({'status': 'failed', 'error': 'Driver dosn\'t exist.'})
        
        driver.location = request.POST["location"]
        driver.save()
        
        return JsonResponse({"status": "success"})    

def driver_get_profile(request):
    driver_id = request.GET.get('did')
    try:
        driver = Driver.objects.get(id=driver_id)
    except Driver.DoesNotExist:
        return JsonResponse({'status': 'failed', 'error': 'Driver dosn\'t exist.'})

    data = OrderDriverSerializer(driver).data

    return JsonResponse({"driver": data})

@csrf_exempt
def driver_update_profile(request):
    if request.method == "POST":
        driver_id = request.POST.get('did')
        try:
            driver = Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            return JsonResponse({'status': 'failed', 'error': 'Driver dosn\'t exist.'})
        
        driver.car_model = request.POST["car_model"]
        driver.plate_number = request.POST["plate_number"]
        driver.save()
        
        return JsonResponse({"status": "success"})    
