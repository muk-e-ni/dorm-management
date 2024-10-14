      
    create table dorms (dormitory_int INT AUTO_INCREMENT PRIMARY KEY,
    dormitory_name VARCHAR(255) NOT NULL,
    total_cubicle INT NOT NULL,
    total_beds_per_cubicle INT NOT NULL
);


create table cubicles if not exists (cubicle_id int auto_increment primary key, 
    dormitory_int int, 
    cubicle_number int not null, 
    total_beds int not null,
     foreign key(dormitory_int) references dorms(dormitory_int))

 CREATE TABLE beds (
     cubicle_id INT,
    bed_id INT AUTO_INCREMENT PRIMARY KEY,
     bed_number INT NOT NULL,
     is_occupied BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (cubicle_id) REFERENCES cubicles(cubicle_id));


CREATE TABLE dormitory_members(
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
     Admission_NO VARCHAR(50) NOT NULL UNIQUE,
     Fisrt_Name text,
     Last_Name text,
     amount_paid int,
     dormitory_int INT,
     cubicle_id INT,
    bed_number INT,
    FOREIGN KEY (dormitory_int) REFERENCES dorms(dormitory_int),
    FOREIGN KEY (cubicle_id) REFERENCES cubicles(cubicle_id));



