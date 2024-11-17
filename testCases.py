import socket

baseCases = [
    {"from":"testing", "type":"set address", "payload":{
        "address":f'tcp://{socket.gethostname()}:12345'
    }},
    {"from":"testing", "type":"get address"},
    {"from":"testing", "type":"set timezone", "payload":{
        "timezone":-8
    }},
    {"from":"testing", "type":"get timezone"
    },
    {"type":"echo"
    },
    {"from":"testing", "type":"set timer", "payload":{
        "name":"timer one", "time":"::2", "payload":{"test":0}
    }},
    {"from":"testing", "type":"set alarm", "payload":{
        "name":"timer two", "datetime":"2024-12-25 05:00:00",
        "payload":{"msg":"merry xmas"}
    }},
    {"from":"testing", "type":"set alarm", "payload":{
        "name":"timer three", "datetime":"2023-7-4 12:00:00",
        "payload":{"msg":"hotdogs"}
    }},
    {"from":"testing", "type":"get ids"
    },
    {"from":"testing", "type":"get active",
    },
    {"from":"testing", "type":"get active", "payload":{
        "limit":1, "start":1
    }},
    {"from":"testing", "type":"get history", "payload":{}
    },
    {"from":"testing", "type":"set timer", "payload":{
        "name":"one second", "time":"::1",
        "payload":{"something":"here"}
    }},
    {"from":"testing", "type":"set timer", "payload":{
        "name":"two seconds", "time":"::2",
        "payload":{"something":"there"}
    }}
]

interCases = [
  '{"from":"testing", "type":"cancel", "payload":{"id":{}}}',
  '{"from":"testing", "type":"del", "payload":{"id":{}}}',
  '{"from":"testing", "type":"get", "payload":{"id":{}}}'
]