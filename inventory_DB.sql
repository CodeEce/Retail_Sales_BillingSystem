create database inventory_db;
use inventory_db;
create table stock(
pid  varchar(100) primary key not null,
category varchar(200),
product varchar(200),
sQty int,
retPrice float,
stotal float
);
create table cusdata(
cusId int not null primary key auto_increment,
cusName varchar(100),
mobile varchar(10),
pdate datetime
);
create table cus_invoice(
invoiceId int primary key auto_increment,
cusId int ,
proName varchar(200),
pQty int,
selPrice decimal(10,2),
pTotal decimal(10,2),
gst decimal(5,2),
FOREIGN KEY (cusId) REFERENCES cusdata(cusId)
);
create table invoice_summary(
summaryId	int auto_increment primary key,
cusId	INT	,
overAlldiscount decimal(5,2),
totalAfterDisc decimal(10,2),
FOREIGN KEY (cusId) REFERENCES cusdata(cusId) );

select * from stock;
select * from cusdata;
select * from cus_invoice;
select * from invoice_summary;


  
