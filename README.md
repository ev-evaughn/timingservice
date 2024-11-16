# timingservice

## Client Side

### Account Commands

#### set address
##### request
```{"from":"secret", "type":"set address", "payload":{"address":"tcp://IP4:PORT"}}```
##### reply
```{"type":"set address", "payload":{"status":"OK" | "FAILED", "msg":"error msg" | null}}```

#### set timezone

### Timer Commands

#### echo

#### set timer

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
