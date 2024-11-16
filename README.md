# timingservice

## Client Side

### Account Commands
The two requests below must be made prior to an alarm expiring in order to receive the alarm. If your address or timezone should change, they can be adjusted without loosing your existing timers.

#### set address
##### request
```{"from":"secret", "type":"set address", "payload":{"address":"tcp://IP4:PORT"}}```
##### reply
```{"type":"set address", "payload":{"status":"OK" | "FAILED",
                                     "msg":"error msg" | null}}```

#### set timezone
##### request
```{"from":"secret", "type":"set timezone", "payload":{"timezone":integer}}```
timezone is UTC offset.
##### reply
```{"type":"set timezone", "payload":{"status":"OK" | "FAILED",
                                      "msg":"error msg" | null}}```

### Timer Commands

#### echo
##### request
```{"type":"echo" [, any valid JSON]}```
##### reply
The request itself will be the reply

#### set timer
##### request
```{"from":"secret", "type":"set timer", "payload":{"name":"timer name, must be unique to user",
                                                    "time":"/^(?<hour>\d{1,2})?:(?<min>\d{1,2})?:(?<sec>\d{1,2})?:(?<dec>\d{1,6})?$/",
                                                    "payload":JSON}}```
##### reply
```{"type":"set timer", "payload":{"status":"OK" | "FAILED",
                                   "msg":"error msg" | null,
                                   "id":integer | null}}```

#### set alarm

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
