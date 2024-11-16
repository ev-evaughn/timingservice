# timingservice

## Client Side

### Account Commands
The two requests below must be made prior to an alarm expiring in order to receive the alarm. If your address or timezone should change, they can be adjusted without loosing your existing timers.

#### set address
##### request
```
{"from":"secret", "type":"set address", "payload":{"address":"tcp://IP4:PORT"}}
```
##### reply
```
{"type":"set address", "payload":{"status":"OK" | "FAILED",
                                     "msg":"error msg" | null}}
```

#### set timezone
##### request
```
{"from":"secret", "type":"set timezone", "payload":{"timezone":integer}}
```
timezone is UTC offset.
##### reply
```
{"type":"set timezone", "payload":{"status":"OK" | "FAILED",
                                      "msg":"error msg" | null}}
```

### Timer Commands

#### echo
##### request
```
{"type":"echo" [, any valid JSON]}
```
##### reply
The request itself will be the reply

#### set timer
##### request
```
{"from":"secret", "type":"set timer", "payload":{"name":"timer name, must be unique to user",
                                                    "time":"/^(?<hour>\d{1,2})?:(?<min>\d{1,2})?:(?<sec>\d{1,2})?:(?<dec>\d{1,6})?$/",
                                                    "payload":JSON}}
```
Time is relative to current time, eg: ":2:" is 2 minutes from now.
##### reply
```
{"type":"set timer", "payload":{"status":"OK" | "FAILED",
                                   "msg":"error msg" | null,
                                   "id":integer | null}}
```

#### set alarm
##### request
```
{"from":"secret", "type":"set alarm", "payload":{"name":"timer name, must be unique to user",
                                                    "date":"/^(?<year>\d{4})?:(?<month>\d{1,2})?:(?<day>\d{1,2})?$/" | null,
                                                    "time":"/^(?<hour>\d{1,2})?:(?<min>\d{1,2})?:(?<sec>\d{1,2})?:(?<dec>\d{1,6})?$/",
                                                    "payload":JSON}}
```
If date is null today is assumed, if a portion of date is missing, todays information is assumed, eg: "::30" is this year this month on the 30th. Unlike in "set timer" here the time is the time of day (not relative to now).

#### cancel

#### del

#### get

#### get active

#### get history

### Alarms

## Host Side

### Requirements
.env in project root with:
```
DBHOST= # the host for the database
DBUSER= # user name to access database
DBPASS= # password to database
DBNAME= # name of database
```

### To run
```
python -m venv ./.venv
source ./.venv/bin/activate
pip -r install requirements.txt
python main.py PORT &
```
