import base64
import responses


def get_encoded_value(value):
    return base64.b64encode(value.encode('ascii')).decode('ascii')


CONSUL_DUMMY_RESPONSE = {
    "LockIndex": 0,
    "Key": "my_variable",
    "Flags": 0,
    "Value": get_encoded_value('foo'),
    "CreateIndex": 924,
    "ModifyIndex": 924
}

CONSUL_DUMMY_RESPONSE_LEVELED = {
    "LockIndex": 0,
    "Key": "my_service/my_variable",
    "Flags": 0,
    "Value": get_encoded_value('foo'),
    "CreateIndex": 924,
    "ModifyIndex": 924
}


CONSUL_DUMMY_RESPONSES_NAMESPACED = [
    {
        "LockIndex": 0,
        "Key": "MYAPP/my_string_0",
        "Flags": 0,
        "Value": get_encoded_value('foo'),
        "CreateIndex": 924,
        "ModifyIndex": 924
    },
    {
        "LockIndex": 0,
        "Key": "MYAPP/my_string_1",
        "Flags": 0,
        "Value": get_encoded_value('bar'),
        "CreateIndex": 924,
        "ModifyIndex": 924
    },
    {
        "LockIndex": 0,
        "Key": "MYAPP/my_int",
        "Flags": 0,
        "Value": get_encoded_value('1'),
        "CreateIndex": 924,
        "ModifyIndex": 924
    },
    {
        "LockIndex": 0,
        "Key": "MYAPP/my_bool",
        "Flags": 0,
        "Value": get_encoded_value('false'),
        "CreateIndex": 924,
        "ModifyIndex": 924
    }
]

def make_namespaced_responses():
    responses.add(
        responses.GET,
        'http://foobar:8500/v1/kv/MYAPP/my_string_0',
        json=[CONSUL_DUMMY_RESPONSES_NAMESPACED[0]],
        headers={'X-Consul-Index': '924'},
        status=200
    )
    responses.add(
        responses.GET,
        'http://foobar:8500/v1/kv/MYAPP/my_string_1',
        json=[CONSUL_DUMMY_RESPONSES_NAMESPACED[1]],
        headers={'X-Consul-Index': '924'},
        status=200
    )
    responses.add(
        responses.GET,
        'http://foobar:8500/v1/kv/MYAPP/my_int',
        json=[CONSUL_DUMMY_RESPONSES_NAMESPACED[2]],
        headers={'X-Consul-Index': '924'},
        status=200
    )
    responses.add(
        responses.GET,
        'http://foobar:8500/v1/kv/MYAPP/my_bool',
        json=[CONSUL_DUMMY_RESPONSES_NAMESPACED[3]],
        headers={'X-Consul-Index': '924'},
        status=200
    )
