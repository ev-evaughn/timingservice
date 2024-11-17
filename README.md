# timingservice

## Client Side

### Account Commands
The two requests below must be made prior to an alarm expiring in order to receive the alarm. If your address or timezone should change, they can be adjusted without loosing your existing timers.

#### set address:
##### request
```
{"from":"secret", "type":"set address", "payload":{"address":"tcp://IP4:PORT"}}
```
##### reply
```
{"type":"set address", "payload":{"status":"OK" | "FAILED",
                                  "msg":"error msg" | null}}
```

#### set timezone:
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

#### echo:
##### request
```
{"type":"echo" [, any valid JSON]}
```
##### reply
The request itself will be the reply

#### set timer:
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

#### set alarm:
##### request
```
{"from":"secret", "type":"set alarm", "payload":{"name":"timer name, must be unique to user",
                                                 "date":"/^(?<year>\d{4})?:(?<month>\d{1,2})?:(?<day>\d{1,2})?$/" | null,
                                                 "time":"/^(?<hour>\d{1,2})?:(?<min>\d{1,2})?:(?<sec>\d{1,2})?:(?<dec>\d{1,6})?$/",
                                                 "payload":JSON}}
```
If date is null today is assumed, if a portion of date is missing, todays information is assumed, eg: "::30" is this year this month on the 30th. Unlike in "set timer" here the time is the time of day (not relative to now).
##### reply
```
{"type":"set alarm", "payload":{"status":"OK" | "FAILED",
                                "msg":"error msg" | null,
                                "id":integer | null}}
```

#### cancel:
##### request
```
{"from":"secret", "type":"cancel", "payload":{"id":integer}}
```
##### reply
```
{"type":"cancel", "payload":{"status:"OK" | "FAILED",
                             "msg":"error msg" | null,
                             "id":integer}}
```
The id is the id of the timer that was requested to be cancelled.  

#### del:
##### request
```
{"from":"secret", "type":"del", "payload":{"id":integer}}
```
##### reply
```
{"type":"del", "payload":{"status":"OK" | "FAILED",
                          "msg":"error msg" | null,
                          "id":integer}}
```
The id is the id of the timer that was requested to be deleted.

#### get:
##### request
```
{"from":"secret", "type":"get", "payload":{"id":integer}}
```
##### reply
```
{"type":"get", "payload":{"status":"OK" | "FAILED",
                          "msg":"error msg" | null,
                          "id":integer,
                          "payload":JSON | null}}
```

#### get ids:
##### request
```
{"from":"secret", "type":"get ids"}
```
##### reply
```
{"type":"get ids", "payload":{"status":"OK" | "FAILED",
                              "msg":"error msg" | null,
                              "active ids":[],
                              "history ids":[]}}
```
If there are aren't any acitive or historical ids, the lists will be empty, otherwise they will be filled with integers.

#### get active:
##### request
```
{"from":"secret", "type":"get active", "payload":{"limit":integer | null,
                                                  "start: integer | nulll}
                                                  | null}
```
limit the number of returns with "limit" and use "start" set where the returns start, eg: {"limit":1, "start":0} will get the next alarm to expire (if there is one). If start is null, 0 is assumed, if limit is null all will be returned.
##### reply
```
{"type":"get active", "payload":{"status":"OK" | "FAILED",
                                 "msg":"error msg" | null,
                                 "actives":[{"id":integer, "date":"YYYY-MM-DD", "time":"HH:MM:SS.FFFFFF", "payload":JSON}]}}
```

#### get history:
##### request
```
{"from":"secret", "type":"get history", "payload":{"limit":integer | null,
                                                   "start:integer | null}
                                                   | null}
```
##### reply
```
{"type":"get history", "payload":{"status":"OK" | "FAILED",
                                    "msg":"error msg" | null,
                                    "histories":[{"id":integer, "date":"YYYY-MM-DD", "time":"HH:MM:SS.FFFFFF", "payload";JSON, "ack":"YYYY-MM-DD HH:MM:SS.FFFFFF" | null}]}}
```
Cancelled and Acked timers will appear in the history, deleted alarms have been deleted from the database.

### Alarms
When the time somes the following request will be made to address you have set:
##### request
```
{"id":integer, "payload":JSON}
```
##### reply
please make the following reply so that the ack time can be set
```
{"id":integer}
```
Where the integer matches the integer in the request, which is the id of the alarm that has expired.

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
