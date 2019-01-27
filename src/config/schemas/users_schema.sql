CREATE TABLE IF NOT EXISTS users (
    name varchar(255) PRIMARY KEY,
    password varchar(255),
    salt varchar(10)
);