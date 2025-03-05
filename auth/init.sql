CREATE DATABASE auth;

GRANT ALL PRIVILEGES ON DATABASE auth TO emmanuelanongba;

\c auth

CREATE TABLE users(
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL
);

INSERT INTO users (email, password) VALUES ('eanongba19@gmail.com', 'Admin123');

-- DROP DATABASE auth
ALTER DATABASE auth OWNER TO emmanuelanongba;
