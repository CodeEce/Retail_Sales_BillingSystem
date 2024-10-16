import datetime
import mysql.connector

def mysqlconnection():
    global mySqlDb
    mySqlDb = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='root',
        port=3306,
        database='inventory_db',
    )

    sqlConnect = mySqlDb.cursor()
    return sqlConnect
def addStock():
    try:
        sqlConnect = mysqlconnection()
        stock = []
        while True:
            addPro = []
            productId = input("Enter Product ID : ")
            addPro.append(productId)
            category = input("Enter Product Category : ").title()
            addPro.append(category)
            pro_name = input("Enter Product Name : ").title()
            addPro.append(pro_name)
            sqty = int(input("Enter the Quantity : "))
            addPro.append(sqty)
            unitPriz = int(input("Enter the unit price of the Product : "))
            addPro.append(unitPriz)
            sTotal = sqty * unitPriz
            addPro.append(sTotal)
            print(sTotal)
            stock.append(addPro)
            addMore = input("Add more product? y/n : ").lower().strip()
            if addMore != 'y':
                print("\nProducts Saved Successfully....!")
                break
        sql = 'INSERT INTO stock(pid,category,product,sQty,retPrice,stotal)values(%s,%s,%s,%s,%s,%s)'
        sqlConnect.executemany(sql,tuple(stock))

        mySqlDb.commit()
        sqlConnect.close()
    except Exception as e:
        print(e)
    finally:
        mySqlDb.close()
#addStock()

def cusInvoice():
    try:
        sqlConnect = mysqlconnection()
        cusData = []
        cusBill = []
        totalAmount = 0
        # collect customer details
        cusname = input("Enter Customer Name : ")
        cusData.append(cusname)
        contactNum = input("Enter Customer Mobile Number : ")
        cusData.append(contactNum)
        purDate = datetime.datetime.now()
        cusData.append(purDate)

        # collect product details in loop
        while True:
            product = []
            proname = input("Enter the Product Name : ").strip().title()
            product.append(proname)
            pqty = int(input("Enter the Quantity : "))
            product.append(pqty)
            selPrice = float(input("Enter the Price : "))
            product.append(selPrice)
            gst = float(input("Enter the GST % : "))
            gstAmount = (pqty * selPrice * gst/100)  # Calculate GST amount
            productTotal = (pqty * selPrice) + gstAmount  # Total without GST
            product.append(productTotal)
            product.append(gstAmount)
            cusBill.append(product)
            totalAmount += productTotal
            buyMore = input("Add more product ? y/n :").lower().strip()
            if buyMore != 'y':
                break

        discount = float(input("Enter the discount % : "))
        discountAmt = totalAmount * discount/100
        totalAftDisc = totalAmount - discountAmt
        sql2 = 'INSERT INTO cusdata(cusName,mobile,pdate)values(%s,%s,%s)'
        sqlConnect.execute(sql2, tuple(cusData))

        sqlConnect.execute('select cusId from cusdata ORDER BY cusId DESC LIMIT 1')
        record = sqlConnect.fetchone()
        cusId = record[0]

        sql1 = 'INSERT INTO cus_invoice(cusId,proName,pQty,selPrice,pTotal,gst)values(%s,%s,%s,%s,%s,%s)'
        for product in cusBill:
            sqlConnect.execute(sql1, (cusId,) + tuple(product))
        sql3 = ('INSERT INTO invoice_summary(cusId, overAlldiscount, totalAfterDisc) VALUES (%s, %s, %s)')
        sqlConnect.execute(sql3, (cusId, discountAmt, totalAftDisc))
        print(f"Total Amount (with GST): {totalAmount:.2f}")
        print(f"Total discount: {discountAmt:.2f}")
        print(f"Total amount to be Paid : {totalAftDisc:.2f}")
        mySqlDb.commit()
        sqlConnect.close()
    except Exception as e:
        print(e)
    finally:
        mySqlDb.close()
#cusInvoice()
def viewBill():
    global sqlConnect, gst
    try:
        sqlConnect = mysqlconnection()
        contact = input("\nEnter Customer Mobile Number : ").strip()
        sql = ("SELECT c.cusId, c.cusName, c.pdate, c.mobile, "
            "i.proName, i.pQty, i.selPrice, i.pTotal,i.gst, "
            "s.overAlldiscount, s.totalAfterDisc "
            "FROM cusdata AS c "
            "INNER JOIN cus_invoice AS i ON c.cusId = i.cusId "
            "INNER JOIN invoice_summary AS s ON c.cusId = s.cusId "
            "WHERE c.mobile = %s")
        num = (contact,)
        sqlConnect.execute(sql,num)
        records = sqlConnect.fetchall()
        if records:  # Check if any record was found
            # Print customer details (common for all products)
            cusId, cusName, pdate, mobile = records[0][0:4]
            pTotal,overAlldiscount, totalAfterDisc = records[0][-3:]
            print(f"Bill No : {cusId}, Purchase Date : {pdate}, Contact : {mobile}, Customer Name : {cusName}\n")
            # Print product details (for each product)
            print("Product Details:")
            for record in records:
                proName, pQty, selPrice,pTotal,gst = record[4:9]
                print(f"Product : {proName}   QTY : {pQty}   Rate : {selPrice}   Total(with GST) : {pTotal:.2f}   GST : {gst:.2f}")
            print(f"Discount : {overAlldiscount:.2f}")
            print(f"Grand Total Rs : {totalAfterDisc:.2f}")
        else:
            print("No records found for the given mobile number.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if sqlConnect:
            sqlConnect.close()
#viewBill()

def profitLoss():

    global sqlConnect
    try:
        sqlConnect = mysqlconnection()
        print("\nEnter the Date Range to View the Sales Report.........\n")
        fromdate = input("Enter From Date --> yyyy-mm-dd : ")
        todate = input("Enter To Date --> yyyy-mm-dd : ")

        sql = (
            "SELECT c.cusId, c.cusName, c.pdate, c.mobile, "
            "i.proName, i.pQty, i.selPrice, i.pTotal, i.gst, "
            "s.category, s.product, s.sQty, s.retPrice, s.stotal, "
            "sum.overAlldiscount, sum.totalAfterDisc "
            "FROM cusdata AS c "
            "INNER JOIN cus_invoice AS i ON c.cusId = i.cusId "
            "INNER JOIN stock AS s ON i.proName = s.product "
            "INNER JOIN invoice_summary AS sum ON c.cusId = sum.cusId "
            "WHERE DATE(c.pdate) BETWEEN %s AND %s"
        )
        date = (fromdate,todate)
        sqlConnect.execute(sql,date)
        record = sqlConnect.fetchall()
        # Check if no records are found
        if not record:
            print("\nNo records found for the given date range.")
            return
        for data in record:
            (cusId,cusName,pdate,mobile,proName,pQty,selPrice,pTotal,gst,category,product,sQty,retPrice,stotal,overAlldiscount,totalAfterDisc) = data
            print("--------------------------")
            print(f"Cus ID : {cusId}, Purchase Date : {pdate}, Contact : {mobile}\nProduct : {proName}  QTY : {pQty}\nRetail Price : {retPrice},"
                  f"  Sold Price : {selPrice}\nTotal Without GST: {pTotal},  GST : {gst}\nDiscount(-) : {overAlldiscount}\nGrand Total : {totalAfterDisc}")
            retpCal = (pQty * retPrice)
            selPCal = (pQty * float(selPrice) - float(overAlldiscount))
            avg = selPCal - float(retpCal)
            if selPrice >retPrice:
                print(f"Profit Rs. : {avg:.2f}")
            else:
                print(f"Loss Rs : {avg:.2f}")
    except Exception as e:
        print(e)
    finally:
        if sqlConnect:
            sqlConnect.close()
#profitLoss()

def viewStock():
    global sqlConnet
    try:
        sqlConnet = mysqlconnection()
        sql = ('select pid,category,product,sQty,retPrice,sTotal from stock')
        sqlConnet.execute(sql)
        records = sqlConnet.fetchall()
        print("------------------------------------- Stock Details --------------------------------->\n")
        for record in records:
            (pid,category,product,sQty,retPrice,sTotal) = record
            print(f"Product ID : {pid},Category : {category},Product : {product},Qty : {sQty},Price : {retPrice},Total :{sTotal}")
    except Exception as e:
        print(e)
    finally:
        if sqlConnet:
            sqlConnet.close()
#viewStock()

# back to main menu
def runagain():
    print()
    menu = input("Go to Main Menu: y/n")
    while True:
        if menu.lower() == "y":
            Menu()
        else:
           Menu()
#runagain()
def Menu():
    print(" ------------------  Welcome to the Super Market--------------------")
    print("Press : 1--  Generate Bill")
    print("Press : 2--  View Bill ")
    print("Press : 3--  Sales Report ")
    print("Press : 4--  Add Stock Details ")
    print("Print : 5--  View Stock Details")
    get_input = int(input("Enter your Choice : "))
    if get_input == 1:
        cusInvoice()
    elif get_input == 2:
        viewBill()
    elif get_input == 3:
        profitLoss()
    elif get_input == 4:
        addStock()
    elif get_input == 5:
        viewStock()
    else:
        print('Sorry! ,Invalid Option! >> Enter correct choice.')
    runagain()
Menu()

