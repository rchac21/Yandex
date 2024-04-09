from django.contrib import admin
from .models import Orderer,Taxi_Driver,Current_Taxi_Drivers_Table,Current_Orderers_Table,Compliance_Table,Received_Call_Table,Show_Data_Table
# Register your models here.




admin.site.register(Orderer)
admin.site.register(Taxi_Driver)
admin.site.register(Current_Taxi_Drivers_Table)
admin.site.register(Current_Orderers_Table)
admin.site.register(Compliance_Table)
admin.site.register(Received_Call_Table)
admin.site.register(Show_Data_Table)