from django import forms
from .models import Orderer, Taxi_Driver


class LoginForm(forms.Form):
    personal_id = forms.IntegerField(label="Login")


class RegistrationOrdererForm(forms.ModelForm):
    class Meta:
        model = Orderer
        fields = ['name', 'personal_id', 'phone_num']


class RegistrationTaxiDriverForm(forms.ModelForm):
    class Meta:
        model = Taxi_Driver
        fields = ['name', 'personal_id', 'phone_num', 'car_series', 'car_num', 'car_color', 'account_num', 'service_type']
    

class DeleteForm(forms.Form):
     personal_id = forms.IntegerField(label="Delete")

# This is the form when the orderer is added as a taxi driver
# and the account number has been added.
class Add_As_Taxi_Driver_Form(forms.Form):
     car_series = forms.CharField(label="Car Series:",max_length=100)
     car_num = forms.CharField(label="Car Num:",max_length=100)
     car_color = forms.CharField(label="Car Color:",max_length=100)
     CHOICES = [
        ('Economy', 'Economy'),
        ('Comfort', 'Comfort'),
        ('Business', 'Business'),
     ]
     service_type = forms.ChoiceField(choices=CHOICES)

# This is the form when the orderer is added as a taxi driver
# and account number has not been added.
class Add_As_Taxi_Driver_Form2(forms.Form):
     car_series = forms.CharField(label="Car Series:",max_length=100)
     car_num = forms.CharField(label="Car Num:",max_length=100)
     car_color = forms.CharField(label="Car Color:",max_length=100)
     account_num = forms.CharField(label="account number:",max_length=100)
     CHOICES = [
        ('Economy', 'Economy'),
        ('Comfort', 'Comfort'),
        ('Business', 'Business'),
     ]
     service_type = forms.ChoiceField(choices=CHOICES)

    
class User_Account_Form(forms.Form):
    account_num = forms.CharField(label="account number:",max_length=100)

class Reference_Locations_Form(forms.Form):
    start_point = forms.CharField(label="start point:",max_length=200)
    end_point = forms.CharField(label="end point:",max_length=100)