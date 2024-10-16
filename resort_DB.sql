create database resort_DB;
use resort_db;
create table cus_data(
cusId int NOT NULL PRIMARY KEY AUTO_INCREMENT ,
cusName varchar(50) NOT NULL,
cusContact varchar(10) NOT NULL,
cusAddress varchar(200) NOT NULL,
AdharNo varchar(12),
Adult int,
kids int,
fromdate date NOT NULL,
todate date NOT NULL
);
create table resort_details(
RID int PRIMARY KEY AUTO_INCREMENT,
rest_name varchar(50),
rest_location varchar(150),
rest_contactNo varchar(15)
);
create table food_details(
FID int PRIMARY KEY AUTO_INCREMENT,
breakfast numeric,
lunch numeric,
dinner numeric
);
create table invoice(
IID int NOT NULL PRIMARY KEY AUTO_INCREMENT,
no_days int,
rent decimal(10,2),
foodCost decimal(10,2),
otherCharges decimal(10,2),
grandTotal decimal(10,2)
);
create table roombooking(
cusId int Not null,
roomtype varchar(100),
noOfRooms int ,
RoomNo varchar(200),
FOREIGN KEY (cusId) REFERENCES cus_data(cusId));
select * from resort_details;
select * from food_details;
select * from cus_data;
select * from invoice;
select * from roombooking;

