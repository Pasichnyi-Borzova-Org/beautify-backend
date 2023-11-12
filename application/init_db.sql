DROP TABLE IF EXISTS users;
CREATE TABLE users (
         username TEXT NOT NULL PRIMARY KEY,
         password TEXT NOT NULL,
         is_master INTEGER NOT NULL,
         name TEXT NOT NULL,
         surname TEXT NOT NULL,
         created_account TEXT NOT NULL,
         completed_orders INTEGER NULL,
         average_rating NUMERIC NULL,
         city TEXT
);

DROP TABLE IF EXISTS appointments;
CREATE TABLE  appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        master_user_name TEXT NOT NULL,
        client_user_name TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        price NUMERIC NOT NULL,
        description TEXT,
        FOREIGN KEY (master_user_name) REFERENCES users (username),
        FOREIGN KEY (client_user_name) REFERENCES users (username)
        );


INSERT INTO users (username, password, is_master, name, surname, created_account, completed_orders, average_rating, city)
VALUES('oleg25', 'qwerty23', 0, 'Oleg','Strunov', '2023-11-01 12:12:56', NULL, NULL, 'Kharkiv'),
      ('anna18', 'qwerty12', 0, 'Anna','Ivanova', '2023-10-25 16:24:14', NULL, NULL, 'Poltava'),
      ('maria45', 'password123', 1, 'Maria','Kolpan', '2023-10-13 09:20:28', 3, 4.6, NULL),
      ('alina27', 'pass1234', 1, 'Alina', 'Kovalenko', '2023-09-03 18:44:08', 15, 4.2, NULL);


INSERT INTO appointments (title, master_user_name, client_user_name, price, start_time, end_time, description)
VALUES('Manicure', 'alina27', 'oleg25', 500.00, '2023-11-06 12:50:00', '2023-11-06 13:50:00', 'French manicure'),
      ('Pedicure', 'maria45', 'oleg25', 150.50, '2023-11-02 09:30:00', '2023-11-02 10:30:00', 'No washing');
