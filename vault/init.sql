CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    country VARCHAR(100),
    population INTEGER
);

INSERT INTO cities (name, country, population) VALUES
('New York', 'USA', 8419600),
('Tokyo', 'Japan', 13929286),
('Paris', 'France', 2148327),
('São Paulo', 'Brazil', 12300000),
('Cairo', 'Egypt', 9915000),
('Berlin', 'Germany', 3769000);
