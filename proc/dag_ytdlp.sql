create table downloads (
    url varchar(150) primary key,
    channel varchar(40),
    download_date timestamptz
);