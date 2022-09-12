from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_view
from coreapp import views, apis

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('restaurant/sign_in', auth_view.LoginView.as_view(template_name='restaurant/sign_in.html'), name='restaurant_sign_in'),
    path('restaurant/sign_out', auth_view.LogoutView.as_view(next_page='/'), name='restaurant_sign_out'),
    path('restaurant/sign_up', views.restaurant_sign_up, name='restaurant_sign_up'),
    path('restaurant/', views.restaurant_home, name='restaurant_home'),

    path('restaurant/account', views.restaurant_account, name='restaurant_account'),
    path('restaurant/meal', views.restaurant_meal, name='restaurant_meal'),
    path('restaurant/meal/add', views.restaurant_add_meal, name='restaurant_add_meal'),
    path('restaurant/meal/edit/<int:meal_id>', views.restaurant_edit_meal, name='restaurant_edit_meal'),
    path('restaurant/order', views.restaurant_order, name='restaurant_order'),
    path('restaurant/report', views.restaurant_report, name='restaurant_report'),

    path('api/customer/restaurants', apis.customer_get_restaurans),
    path('api/customer/meals/<int:restaurant_id>', apis.customer_get_meals),
    path('api/customer/order/add', apis.customer_add_order),
    path('api/customer/order/latest', apis.customer_get_latest_order),
    path('api/customer/order/latest_status', apis.customer_get_latest_order_status),
    path('api/customer/driver/location', apis.customer_get_driver_location),
    path('api/customer/payment_intent', apis.create_payment_intent),

    path('api/driver/order/ready', apis.driver_get_ready_orders),
    path('api/driver/order/pick', apis.driver_pick_order),
    path('api/driver/order/latest', apis.driver_get_latest_order),
    path('api/driver/order/complete', apis.driver_complete_order),
    path('api/driver/revenue', apis.driver_get_revenue),
    path('api/driver/location/update', apis.driver_update_location),
    path('api/driver/profile', apis.driver_get_profile),
    path('api/driver/profile/update', apis.driver_update_profile),

    path('api/restaurant/order/notification/<last_request_time>', apis.restaurant_order_notification),
]
