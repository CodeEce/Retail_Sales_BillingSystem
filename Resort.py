import mysql.connector
from _datetime import datetime

# connect database
def mysqlconnection():
    global mysqlDB
    mysqlDB = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='root',
        port=3306,
        database='resort_DB',
    )
    # sends commands to database and retrieves data.
    myCursor = mysqlDB.cursor()
    return myCursor

# Add customer data to database
def customerdetails():
    try:
        sqlConnect = mysqlconnection()
        cust_details = []
        cust_name = input("Enter the name of the customer : ")
        cust_details.append(cust_name)
        cust_contact = int(input("Enter the contact number of the customer : "))
        cust_details.append(cust_contact)
        cust_address = input("Enter the Address of the customer : ")
        cust_details.append(cust_address)
        cust_adharno = int(input("Enter the Aadhar number of the customer : "))
        cust_details.append(cust_adharno)
        cust_adults = int(input("Enter Number of Adults : "))
        cust_details.append(cust_adults)
        cust_kids = int(input("Enter the Number of kids : "))
        cust_details.append(cust_kids)
        cust_fromdate = input("Enter the Room Check_in Date, yyyy-mm-dd : ")
        cust_details.append(cust_fromdate)
        cust_todate = input("Enter the Room Check_out Date, yyyy-mm-dd : ")
        cust_details.append(cust_todate)
        sql = ("insert into cus_data(cusName,cusContact,cusAddress,AdharNo,Adult,Kids,fromdate,todate)values(%s,%s,"
               "%s,%s,%s,%s,%s,%s)")
        sqlConnect.execute(sql, tuple(cust_details))
        mysqlDB.commit()
        print("Cutomer Details Saved Successfully....")
    except Exception as e:
        print(e)
    finally:
        mysqlDB.close()
#customerdetails()

# get data from customer table,book room using cusId
def roomBooking():
   global bfCost, diCost, luCost, gTotal, sqlConnect, cusID, roomtype,noofdays,adult_count,kids_count
   try:
        sqlConnect = mysqlconnection()
        bookings = []
        rent = []
        print('We have the following type of rooms for you:-')
        print('Press 1. type First class Room Cost--->Rs 6000 PN')
        print('Press 2. type Business class Room cost around--->Rs 4000 PN')
        print('Press 3. type Economy class Room Cost around --->Rs 2000 PN')

        choice = int(input("Enter your choice : "))
        no_rooms = int(input("Enter How Many room you want?:"))
        bookings.append(no_rooms)
        roomno = input('Enter Room Number ,separated by commas if multiple').strip().split(",")
        roomNo = [x.strip() for x in roomno]
        room_no_string = ','.join(roomNo)
        if choice == 1:
            roomtype = "First Class"
            roomrent = 6000 * no_rooms
            rent.append(roomrent)
        elif choice == 2:
            roomtype = "Bussiness Class"
            roomrent = 4000 * no_rooms
            rent.append(roomrent)
        elif choice == 3:
            roomtype ="Economy Class"
            roomrent = 2000 * no_rooms
            bookings.append(roomtype)
            rent.append(roomrent)
        else:
            print('Please select a class type.')

        print("Booking Sucessfully!,Your room number is:",roomno)
        food = input("You Need Food? YES/NO : ").strip().lower()
        totalFoodcost = 0
        if food == "yes":
              print("For Adults PN --> BreakFast:100rs; Lunch:150rs; Dinner:120rs\nFor Kids PN -->Half the price")
              #finddate()
              sqlConnect.execute('SELECT cusId,Adult,Kids,fromdate,todate FROM cus_data ORDER BY cusId DESC LIMIT 1')
              record = sqlConnect.fetchone()
              if record is None:
                  print("No customer found")
                  return
              cusID,adult_count, kids_count,fromDate,toDate = record
              difference = toDate - fromDate
              noofdays = difference.days

              sqlConnect.execute('SELECT breakfast,lunch,dinner from food_details')
              getcost = sqlConnect.fetchone()
              if getcost is None:
                  print("Details not found")
                  return
              costBF,costL,costD = getcost
              meals = input("Enter your meal(s) (BF for Breakfast, LU for Lunch, DI for Dinner, separated by commas if multiple):").strip().upper().split(",")
              bfCost = 0
              luCost = 0
              diCost = 0
              for meal in meals:
                  if "BF" in meal:
                      bfCost = (adult_count * costBF) +(kids_count * costBF/2) * noofdays
                  if "LU" in meal:
                      luCost = (adult_count * costL) +(kids_count * costL/2) * noofdays
                  if "DI" in meal:
                      diCost = (adult_count * costD) + (kids_count * costD/2) * noofdays
              totalFoodcost = bfCost + luCost + diCost
              print("Your Meal Order Accepted")
        else:
            sqlConnect.execute('SELECT cusId,Adult,Kids,fromdate,todate FROM cus_data ORDER BY cusId DESC LIMIT 1')
            record = sqlConnect.fetchone()
            if record is None:
                print("No customer found")
                return
            cusID, adult_count, kids_count, fromDate, toDate = record
            difference = toDate - fromDate
            noofdays = difference.days
        rTotal = sum(rent)
        othercharges = int(input("Enter any other Charges Rs : "))
        gTotal = (rTotal * noofdays)+totalFoodcost+othercharges
        sql1 = "INSERT INTO roombooking(cusId,roomtype,noOfRooms,RoomNo) VALUES (%s,%s,%s,%s)"
        sql2 = "insert into invoice (no_days,rent,foodCost,otherCharges,grandTotal)values(%s, %s,%s,%s,%s)"
        sqlConnect.execute(sql1, (cusID,roomtype,no_rooms,room_no_string))
        sqlConnect.execute(sql2, (noofdays,rTotal,totalFoodcost, othercharges, gTotal))
        mysqlDB.commit()
        print("Thank you for choosing us....!")

   except Exception as e:
        print(e)
   finally:
      if sqlConnect:
         sqlConnect.close()
      if mysqlDB:
         mysqlDB.close()
#roomBooking()

# join tables and get combined data from database
def custinvoice():
    try:
        sqlConnect = mysqlconnection()
        print("**********CUSTOMER INVOINCE**********")
        contact = int(input("Enter Customer Contact Number to View Bill : "))
        sql = ("select r.cusId,c.cusName,c.cusContact,c.fromdate,c.todate,r.roomtype,r.noOfRooms,i.no_days,i.rent,i.foodcost,"
                       "i.othercharges,i.grandTotal from cus_data as c INNER JOIN roombooking as r ON c.cusId = r.cusId "
                      "inner join invoice as i on c.cusId = i.IID where c.cusContact = %s")
        num = (contact,)
        sqlConnect.execute(sql,num)
        viewBill = sqlConnect.fetchall()
        for bill in viewBill:
            (cusId,cusName,cusContact,fromdate,todate,roomtype,noOfRooms,rent,no_days,foodcost,othercharges,grandTotal) = bill
            print(f"Name of the Customer :{cusName},  Check_in : {fromdate},  Check_out : {todate}\nRoom Type : {roomtype},"
                  f"  No_Of Rooms : {noOfRooms}\nRoom Rent : {rent}, No Of Days : {no_days}, Food : {foodcost}, Other Charges : {othercharges}\n"
                  f"Grand Total : {grandTotal}")
        sqlConnect.close()
    except Exception as e:
        print(e)
    finally:
        mysqlDB.close()
#custinvoice()

# All customer history retrieve from database
def viewAllCus_Details():
    try:
        sqlConnect = mysqlconnection()
        sql = ("select r.cusId,c.cusName,c.cusContact,c.fromdate,c.todate,r.roomtype,r.noOfRooms,"
               "i.grandTotal from cus_data as c INNER JOIN roombooking as r ON c.cusId = r.cusId"
                " inner join invoice as i on c.cusId = i.IID")
        sqlConnect.execute(sql)
        viewdata = sqlConnect.fetchall()
        print("All Customer Details ........")
        for data in viewdata:
            print(data)
        sqlConnect.close()
    except Exception as e:
        print(e)
    finally:
        mysqlDB.close()

# Add resort details to DB
def resortdetails():
    try:
        sqlConnect = mysqlconnection()
        sqlConnect.execute('select COUNT(*) from resort_details')
        record_count = sqlConnect.fetchone()[0]
        if record_count > 0:
            print("The resort_details already Exist.")
        else:
            rest_details = []
            rest_name = input("Enter the name of the resort : ")
            rest_details.append(rest_name)
            rest_location = input("Enter the address of the resort : ")
            rest_details.append(rest_location)
            rest_contactNo = input("Enter the contact number of the resort : ")
            rest_details.append(rest_contactNo)
            # sql query to insert the data to database
            sql = 'insert into resort_details(rest_name,rest_location,rest_contactNo) values(%s,%s,%s)'
            # Execute the SQL query by passing the list as a tuple
            sqlConnect.execute(sql, tuple(rest_details))
            mysqlDB.commit()
            sqlConnect.close()
    except Exception as e:
        print(e)
    finally:
        mysqlDB.close()
#resortdetails()

# Add food cost into DB
def foodcost():
    try:
        sqlConnect = mysqlconnection()
        sqlConnect.execute("SELECT COUNT(*) from food_details")
        record_count = sqlConnect.fetchone()[0]
        if record_count > 0:
            print("The Cost of the Food already Exist.")
        else:
            food_cost = []
            BFcost = int(input("Enter the cost of Breakfast Per Day : "))
            food_cost.append(BFcost)
            LUcost = int(input("Enter the cost of Lunch Per Day : "))
            food_cost.append(LUcost)
            DIcost = int(input("Enter the cost of Dinner Per Day"))
            food_cost.append(DIcost)
            sql = "insert into food_details(breakfast,lunch,dinner)values(%s,%s,%s)"
            sqlConnect.execute(sql, tuple(food_cost))
            mysqlDB.commit()
            sqlConnect.close()
    except Exception as e:
        print(e)
    finally:
        mysqlDB.close()
#foodcost()

# back to main menu
def runagain():
    print()
    menu = input("Go to Main Menu: y/n")
    while True:
        if menu.lower() == "y":
            setMenu()
        else:
           setMenu()
#runagain()

# initialize page
def setMenu():
    print(" Welcome to Blue Hills International")
    print("Press 1 : Enter customer data for room booking")
    print("Press 2 : Customer Invoice ")
    print("Press 3 : View All Booking History")
    print("Press 4 : View Resort Details")
    print("Press 5 : Know Cost of Food")
    userInput = int(input("Enter your choice"))
    if userInput == 1:
        customerdetails()
        roomBooking()
    elif userInput == 2:
        custinvoice()
    elif userInput == 3:
        viewAllCus_Details()
    elif userInput == 4:
        resortdetails()
    elif userInput == 5:
        foodcost()
    else:
        print('Sorry! ,Invalid Option! >> Enter correct choice.')
    runagain()
setMenu()






