BEGIN TRANSACTION;
CREATE TABLE category (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
INSERT INTO "category" (name) VALUES('Clothes');
INSERT INTO "category" (name) VALUES('Shoes');
INSERT INTO "category" (name) VALUES('Tools');
INSERT INTO "category" (name) VALUES('Toys');
CREATE TABLE login (
	id SERIAL NOT NULL, 
	oauth_id BIGINT, 
	name VARCHAR(60), 
	email VARCHAR(100), 
	PRIMARY KEY (id), 
	UNIQUE (oauth_id)
);
INSERT INTO "login" VALUES(0,0,'Chris',NULL);
CREATE TABLE product (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	price NUMERIC(10, 2), 
	description VARCHAR(500), 
	"imageName" VARCHAR(100) DEFAULT 'default_product.png', 
	"dateAdded" DATE DEFAULT '2016-02-03 00:00:00' NOT NULL, 
	category_id INTEGER, 
	seller_id INTEGER, 
	PRIMARY KEY (id), 
	UNIQUE (name), 
	FOREIGN KEY(category_id) REFERENCES category (id), 
	FOREIGN KEY(seller_id) REFERENCES login (id)
);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('Black Dress',49.99,'A beautiful dress','black-dress-clipart.jpg','2016-02-03 00:00:00',1,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('T-shirt',29.99,'A basic black t-shirt','t-shirt.jpg','2016-02-03 00:00:00',1,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('Socks',19.99,'Nice athletic socks','socks.jpg','2016-02-03 00:00:00',1,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('Jacket',39.99,'Uniform-style jacket','jacket.png','2016-02-03 00:00:00',1,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('Skirt',39.99,'A very colorful skirt','skirt.jpg','2016-02-03 00:00:00',1,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('Suit',199.99,'A navy suit','suit.jpg','2016-02-03 00:00:00',1,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('Leather Boots',79.99,'Sturdy leather boots','leather-boots.jpg','2016-02-03 00:00:00',2,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('Sandals',69.99,'Comfortable flip-flops','sandals.jpg','2016-02-03 00:00:00',2,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('Sneakers',89.99,'High quality running sneakers','sneakers.jpg','2016-02-03 00:00:00',2,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('Slippers',79.99,'Retro slippers','slippers.jpg','2016-02-03 00:00:00',2,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('Dress shoes',99.99,'Premium material dress shoes','dress-shoes.jpg','2016-02-03 00:00:00',2,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('Hammer',5.99,'It''s a hammer','hammer.png','2016-02-03 00:00:00',3,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('Screwdriver',5.99,'Phillip''s screwdriver','screwdriver.png','2016-02-03 00:00:00',3,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('Pliers',6.99,'Needle-nose pliers','pliers.jpg','2016-02-03 00:00:00',3,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('Ruler',3.99,'Metric ruler','ruler.png','2016-02-03 00:00:00',3,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('Thermometer',4.99,'Tells the temperature','thermometer.png','2016-02-03 00:00:00',3,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('Building blocks',14.99,'Hundreds of blocking blocks','building-blocks.jpg','2016-02-03 00:00:00',4,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('Toy Truck',2.99,'Perfect gift for young kids','toy-truck.jpg','2016-02-03 00:00:00',4,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('Stuffed Bear',8.99,'A child''s best friend','stuffed-bear.jpg','2016-02-03 00:00:00',4,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('Dice',3.99,'Dice that can be used for all kinds of games','dice.jpg','2016-02-03 00:00:00',4,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('Jigsaw puzzle',9.99,'1000-piece jigsaw puzzle','jigsaw-puzzle.jpg','2016-02-03 00:00:00',4,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('TET',5.99,'safd','default_product.png','2016-02-03 00:00:00',1,0);
INSERT INTO "product" (name, price, description, "imageName", "dateAdded", category_id, seller_id) 
	VALUES('ELTKJLFS',8.99,'dsafkh','Screen_Shot_2016-01-15_at_9.40.39_PM.png','2016-02-03 00:00:00',1,0);
CREATE TABLE shopping_cart (
	buyer_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	quantity INTEGER DEFAULT '1', 
	PRIMARY KEY (buyer_id, product_id), 
	FOREIGN KEY(buyer_id) REFERENCES login (id), 
	FOREIGN KEY(product_id) REFERENCES product (id)
);
CREATE TABLE review (
	id SERIAL NOT NULL, 
	rating INTEGER, 
	description VARCHAR(500), 
	"dateAdded" DATE DEFAULT '2016-02-03' NOT NULL, 
	product_id INTEGER, 
	user_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES product (id), 
	FOREIGN KEY(user_id) REFERENCES login (id)
);
INSERT INTO "review" (rating, description, "dateAdded", product_id, user_id) 
	VALUES(5,'Very comfortable and last long','2016-02-03',3,0);
INSERT INTO "review" (rating, description, "dateAdded", product_id, user_id) 
	VALUES(3,'Very sturdy!','2016-02-03',8,0);
INSERT INTO "review" (rating, description, "dateAdded", product_id, user_id) 
	VALUES(4,'If you have nails, you *need* this hammer','2016-02-03',13,0);
INSERT INTO "review" (rating, description, "dateAdded", product_id, user_id) 
	VALUES(4,'Every child would love this stuff animal','2016-02-03',20,0);
COMMIT;
