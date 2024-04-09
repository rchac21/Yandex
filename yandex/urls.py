from django.urls import path
from yandex import views


urlpatterns = [
    path('', views.login, name = 'login'),
    path('registration/<str:status>/', views.registration, name = 'registration'),
    path('delete/', views.delete, name = 'delete'),
    path('registrationtype/', views.registration_type, name = 'registrationtype'),
    path('process_for_users/<int:personal_id>/', views.process_for_users, name = 'process_for_users'),
    path('choose_service_type/<int:personal_id>/', views.choose_service_type, name = 'choose_service_type'),
    path('message_text/<int:personal_id>', views.message_text, name = 'message_text'),
    path('show_driver_data/<int:personal_id>/', views.show_driver_data, name = 'show_driver_data'),
    path('work/<int:personal_id>/', views.work, name = 'work'),
    path('show_client_data/<int:personal_id>/', views.show_client_data, name = 'show_client_data'),
    path('add_as_taxi_driver/<int:personal_id>/', views.add_as_taxi_driver, name = 'add_as_taxi_driver'),
    path('choose_payment_method/<int:personal_id>/<str:service_type>/', views.choose_payment_method, name = 'choose_payment_method'),
    path('insufficient_balance_message/<int:personal_id>/<str:service_type>/', views.insufficient_balance_message, name = 'insufficient_balance_message'),
    path('add_user_account_table/<int:personal_id>/<str:service_type>/', views.add_user_account_table, name = 'add_user_account_table'),
    path('process_for_orderers/<int:personal_id>/', views.process_for_orderers, name = 'process_for_orderers'),
    path('add_or_change_account_number/<int:personal_id>/', views.add_or_change_account_number, name = 'add_or_change_account_number'),
    path('delete_account_num/<int:personal_id>/', views.delete_account_num, name = 'delete_account_num'),
]

