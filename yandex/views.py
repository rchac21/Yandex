from django.shortcuts import render, redirect
from .models import Orderer, Taxi_Driver,Current_Taxi_Drivers_Table,Current_Orderers_Table,Compliance_Table,Received_Call_Table,Show_Data_Table,Potential_Current_Orderer,Users_Accounts
from .forms import Reference_Locations_Form, RegistrationOrdererForm, RegistrationTaxiDriverForm, LoginForm, DeleteForm, Add_As_Taxi_Driver_Form, User_Account_Form, Add_As_Taxi_Driver_Form2
import random


# Allows the user to register as a customer who
# You can only call a taxi if you register as a taxi driver
# which will be able to both work and call.
def registration_type(request):
   return render(request,'yandex/registrationtype.html')

# Registration process.
def registration(request,status):
    if request.method == "POST":
        form = ''
        personal_ids = list(Orderer.objects.values_list('personal_id', flat=True))
        phone_nums = list(Orderer.objects.values_list('phone_num', flat=True))
        if status == 'orderer':
           form = RegistrationOrdererForm(request.POST)
        else:
           form = RegistrationTaxiDriverForm(request.POST)  

        personal_id = request.POST.get('personal_id')
        phone_num = int(request.POST.get('phone_num'))

        if form.is_valid() and phone_num not in phone_nums:
            form.save()
            obj = Show_Data_Table(
                orderer_pers_id = int(personal_id),
                show = False,
                )
            obj.save()
            if status != 'orderer':
                obj = Orderer(
                name = form.cleaned_data["name"],
                personal_id = int(personal_id),
                phone_num = int(form.cleaned_data["phone_num"]),
                )
                obj.save()
                obj2 = Users_Accounts(
                personal_id = int(personal_id),
                account = form.cleaned_data["account_num"],
                amount = random.randint(50,100),
                )
                obj2.save()
            return redirect('login')
        else:
            text = ''
            if (int(personal_id) in personal_ids) and (phone_num in phone_nums):
               text = 'A user with such a personal ID and phone number already exists'
            elif (int(personal_id) not in personal_ids) and (phone_num in phone_nums):
                text = 'A user with such a phone number already exists'
            elif (int(personal_id) in personal_ids) and (phone_num not in phone_nums):
                text = 'A user with such a personal ID already exists'
            else:
                text = "form isn't valid"
            return render(request, 'yandex/error_message.html',{'text': text})    
    else:
        if status == 'orderer':
           form = RegistrationOrdererForm()
        else:
           form = RegistrationTaxiDriverForm()   
        return render(request,"yandex/registration.html",{
            "form": form,
        })

# Login process.
def login(request):
    if request.method == "POST":  
        orderer_pers_ids = list(Orderer.objects.values_list('personal_id', flat=True))
        taxi_Driver_pers_ids = list(Taxi_Driver.objects.values_list('personal_id', flat=True))
        personal_id = request.POST.get('personal_id')
        if int(personal_id) in taxi_Driver_pers_ids:          
           return redirect('process_for_users',personal_id=int(personal_id))      
        elif int(personal_id) in orderer_pers_ids:            
            return redirect('process_for_orderers', personal_id=int(personal_id))        
        else:
            text = 'There is no user on this personal ID'
            return render(request, 'yandex/error_message.html',{'text': text})        
    return render(request,'yandex/login.html',{'form': LoginForm()})

# Deletes the user account, that is, it is deleted from all tables.
def delete(request):
    if request.method == 'POST':
        orderer_pers_ids = list(Orderer.objects.values_list('personal_id', flat=True))
        taxi_Driver_pers_ids = list(Taxi_Driver.objects.values_list('personal_id', flat=True))
        personal_id = request.POST.get('personal_id')
        if int(personal_id) in taxi_Driver_pers_ids:
           Delete_User_From_Every_Tables(int(personal_id))
           return redirect('login')
        elif int(personal_id) in orderer_pers_ids:
            Delete_Orderer_From_Every_Tables(int(personal_id))
            return redirect('login')
        else:
            text = 'There is no user on this personal ID'
            return render(request, 'yandex/error_message.html',{'text': text}) 
              
    return render(request, 'yandex/delete.html', {'form' : DeleteForm()})

# A process for a user that can work as
# Also calling him a taxi driver.
def process_for_users(request,personal_id):
   if request.method == 'POST':
       Delete_Taxi_Driver_From_Every_Tables(personal_id)
       text = 'successfully cancelled'
       return render(request, 'yandex/message_text2.html',{
           'text': text,
           'personal_id': personal_id,
           'check': False,
           })
   if User_Is_Only_Orderer(personal_id):
       return redirect('process_for_orderers', personal_id=personal_id)
   if taxi_driver_recieve_call(personal_id):
      if Show_Data_Table.objects.get(orderer_pers_id=personal_id).show == True:
          obj = Show_Data_Table.objects.get(orderer_pers_id=personal_id)
          obj.show = False
          obj.save()
          Delete_Orderer_from_Rec_Call_Tab(personal_id)
      else:
          return redirect('show_driver_data', personal_id=personal_id)
   if User_Is_Current_As_Taxi_Driver(personal_id):
       return redirect('work',personal_id=personal_id)
   if User_Is_Current_As_Orderer(personal_id):
       return redirect('process_for_orderers', personal_id=personal_id)
   return render(request, 'yandex/process_for_users.html', {'personal_id' : personal_id})

# Process for a user who can only call a taxi.
def process_for_orderers(request,personal_id):
   if taxi_driver_recieve_call(personal_id):
      if Show_Data_Table.objects.get(orderer_pers_id=personal_id).show == True:
          obj = Show_Data_Table.objects.get(orderer_pers_id=personal_id)
          obj.show = False
          obj.save()
          Delete_Orderer_from_Rec_Call_Tab(personal_id)
      else:
          return redirect('show_driver_data', personal_id=personal_id) 

   if not is_call_taxi(personal_id):
      if request.method == 'POST':
         form = Reference_Locations_Form(request.POST)
         if form.is_valid():
            Insert_In_Potential_Current_Orderer(personal_id)
            return redirect('choose_service_type', personal_id=personal_id)
      check = True
      if User_Is_Only_Orderer(personal_id):
          check = False
      check2 = USer_Has_Account(personal_id)
      return render(request, 'yandex/process_for_orderers.html',{
         'form': Reference_Locations_Form(),
         'personal_id': personal_id,
         'check': check,
         'check2': check2,
         })
   else:
        return redirect('message_text', personal_id=personal_id)

# I offer the user two options of payment method to pay in cash
# or pay by card.
def choose_payment_method(request,personal_id,service_type):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        if payment_method == 'card':
           if USer_Has_Account(personal_id):
              balance = Users_Accounts.objects.get(personal_id=personal_id).amount
              travel_fee = Get_Amount_From_Potential_Current_Orderers_Table(personal_id,service_type)
              if balance >= travel_fee:
                  new_process(personal_id,service_type)
                  return redirect('message_text', personal_id=personal_id)
              else:
                  return redirect('insufficient_balance_message', personal_id=personal_id,service_type=service_type)
           else:
               return redirect('add_user_account_table', personal_id=personal_id,service_type=service_type)
        else:
            new_process(personal_id,service_type)
            return redirect('message_text', personal_id=personal_id)
    return render(request, 'yandex/choose_payment_method.html')

# If the client has an insufficient amount on the card, then a corresponding 
# message is displayed And I offer to pay in cash.
def insufficient_balance_message(request,personal_id,service_type):
    if request.method == 'POST':
       new_process(personal_id,service_type)
       return redirect('message_text', personal_id=personal_id)
    check = User_Is_Only_Orderer(personal_id) 
    return render(request, 'yandex/insufficient_balance_message.html',{
        'check': check,
        'personal_id': personal_id,
        })

# Adds an account number to the user.
def add_user_account_table(request,personal_id,service_type):
    if request.method == 'POST':
        form = User_Account_Form(request.POST)
        if form.is_valid():
           account_num = form.cleaned_data["account_num"]
           balance = random.randint(50,100)
           obj = Users_Accounts(
               personal_id = personal_id,
               account = account_num,
               amount = balance,
           )
           obj.save()
           return redirect('choose_payment_method',personal_id=personal_id,service_type=service_type)
    text = "you don't have add account if you want pay on card please add it"
    text2 = "Add Account"    
    return render(request, 'yandex/add_user_account_table.html',{
        'form': User_Account_Form(),
        'text': text,
        'text2': text2,
        })

# When the taxi driver receives the order, the customer will be charged
# The fare from the balance is the transferred amount.
def Cut_Amount_Ordere_From_Balance(orderer_pers_id,amount):
    balance = Users_Accounts.objects.get(personal_id=orderer_pers_id).amount
    obj = Users_Accounts.objects.get(personal_id=orderer_pers_id)
    obj.amount = balance - amount
    obj.save()

# Adds user records to the following tables:
# Show_Data_Table, Current_Orderers_Table, Compliance_Table.
def new_process(personal_id,service_type):
    obj = Show_Data_Table.objects.get(orderer_pers_id=personal_id)
    obj.show = False
    obj.save()
    Insert_Orderer_In_Current_Orderers_Table(personal_id,service_type)
    Insert_Orderer_In_Compliance_Table(personal_id)

# When the client makes a call, the given process is issued for it
# The message that its call is fixed also shows the "DELETE ORDER" button
# which, if pressed, can cancel the call.
def message_text(request,personal_id):
   # POST means that the client has canceled the call or pressed the "DELETE ORDER" button;
   if request.method == 'POST':
       Delete_Orderer_from_Cur_Tab(personal_id) 
       Delete_Orderer_from_Comp_Tab(personal_id)
       check = True
       if User_Is_Only_Orderer(personal_id):
           check = False
       text = 'Your order has been successfully cancelled'
       return render(request, 'yandex/message_text2.html',{
           'text': text,
           'personal_id': personal_id,
           'check': check,
           })
   return render(request, 'yandex/message_text.html')

# show driver data to client(personal_id).
def show_driver_data(request,personal_id):
    taxi_driver_pers_id = Received_Call_Table.objects.get(orderer_pers_id=personal_id).taxi_driver_pers_id
    distance = Received_Call_Table.objects.get(orderer_pers_id=personal_id).distance
    distance2 = Received_Call_Table.objects.get(orderer_pers_id=personal_id).distance2 
    distance_time = Received_Call_Table.objects.get(orderer_pers_id=personal_id).distance_time 
    distance_time2 = Received_Call_Table.objects.get(orderer_pers_id=personal_id).distance_time2 
    amount = Received_Call_Table.objects.get(orderer_pers_id=personal_id).amount 
    taxi_driver_data = Taxi_Driver.objects.get(personal_id=taxi_driver_pers_id)
    obj = Show_Data_Table.objects.get(orderer_pers_id=personal_id)
    obj.show = True
    obj.save()
    return render(request, 'yandex/show_driver_data.html',{
        'taxi_driver_data': taxi_driver_data,
        'distance': distance,
        'distance2': distance2, 
        'distance_time': distance_time, 
        'distance_time2': distance_time2, 
        'amount': amount, 
        })

# Adds the orderer as a taxi driver, that is, he will be able
# to work as well as call a taxi.
def add_as_taxi_driver(request,personal_id):
    if request.method == "POST":
        user_has_account = USer_Has_Account(personal_id)
        form = ''
        if user_has_account:
           form = Add_As_Taxi_Driver_Form(request.POST)
        else:
           form = Add_As_Taxi_Driver_Form2(request.POST)
        if form.is_valid():
            account_num = ''
            if user_has_account:
                account_num = Get_Account_Number(personal_id)
            else:
                account_num = form.cleaned_data["account_num"]
                obj = Users_Accounts(
                    personal_id = personal_id,
                    account = account_num,
                    amount = random.randint(50,100)
                )
                obj.save()
            obj = Taxi_Driver(
                name = Orderer.objects.get(personal_id=personal_id).name,
                personal_id = personal_id,
                phone_num = Orderer.objects.get(personal_id=personal_id).phone_num,
                car_series = form.cleaned_data["car_series"],
                car_num = form.cleaned_data["car_num"],
                car_color = form.cleaned_data["car_color"] ,
                service_type = form.cleaned_data['service_type'],
                account_num = account_num,
            )
            obj.save()
            text = "Successful added as a taxi driver"
            return render(request, 'yandex/message_text2.html',{
                'text': text,
                'personal_id': personal_id,
                'check': True,
                })
    user_has_account = USer_Has_Account(personal_id)
    form = ''
    if user_has_account:
       form = Add_As_Taxi_Driver_Form()
    else:
        form = Add_As_Taxi_Driver_Form2()
    return render(request, 'yandex/add_as_taxi_driver.html',{"form": form})
    

# This is the case when the user is both an orderer and a taxi driver
# Canceled only the taxi driver, so that the error did not occur with the back exit arrow
# Put this check in process_for_users and since this user was deleted as a taxi driver
# Essay is just an orderer and will pass process_for_orderers to this function.
def User_Is_Only_Orderer(personal_id):
    orderer_pers_ids = list(Orderer.objects.values_list('personal_id', flat=True))
    taxi_driver_pers_ids = list(Taxi_Driver.objects.values_list('personal_id', flat=True))
    if (personal_id in orderer_pers_ids) and (personal_id not in taxi_driver_pers_ids):
       return True
    return False

# Checks whether the given (personal_id) user has a taxi.
def is_call_taxi(personal_id):
    cur_ord_pers_ids = list(Current_Orderers_Table.objects.values_list('orderer_pers_id', flat=True))
    if personal_id in cur_ord_pers_ids:
        return True
    return False

# Checks whether the call of the given user (personal_id)
# was taken by any taxi driver.
def taxi_driver_recieve_call(personal_id):
    received_ord_pers_ids = list(Received_Call_Table.objects.values_list('orderer_pers_id', flat=True))
    if personal_id in received_ord_pers_ids:
        return True
    return False

# Removes the orderer from the Current_Orderers_Table table.
def Delete_Orderer_from_Cur_Tab(personal_id):
    orderer_pers_ids = list(Current_Orderers_Table.objects.values_list('orderer_pers_id', flat=True))
    if personal_id in orderer_pers_ids:
       Current_Orderers_Table.objects.get(orderer_pers_id=personal_id).delete() 

# Removes the orderer from the Compliance_Table table.
def Delete_Orderer_from_Comp_Tab(personal_id):
    orderer_pers_ids = list(Compliance_Table.objects.values_list('orderer_pers_id', flat=True))
    if personal_id in orderer_pers_ids:
       Compliance_Table.objects.filter(orderer_pers_id=personal_id).delete()

# Removes the orderer from the Received_Call_Table table.
def Delete_Orderer_from_Rec_Call_Tab(personal_id):
    orderer_pers_ids = list(Received_Call_Table.objects.values_list('orderer_pers_id', flat=True))
    if personal_id in orderer_pers_ids:
       Received_Call_Table.objects.get(orderer_pers_id=personal_id).delete()

# Returns the amount of personal ID and service provided
# According to the service from the Potential_Current_Orderer table.
def Get_Amount_From_Potential_Current_Orderers_Table(personal_id,service_type):
    obj = Potential_Current_Orderer.objects.get(personal_id=personal_id)
    amount = 0
    if service_type == "Economy":
       amount = obj.economy
    elif service_type == "Comfort":
        amount = obj.comfort
    else:
        amount = obj.business
    return amount


# Adds a customer to the Current_Orderers_Table table.
def Insert_Orderer_In_Current_Orderers_Table(personal_id,service_type):
    distance = Potential_Current_Orderer.objects.get(personal_id=personal_id).distance
    amount = Get_Amount_From_Potential_Current_Orderers_Table(personal_id,service_type)
    cur_orderer = Current_Orderers_Table(
              orderer_pers_id = personal_id,
              service_type = service_type,
              distance = distance,
              amount = amount
              )
    cur_orderer.save()

# Adds customer records to the Compliance_Table table.
def Insert_Orderer_In_Compliance_Table(personal_id):
    current_taxi_drivers = list(Current_Taxi_Drivers_Table.objects.values_list('taxi_driver_pers_id', flat=True))
    if len(current_taxi_drivers) > 0:
        cur_ord_serv_type = Current_Orderers_Table.objects.get(orderer_pers_id=personal_id).service_type
        for current_taxi_driver in current_taxi_drivers:
            cur_tax_driv_serv_type = Current_Taxi_Drivers_Table.objects.get(taxi_driver_pers_id=current_taxi_driver).service_type
            if cur_ord_serv_type == cur_tax_driv_serv_type:
                distance = random.randint(1,5) 
                distance2 = Current_Orderers_Table.objects.get(orderer_pers_id=personal_id).distance 
                distance_time = distance * 0.8 
                distance_time2 = distance2 * 0.8 
                amount = Current_Orderers_Table.objects.get(orderer_pers_id=personal_id).amount 
                obj = Compliance_Table(
                        taxi_driver_pers_id = current_taxi_driver,
                        orderer_pers_id = personal_id,
                        distance = distance,
                        distance2 = distance2, 
                        distance_time = distance_time, 
                        distance_time2 = distance_time2, 
                        amount = amount 
                    )
                obj.save()

# delete customer records from the given tables where they are, because the account has been canceled,
# Orderer, Current_Orderer_Table, compliance_table, received_call_table.
def Delete_Orderer_From_Every_Tables(personal_id):
    Orderer.objects.get(personal_id=personal_id).delete()
    Show_Data_Table.objects.get(orderer_pers_id=personal_id).delete()
    Delete_Orderer_from_Comp_Tab(personal_id)
    Delete_Orderer_from_Cur_Tab(personal_id)
    Delete_Orderer_from_Rec_Call_Tab(personal_id)
    Delete_Orderer_From_Potential_Current_Orderer(personal_id)
    Delete_Orderer_From_Users_Accounts(personal_id)

# Removes a taxi driver from the Current_Taxi_Drivers_Table table.
def Delete_Taxi_Driver_from_Cur_Tab(personal_id):
    taxi_driver_pers_ids = list(Current_Taxi_Drivers_Table.objects.values_list('taxi_driver_pers_id', flat=True))
    if personal_id in taxi_driver_pers_ids:
       Current_Taxi_Drivers_Table.objects.get(taxi_driver_pers_id=personal_id).delete() 

# Removes the taxi driver from the Compliance_Table table.
def Delete_Taxi_Driver_from_Comp_Tab(personal_id):
    taxi_driver_pers_ids = list(Compliance_Table.objects.values_list('taxi_driver_pers_id', flat=True))
    if personal_id in taxi_driver_pers_ids:
       Compliance_Table.objects.filter(taxi_driver_pers_id=personal_id).delete()

# Removes the taxi driver from the Received_Call_Table table.
def Delete_Taxi_Driver_from_Rec_Call_Tab(personal_id):
    taxi_driver_pers_ids = list(Received_Call_Table.objects.values_list('taxi_driver_pers_id', flat=True))
    if personal_id in taxi_driver_pers_ids:
       Received_Call_Table.objects.get(taxi_driver_pers_id=personal_id).delete()

# Taxi driver records are deleted from the given tables where they are,
# Taxi_Driver, Current_Taxi_Drivers_Table, Compliance_Table, Received_Call_Table.
def Delete_Taxi_Driver_From_Every_Tables(personal_id):
    Taxi_Driver.objects.get(personal_id=personal_id).delete()
    Delete_Taxi_Driver_from_Comp_Tab(personal_id)
    Delete_Taxi_Driver_from_Cur_Tab(personal_id)
    Delete_Taxi_Driver_from_Rec_Call_Tab(personal_id)
    Delete_Orderer_From_Users_Accounts(personal_id)

# Deletes user records from all tables where they are because the account has been canceled.
def Delete_User_From_Every_Tables(personal_id):
    Delete_Taxi_Driver_From_Every_Tables(personal_id)
    Delete_Orderer_From_Every_Tables(personal_id)

# Checks if the taxi driver is in the Current_Taxi_Drivers_Table table.
def User_Is_Current_As_Taxi_Driver(personal_id):
    taxi_driver_pers_ids = list(Current_Taxi_Drivers_Table.objects.values_list('taxi_driver_pers_id', flat=True))
    if personal_id in taxi_driver_pers_ids:
       return True
    return False

# Checks if the taxi driver is in the Current_Orderers_Table table.
def User_Is_Current_As_Orderer(personal_id):
    orderer_pers_ids = list(Current_Orderers_Table.objects.values_list('orderer_pers_id', flat=True))
    if personal_id in orderer_pers_ids:
       return True
    return False

# Adds a taxi driver to the Current_Taxi_Drivers_Table table.
def Insert_taxi_Driver_In_Current_Orderers_Table(personal_id,service_type):
    taxi_driver = Current_Taxi_Drivers_Table(
              taxi_driver_pers_id = personal_id,
              service_type = service_type,
              )
    taxi_driver.save()

# Adds taxi driver records to the Compliance_Table table.
def Insert_Taxi_Driver_In_Compliance_Table(personal_id):
    current_orderers = list(Current_Orderers_Table.objects.values_list('orderer_pers_id', flat=True))
    if len(current_orderers) > 0:
        cur_tax_driv_serv_type = Current_Taxi_Drivers_Table.objects.get(taxi_driver_pers_id=personal_id).service_type
        for current_orderer in current_orderers:
            cur_ord_serv_type = Current_Orderers_Table.objects.get(orderer_pers_id=current_orderer).service_type
            if cur_ord_serv_type == cur_tax_driv_serv_type:
                distance = random.randint(1,5)
                distance2 = Current_Orderers_Table.objects.get(orderer_pers_id=current_orderer).distance 
                distance_time = distance * 0.8 
                distance_time2 = distance2 * 0.8 
                amount = Current_Orderers_Table.objects.get(orderer_pers_id=current_orderer).amount 
                obj = Compliance_Table(
                        taxi_driver_pers_id = personal_id,
                        orderer_pers_id = current_orderer,
                        distance = distance,
                        distance2 = distance2, 
                        distance_time = distance_time, 
                        distance_time2 = distance_time2, 
                        amount = amount 
                    )
                obj.save()

# Shows the customer data to the taxi driver.
def show_client_data(request,personal_id):
    name = Orderer.objects.get(personal_id=personal_id).name
    phone_num = Orderer.objects.get(personal_id=personal_id).phone_num
    distance = Received_Call_Table.objects.get(orderer_pers_id=personal_id).distance
    distance2 = Received_Call_Table.objects.get(orderer_pers_id=personal_id).distance2 
    distance_time = Received_Call_Table.objects.get(orderer_pers_id=personal_id).distance_time 
    distance_time2 = Received_Call_Table.objects.get(orderer_pers_id=personal_id).distance_time2 
    amount = Received_Call_Table.objects.get(orderer_pers_id=personal_id).amount 
    taxi_driver_pers_id = Received_Call_Table.objects.get(orderer_pers_id=personal_id).taxi_driver_pers_id
    service_type = Taxi_Driver.objects.get(personal_id=taxi_driver_pers_id).service_type
    return render(request, 'yandex/show_client_data.html',{
        'name': name,
        'phone_num': phone_num,
        'distance': distance,
        'service_type': service_type,
        'personal_id': taxi_driver_pers_id,
        'distance2': distance2, 
        'distance_time': distance_time, 
        'distance_time2': distance_time2, 
        'amount': amount, 
        })
 
# Adds a record of the transmitted data to the Received_Call_Table table.
def Insert_In_Received_Call_Table(taxi_driver_pers_id,orderer_pers_id,distance,distance2,distance_time,distance_time2,amount):
    obj = Received_Call_Table(
                    taxi_driver_pers_id = taxi_driver_pers_id,
                    orderer_pers_id = orderer_pers_id,
                    distance = distance,
                    distance2 = distance2, 
                    distance_time = distance_time, 
                    distance_time2 = distance_time2, 
                    amount = amount, 
                    )
    obj.save()

# Work process of a taxi driver.
def work(request,personal_id):
    if request.method == 'POST':
       delete_value = request.POST.get('delete_work')
       if delete_value is None:
          orderer_pers_id = int(request.POST.get('receive'))
          compliance_entries = Compliance_Table.objects.filter(taxi_driver_pers_id=personal_id, orderer_pers_id=orderer_pers_id)
          distance = [entry.distance for entry in compliance_entries]
          distance2 = [entry.distance2 for entry in compliance_entries] 
          distance_time = [entry.distance_time for entry in compliance_entries] 
          distance_time2 = [entry.distance_time2 for entry in compliance_entries] 
          amount = [entry.amount for entry in compliance_entries] 
          Insert_In_Received_Call_Table(personal_id,orderer_pers_id,distance[0],distance2[0],distance_time[0],distance_time2[0],amount[0])
          Delete_Taxi_Driver_from_Cur_Tab(personal_id)
          Delete_Taxi_Driver_from_Comp_Tab(personal_id)
          Delete_Orderer_from_Cur_Tab(orderer_pers_id)
          Delete_Orderer_from_Comp_Tab(orderer_pers_id)
          Cut_Amount_Ordere_From_Balance(orderer_pers_id,amount[0])
          Add_Amount_Taxi_Driver(personal_id,amount[0])
          return redirect('show_client_data', personal_id=orderer_pers_id)
       else:
           Delete_Taxi_Driver_from_Cur_Tab(personal_id)
           Delete_Taxi_Driver_from_Comp_Tab(personal_id)
           return redirect('process_for_users',personal_id=personal_id)

    orders_list = []
    is_calls = False
    if not User_Is_Current_As_Taxi_Driver(personal_id):
        service_type = Taxi_Driver.objects.get(personal_id=personal_id).service_type
        Insert_taxi_Driver_In_Current_Orderers_Table(personal_id,service_type)
        Insert_Taxi_Driver_In_Compliance_Table(personal_id)
    taxi_driver_pers_ids = list(Compliance_Table.objects.values_list('taxi_driver_pers_id', flat=True))
    if personal_id in taxi_driver_pers_ids:
        is_calls = True
        calls = Compliance_Table.objects.filter(taxi_driver_pers_id=personal_id)
        for call in calls:
           name = Orderer.objects.get(personal_id=call.orderer_pers_id).name
           orderer_pers_id = call.orderer_pers_id
           distance = call.distance
           distance2 = call.distance2 
           distance_time = call.distance_time 
           distance_time2 = call.distance_time2 
           amount = call.amount 
           list1 = [name,orderer_pers_id,distance,distance2,distance_time,distance_time2,amount]
           orders_list.append(list1)
    return render(request, 'yandex/work.html',{
        'list': orders_list,
        'is_calls': is_calls,
        })

# Removes the customer from the Potential_Current_Orderer table if present.
def Delete_Orderer_From_Potential_Current_Orderer(personal_id):
    pers_ids = list(Potential_Current_Orderer.objects.values_list('personal_id', flat=True))
    if personal_id in pers_ids:
        Potential_Current_Orderer.objects.get(personal_id=personal_id).delete()

# Removes the client from the Users_Accounts table if present.
def  Delete_Orderer_From_Users_Accounts(personal_id):
    pers_ids = list(Users_Accounts.objects.values_list('personal_id', flat=True))
    if personal_id in pers_ids:
        Users_Accounts.objects.get(personal_id=personal_id).delete()

# Adds a customer to the Potential_Current_Orderer table.
def Insert_In_Potential_Current_Orderer(personal_id):
    Delete_Orderer_From_Potential_Current_Orderer(personal_id)
    distance = random.randint(2,50)
    economy = distance * 0.5
    comfort = distance * 1
    business = distance * 2
    obj = Potential_Current_Orderer(
        personal_id = personal_id,
        distance = distance,
        economy = economy,
        comfort = comfort,
        business = business
    )
    obj.save()

# Adds the transferred amount, which is the fare, to the taxi driver.
def Add_Amount_Taxi_Driver(personal_id,amount):
    obj = Users_Accounts.objects.get(personal_id=personal_id)
    balance = obj.amount
    obj.amount = balance + amount
    obj.save()

# Checks if the user has an account added to the Users_Accounts table.
def USer_Has_Account(personal_id):
    pers_ids = list(Users_Accounts.objects.values_list('personal_id', flat=True))
    if personal_id in pers_ids:
        return True
    return False

# Returns the user's account number.
def Get_Account_Number(personal_id):
    return Users_Accounts.objects.get(personal_id=personal_id).account

# Allows the user to choose one of three services:
# 'Economy', 'Comfort', 'Business'
def choose_service_type(request,personal_id):
    # POST means that the client called a taxi or pressed one of the three buttons;
        if request.method == 'POST':
            service_type = request.POST.get('service_type')
            return redirect('choose_payment_method',personal_id=personal_id,service_type=service_type) 
        obj = Potential_Current_Orderer.objects.get(personal_id=personal_id) 
        return render(request, 'yandex/choose_service_type.html',{
            "personal_id": personal_id,
            "economy": obj.economy, 
            "comfort": obj.comfort, 
            "business": obj.business, 
            "distance": obj.distance 
        })

# Allows user to add account number Or if you want to change it.
def add_or_change_account_number(request,personal_id):
    if request.method == 'POST':
        form = User_Account_Form(request.POST)
        if form.is_valid():
           account_num = form.cleaned_data["account_num"]
           balance = random.randint(50,100)
           obj = Users_Accounts(
               personal_id = personal_id,
               account = account_num,
               amount = balance,
           )
           obj.save()
           if User_Is_Only_Orderer(personal_id):
              return redirect('process_for_orderers',personal_id=personal_id)
           return redirect('process_for_users',personal_id=personal_id)
    text = ''
    text2 = ''
    if USer_Has_Account(personal_id):
       text = "please enter new account number, if you want change it"
       text2 = "Change Account"
    else:
       text = "you don't have add account if you want pay on card please add it" 
       text2 = "Add Account"   
    return render(request, 'yandex/add_user_account_table.html',{
        'form': User_Account_Form(),
        'text': text,
        'text2': text2,
        })

# Allows user to delete account if added.
def delete_account_num(request,personal_id):
    if request.method == 'POST':
       Delete_Orderer_From_Users_Accounts(personal_id)
       return redirect('process_for_orderers',personal_id=personal_id)
    name = Orderer.objects.get(personal_id=personal_id).name
    return render(request, 'yandex/delete_account_num.html',{'name': name})
       

