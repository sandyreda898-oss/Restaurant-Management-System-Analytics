USE RestaurantManagementSystem;

-----------------------------
-- 1) Roles
-----------------------------
INSERT INTO Roles (RoleName)
VALUES
('Admin'),
('Manager'),
('Cashier'),
('Chef'),
('Delivery');

-----------------------------
-- 2) Categories
-----------------------------
INSERT INTO Categories (CategoryName, Description)
VALUES
('Fast Food', 'Quick meals'),
('Pizza', 'Pizza varieties'),
('Pasta', 'Italian pasta'),
('Drinks', 'Beverages'),
('Desserts', 'Sweet dishes');

-----------------------------
-- 3) AddOns
-----------------------------
INSERT INTO AddOns (AddOnName, Price)
VALUES
('Extra Cheese',20),
('French Fries',30),
('Garlic Sauce',10),
('BBQ Sauce',10),
('Extra Chicken',40),
('Mushrooms',15),
('Olives',15),
('Soft Drink Upgrade',20);

-----------------------------
-- 4) Suppliers
-----------------------------
INSERT INTO Suppliers (SupplierName, ContactPerson, Phone, Email, Address)
VALUES
('Fresh Meat Co.','Mahmoud Adel','0111111111','meat@supplier.com','Cairo'),
('Dairy Best','Nour Hassan','0111111112','dairy@supplier.com','Giza'),
('Soft Drinks Egypt','Ali Reda','0111111113','drinks@supplier.com','Alexandria'),
('Bakery Supply','Hany Samir','0111111114','bakery@supplier.com','Mansoura');

-----------------------------
-- 5) Employees
-----------------------------
INSERT INTO Employees (FullName, RoleID, Phone, Salary, Username, PasswordHash)
VALUES
('Ahmed Hassan',1,'0100000001',15000,'admin1','hashed_password'),
('Mona Adel',2,'0100000002',12000,'manager1','hashed_password'),
('Sara Ali',3,'0100000003',6500,'cashier1','hashed_password'),
('Mohamed Samy',4,'0100000004',7500,'chef1','hashed_password'),
('Omar Tarek',5,'0100000005',5500,'delivery1','hashed_password'),
('Khaled Mostafa',5,'0100000006',5500,'delivery2','hashed_password');

-----------------------------
-- 6) MenuItems
-----------------------------
INSERT INTO MenuItems
(CategoryID, ItemName, Description, Price, CostPrice, Calories, PreparationTime)
VALUES
(1,'Classic Burger','Beef burger with fries',120,65,750,15),
(1,'Chicken Burger','Grilled chicken burger',110,55,680,12),
(1,'Double Burger','Double beef burger',170,90,980,18),
(2,'Margherita Pizza','Cheese pizza',180,90,950,20),
(2,'Pepperoni Pizza','Pepperoni pizza',220,110,1100,22),
(2,'BBQ Chicken Pizza','BBQ pizza',240,125,1150,25),
(3,'Pasta Alfredo','Creamy pasta',150,70,850,18),
(3,'Pasta Bolognese','Meat pasta',170,85,900,20),
(4,'Coca Cola','Soft drink',25,10,150,1),
(4,'Orange Juice','Fresh juice',35,15,180,2),
(4,'Water','Mineral water',15,5,0,1),
(5,'Chocolate Cake','Chocolate dessert',80,35,500,5),
(5,'Ice Cream','Vanilla ice cream',60,25,300,3);

-----------------------------
-- 7) Inventory
-----------------------------
INSERT INTO Inventory (IngredientName, QuantityAvailable, Unit, ReorderLevel, SupplierID)
VALUES
('Beef Meat',500,'Kg',50,1),
('Chicken Breast',400,'Kg',40,1),
('Cheese',300,'Kg',30,2),
('Pizza Dough',1000,'Pieces',100,4),
('Soft Drinks Bottles',5000,'Bottle',500,3),
('Pasta',700,'Kg',70,4),
('Chocolate',200,'Kg',20,4);

-----------------------------
-- 8) Coupons
-----------------------------
INSERT INTO Coupons (Code, DiscountType, DiscountValue, StartDate, EndDate, MaxUsage, Status)
VALUES
('WELCOME10','Percentage',10,GETDATE(),DATEADD(MONTH,6,GETDATE()),5000,'Active'),
('FREEDEL','Fixed',30,GETDATE(),DATEADD(MONTH,3,GETDATE()),3000,'Active'),
('SAVE20','Percentage',20,GETDATE(),DATEADD(MONTH,2,GETDATE()),2000,'Active');

-----------------------------
-- 9) Customers (1000 Rows)
-----------------------------
DECLARE @i INT = 1;
WHILE @i <= 1000
BEGIN
    INSERT INTO Customers
    (FullName, Phone, Email, PasswordHash, Address, City, LoyaltyPoints, Status)
    VALUES
    (
        CONCAT('Customer ', @i),
        CONCAT('01234', RIGHT('00000' + CAST(@i AS VARCHAR(5)),5)),
        CONCAT('customer', @i, '@mail.com'),
        'hashed_password',
        CONCAT('Address ', @i),
        CASE
            WHEN @i % 5 = 0 THEN 'Cairo'
            WHEN @i % 5 = 1 THEN 'Giza'
            WHEN @i % 5 = 2 THEN 'Alexandria'
            WHEN @i % 5 = 3 THEN 'Mansoura'
            ELSE 'Damietta'
        END,
        ABS(CHECKSUM(NEWID())) % 500,
        'Active'
    );

    SET @i = @i + 1;
END;

-----------------------------
-- 10) Orders (1000 Rows)
-----------------------------
SET @i = 1;
WHILE @i <= 1000
BEGIN
    DECLARE @cust INT = ((@i - 1) % 1000) + 1;
    DECLARE @total DECIMAL(10,2) = 100 + (ABS(CHECKSUM(NEWID())) % 400);
    DECLARE @tax DECIMAL(10,2) = @total * 0.14;
    DECLARE @discount DECIMAL(10,2) = ABS(CHECKSUM(NEWID())) % 50;
    DECLARE @delivery DECIMAL(10,2) = 30;
    DECLARE @final DECIMAL(10,2) = @total + @tax + @delivery - @discount;

    INSERT INTO Orders
    (CustomerID, OrderDate, TotalAmount, Tax, Discount, DeliveryFee, FinalAmount, PaymentStatus, OrderStatus, DeliveryAddress)
    VALUES
    (
        @cust,
        DATEADD(DAY, - (ABS(CHECKSUM(NEWID())) % 365), GETDATE()),
        @total,
        @tax,
        @discount,
        @delivery,
        @final,
        'Paid',
        CASE
            WHEN @i % 4 = 0 THEN 'Delivered'
            WHEN @i % 4 = 1 THEN 'Preparing'
            WHEN @i % 4 = 2 THEN 'Out for Delivery'
            ELSE 'Completed'
        END,
        CONCAT('Customer Address ', @cust)
    );

    SET @i = @i + 1;
END;

-----------------------------
-- 11) OrderDetails (2 Items per order minimum)
-----------------------------
SET @i = 1;
WHILE @i <= 1000
BEGIN
    INSERT INTO OrderDetails (OrderID, ItemID, Quantity, UnitPrice, SubTotal)
    VALUES
    (@i, ((@i % 13) + 1), 1 + (@i % 3), 100 + (@i % 100), (1 + (@i % 3)) * (100 + (@i % 100)));

    INSERT INTO OrderDetails (OrderID, ItemID, Quantity, UnitPrice, SubTotal)
    VALUES
    (@i, (((@i + 3) % 13) + 1), 1 + ((@i + 1) % 2), 50 + (@i % 50), (1 + ((@i + 1) % 2)) * (50 + (@i % 50)));

    SET @i = @i + 1;
END;

-----------------------------
-- 12) Payments
-----------------------------
SET @i = 1;
WHILE @i <= 1000
BEGIN
    INSERT INTO Payments
    (OrderID, PaymentMethod, PaymentDate, PaidAmount, TransactionID, PaymentStatus)
    SELECT
        @i,
        CASE
            WHEN @i % 3 = 0 THEN 'Cash'
            WHEN @i % 3 = 1 THEN 'Credit Card'
            ELSE 'Wallet'
        END,
        GETDATE(),
        FinalAmount,
        CONCAT('TXN', RIGHT('00000' + CAST(@i AS VARCHAR(5)),5)),
        'Completed'
    FROM Orders
    WHERE OrderID = @i;

    SET @i = @i + 1;
END;

-----------------------------
-- 13) Deliveries
-----------------------------
SET @i = 1;
WHILE @i <= 1000
BEGIN
    INSERT INTO Deliveries
    (OrderID, DeliveryEmployeeID, PickupTime, DeliveredTime, DeliveryStatus, CustomerRating)
    VALUES
    (
        @i,
        CASE WHEN @i % 2 = 0 THEN 5 ELSE 6 END,
        DATEADD(MINUTE, -45, GETDATE()),
        GETDATE(),
        'Delivered',
        3 + (@i % 3)
    );

    SET @i = @i + 1;
END;

-----------------------------
-- 14) Reviews (500 Rows)
-----------------------------
SET @i = 1;
WHILE @i <= 500
BEGIN
    INSERT INTO Reviews
    (CustomerID, OrderID, Rating, Comment)
    VALUES
    (
        @i,
        @i,
        3 + (@i % 3),
        CONCAT('Review for order ', @i)
    );

    SET @i = @i + 1;
END;

IF NOT EXISTS (SELECT 1 FROM Employees WHERE Username = 'admin1')
BEGIN
    INSERT INTO Employees
    (FullName, RoleID, Phone, Salary, Username, PasswordHash)
    VALUES
    ('Ahmed Hassan',1,'0100000001',15000,'admin1','hashed_password');
END


