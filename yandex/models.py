from django.db import models

# Create your models here.
class Orderer(models.Model):
     name = models.CharField(max_length=100)
     personal_id = models.IntegerField(primary_key=True)
     phone_num = models.IntegerField()

     def __str__(self):
        return self.name
     

class Taxi_Driver(models.Model):
     name = models.CharField(max_length=100)
     personal_id = models.IntegerField(primary_key=True)
     phone_num = models.IntegerField()
     car_series = models.CharField(max_length=100)
     car_num = models.CharField(max_length=100)
     car_color = models.CharField(max_length=100)
     CHOICES = [
        ('Economy', 'Economy'),
        ('Comfort', 'Comfort'),
        ('Business', 'Business'),
     ]
    
     service_type = models.CharField(max_length=10, choices=CHOICES)
     account_num = models.CharField(max_length=100,null=True)

     def __str__(self):
       return self.name

# If the client has called a taxi, it falls in this table.
class Current_Orderers_Table(models.Model):
     orderer_pers_id = models.IntegerField(primary_key=True)
     service_type = models.CharField(max_length=100)
     distance = models.IntegerField(null=True)
     amount = models.IntegerField(null=True)

     
# If the driver works then it falls into this table.
class Current_Taxi_Drivers_Table(models.Model):
     taxi_driver_pers_id = models.IntegerField(primary_key=True)
     service_type = models.CharField(max_length=100)

     
# This table matches the customer, taxi driver and Including the distance between,
# that is, each driver corresponds to the customer and the distance Up to this
# client, that is, each driver will match all clients that Current_Orderers_Table
# is in this table.     
class Compliance_Table(models.Model):
     taxi_driver_pers_id = models.IntegerField()
     orderer_pers_id = models.IntegerField()
     distance = models.IntegerField(null=True) # This is the distance from the taxi driver to the customer.
     distance2 = models.IntegerField(null=True) # It is the client that specifies the distance between the locations.
     distance_time = models.IntegerField(null=True) # This is the time from the taxi driver to the customer.
     distance_time2 = models.IntegerField(null=True) # This is the time in which the client will arrive at the destination.
     amount = models.IntegerField(null=True) 

     
# If the taxi driver took the order, then this table will include: taxi driver,
# Customer whose order was picked up and the distance between them.
class Received_Call_Table(models.Model):
     taxi_driver_pers_id = models.IntegerField()
     orderer_pers_id = models.IntegerField(primary_key=True)
     distance = models.IntegerField(null=True)
     distance2 = models.IntegerField(null=True) # It is the client that specifies the distance between the locations.
     distance_time = models.IntegerField(null=True) # This is the time from the taxi driver to the customer.
     distance_time2 = models.IntegerField(null=True) # This is the time in which the client will arrive at the destination.
     amount = models.IntegerField(null=True)


# According to this table, I know whether the client has seen the driver data or not.
class Show_Data_Table(models.Model):
     orderer_pers_id = models.IntegerField(primary_key=True)
     show = models.BooleanField(default=False)

# In this table, the distance for the potential client is generated,
# Where to go and the amount according to the services provided.
class Potential_Current_Orderer(models.Model):
     personal_id = models.IntegerField(primary_key=True)
     distance = models.IntegerField(null=True) # It is the client that specifies the distance between the locations.
     comfort = models.IntegerField(null=True) # This is the amount that the client will pay if he travels with this service.
     economy = models.IntegerField(null=True) # This is the amount that the client will pay if he travels with this service.
     business = models.IntegerField(null=True) # This is the amount that the client will pay if he travels with this service.

# User's personal ID, account number, account amount are logged in this table
# When calling a taxi, I will ask whether he will pay in cash or by card and if he has chosen a card
# I will enter the card account number and log it in this table, and I will deduct the amount during payment.
class Users_Accounts(models.Model):
     personal_id = models.IntegerField(primary_key=True)
     account = models.CharField(max_length=100)
     amount = models.IntegerField(null=True)