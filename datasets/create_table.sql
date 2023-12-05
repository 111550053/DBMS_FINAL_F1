drop database if exists f1;
create database f1;
use f1;

create table circuits
(
    circuitId tinyint not null,
    circuitRef varchar(50) not null,
    name varchar(100) not null,
    location varchar(50),
    country varchar(50) not null,
    lat float not null,
    lng float not null,
    alt smallint,
    url varchar(200) not null,
    primary key (circuitId)
);

create table constructors
(
    constructorId smallint not null,
    constructorRef varchar(50) not null,
    name varchar(50) not null,
    nationality varchar(50) not null,
    url varchar(200) not null,
    primary key (constructorId)
);

create table drivers
(
    driverId smallint not null,
    driverRef varchar(50) not null,
    number smallint,
    code char(3),
    forename varchar(50) not null,
    surname varchar(50) not null,
    dob char(10) not null,
    nationality varchar(50) not null,
    url varchar(200),
    primary key (driverId)
);

create table races
(
    raceId smallint not null,
    year smallint not null,
    round tinyint not null,
    circuitId tinyint not null,
    name varchar(100) not null,
    date char(10),
    time char (10),
    url varchar(200),
    fp1_date char(10),
    fp1_time char(10),
    fp2_date char(10),
    fp2_time char(10),
    fp3_date char(10),
    fp3_time char(10),
    quali_date char(10),
    quali_time char(10),
    sprint_date char(10),
    sprint_time char(10),
    primary key (raceId),
    foreign key (circuitId) references circuits(circuitId)
);

create table constructor_results
(
    constructorResultsId smallint not null,
    raceId smallint not null,
    constructorId smallint not null,
    points tinyint,
    status varchar(20),
    primary key (constructorResultsId)
    -- foreign key (raceId) references races(raceId)
    -- foreign key (constructorId) references constructors(constructorId)
);

create table constructor_standings
(
    constructorStandingsId smallint not null,
    raceId smallint not null,
    constructorId smallint not null,
    points smallint not null,
    position tinyint not null,
    positionText varchar(10) not null,
    wins tinyint not null,
    primary key (constructorStandingsId)
    -- foreign key (raceId) references races(raceId)
    -- foreign key (constructorId) references constructors(constructorId)
);


create table driver_standings
(
    driverStandingsId mediumint not null,
    raceId smallint not null,
    driverId smallint not null,
    points smallint not null,
    position tinyint not null,
    positionText varchar(10) not null,
    wins tinyint not null,
    primary key (driverStandingsId)
    -- foreign key (raceId) references races(raceId),
    -- foreign key (driverId) references drivers(driverId)
);

create table lap_times
(
    raceId smallint not null,
    driverId smallint not null,
    lap smallint not null,
    position tinyint not null,
    time varchar(20) not null,
    milliseconds mediumint not null,
    primary key (raceId, driverId, lap)
    -- foreign key (raceId) references races(raceId),
    -- foreign key (driverId) references drivers(driverId)
);

create table pit_stops
(
    raceId smallint not null,
    driverId smallint not null,
    stop tinyint not null,
    lap tinyint not null,
    time char(10) not null,
    duration varchar(10) not null,
    milliseconds mediumint not null,
    primary key (raceId, driverId, stop)
);

create table qualifying
(
    qualifyId smallint not null,
    raceId smallint not null,
    driverId smallint not null,
    constructorId smallint not null,
    number smallint,
    position tinyint not null,
    q1 varchar(10),
    q2 varchar(10),
    q3 varchar(10),
    primary key (qualifyId),
    -- foreign key (raceId) references races(raceId),
    foreign key (driverId) references drivers(driverId),
    foreign key (constructorId) references constructors(constructorId)
);


create table results
(
    resultId smallint not null,
    raceId smallint not null,
    driverId smallint not null,
    constructorId smallint not null,
    number smallint,
    grid tinyint not null,
    position tinyint,
    positionText char(2),
    positionOrder tinyint,
    points tinyint not null,
    laps smallint not null,
    time varchar(20),
    milliseconds int,
    fastestLap tinyint,
    resultRank tinyint,
    fastestLapTime varchar(20),
    fastestLapSpeed float,
    statusId smallint,
    primary key (resultId),
    -- foreign key (raceId) references races(raceId),
    foreign key (driverId) references drivers(driverId),
    foreign key (constructorId) references constructors(constructorId)
);

create table seasons
(
    year smallint not null,
    url varchar(200),
    primary key (year)
);

create table sprint_results
(
    resultId smallint not null,
    raceId smallint not null,
    driverId smallint not null,
    constructorId smallint not null,
    number smallint,
    grid tinyint not null,
    position tinyint,
    positionText char(2) not null,
    positionOrder tinyint not null,
    points tinyint not null,
    laps smallint not null,
    time varchar(20),
    milliseconds mediumint,
    fastestLap tinyint,
    fastestLapTime varchar(20),
    statusId smallint not null,
    primary key (resultId),
    foreign key (raceId) references races(raceId),
    foreign key (driverId) references drivers(driverId),
    foreign key (constructorId) references constructors(constructorId)
);

create table status
(
    Id smallint not null,
    status varchar(100) not null,
    primary key (Id)
);

create table users
(
    userId smallint not null,
    userName varchar(100) not null,
    passwd varchar(100) not null,
    admin boolean not null,
    primary key (userId)
);

insert into users 
values (1, 'admin', 'admin', true);

create table custom_content
(
    customDataId smallint not null,
    userId smallint not null,
    customType tinyint not null,
    customcontentId smallint not null,
    primary key (customDataId)
);


load data local infile './circuits.csv'
into table circuits
fields terminated by ','
enclosed by '"'
lines terminated by '\n'
ignore 1 lines;

show warnings;

load data local infile './constructor_results.csv'
into table constructor_results
fields terminated by ','
enclosed by '"'
lines terminated by '\n'
ignore 1 lines;

show warnings;

load data local infile './constructor_standings.csv'
into table constructor_standings
fields terminated by ','
enclosed by '"'
lines terminated by '\n'
ignore 1 lines;

show warnings;

load data local infile './constructors.csv'
into table constructors
fields terminated by ','
enclosed by '"'
lines terminated by '\n'
ignore 1 lines;

show warnings;

load data local infile './driver_standings.csv'
into table driver_standings
fields terminated by ','
enclosed by '"'
lines terminated by '\n'
ignore 1 lines;

show warnings;

load data local infile './drivers.csv'
into table drivers
fields terminated by ','
enclosed by '"'
lines terminated by '\n'
ignore 1 lines;

show warnings;

load data local infile './lap_times.csv'
into table lap_times
fields terminated by ','
enclosed by '"'
lines terminated by '\n'
ignore 1 lines;

show warnings;

load data local infile './pit_stops.csv'
into table pit_stops
fields terminated by ','
enclosed by '"'
lines terminated by '\n'
ignore 1 lines;

show warnings;

load data local infile './qualifying.csv'
into table qualifying
fields terminated by ','
enclosed by '"'
lines terminated by '\n'
ignore 1 lines;

show warnings;

load data local infile './races.csv'
into table races
fields terminated by ','
enclosed by '"'
lines terminated by '\n'
ignore 1 lines;

show warnings;

load data local infile './results.csv'
into table results
fields terminated by ','
enclosed by '"'
lines terminated by '\n'
ignore 1 lines;

show warnings;

load data local infile './seasons.csv'
into table seasons
fields terminated by ','
enclosed by '"'
lines terminated by '\n'
ignore 1 lines;

show warnings;

load data local infile './sprint_results.csv'
into table sprint_results
fields terminated by ','
enclosed by '"'
lines terminated by '\n'
ignore 1 lines;

show warnings;

load data local infile './status.csv'
into table status
fields terminated by ','
enclosed by '"'
lines terminated by '\n'
ignore 1 lines;

show warnings;