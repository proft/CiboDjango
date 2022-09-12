from rest_framework import serializers
from coreapp.models import Customer, Restaurant, Meal, Driver, Order, OrderDetails

class RestaurantSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()

    def get_logo(self, restaurant):
        return "https://www.django-rest-framework.org/img/logo.png"


    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'phone', 'address', 'logo')

class MealSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, restaurant):
        return "https://usapple.org/wp-content/uploads/2019/10/apple-pink-lady.png"

    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'short_description', 'image', 'price')        

# ORDER

class OrderCustomerSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='user.get_full_name')

    class Meta:
        model = Customer
        fields = ('id', 'name', 'avatar', 'address')   

class OrderDriverSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='user.get_full_name')

    class Meta:
        model = Driver
        fields = ('id', 'name', 'avatar', 'car_model', 'plate_number')            

class OrderRestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'phone', 'address')                    

class OrderMealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ('id', 'name', 'price')        

class OrderDetailsSerializer(serializers.ModelSerializer):
    meal = OrderMealSerializer()

    class Meta:
        model = OrderDetails
        fields = ('id', 'meal', 'quantity', 'sub_total')                

class OrderSerializer(serializers.ModelSerializer):
    customer = OrderCustomerSerializer()
    driver = OrderDriverSerializer()
    restaurant = OrderRestaurantSerializer()
    order_details = OrderDetailsSerializer(many=True)
    status = serializers.ReadOnlyField(source='get_status_name')

    class Meta:
        model = Order
        fields = ('id', 'customer', 'restaurant', 'driver', 'order_details', 'total', 'status', 'address')                        

class OrderStatusSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField(source='get_status_display')

    class Meta:
        model = Order
        fields = ('id', 'status')