SET FOREIGN_KEY_CHECKS = 0;
SET AUTOCOMMIT = 0;

CREATE OR REPLACE TABLE timingserviceUsers (
  userID int AUTO_INCREMENT PRIMARY KEY,
  secret varchar(255) UNIQUE NOT NULL,
  address varchar(255),
  timezone int DEFAULT -8
);

CREATE OR REPLACE TABLE timingserviceTimers (
  timerID INT AUTO_INCREMENT PRIMARY KEY,
  userID INT NOT NULL,
  timerName varchar(255) NOT NULL,
  time datetime NOT NULL,
  payload JSON NOT NULL CHECK (json_valid(`payload`)),
  ack datetime,
  UNIQUE (userID, timerName),
  FOREIGN KEY (userID) REFERENCES timingserviceUsers (userID) 
  ON DELETE CASCADE ON UPDATE CASCADE
);

SET FOREIGN_KEY_CHECKS = 1;
SET AUTOCOMMIT = 1;
