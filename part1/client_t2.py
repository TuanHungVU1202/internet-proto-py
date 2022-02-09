import json
import socket
import ssl
import time

import certifi

import h2.connection
import h2.events

import constant
import util

SERVER_NAME = 'localhost'
SERVER_PORT = 8443

socket.setdefaulttimeout(25)
# ctx = ssl.create_default_context(cafile=certifi.where())
# ctx.check_hostname = False
# ctx.verify_mode = ssl.CERT_NONE
# ctx.set_alpn_protocols(['h2'])

# open a socket to the server and initiate TLS/SSL
s = socket.create_connection((SERVER_NAME, SERVER_PORT))
# s = ctx.wrap_socket(s, server_hostname=SERVER_NAME)

c = h2.connection.H2Connection()
c.initiate_connection()
s.sendall(c.data_to_send())

headers = [
    (':method', 'GET'),
    (':path', '/espoo'),
    (':authority', constant.SERVER_NAME),
    (':scheme', 'https'),
]
c.send_headers(1, headers, end_stream=True)
s.sendall(c.data_to_send())

body = b''
cache = {}
response_stream_ended = False
while not response_stream_ended:
    # read raw data from the socket
    data = s.recv(65536 * 1024)
    if not data:
        continue

    # feed raw data into h2, and process resulting events
    events = c.receive_data(data)
    for event in events:
        print(f'Got event {type(event)}')
        if isinstance(event, h2.events.DataReceived):
            print(f'Receive data from stream {event.stream_id}')
            # update flow control so the server doesn't starve us
            c.acknowledge_received_data(event.flow_controlled_length, event.stream_id)
            # more response body data received
            body += event.data
        if isinstance(event, h2.events.StreamEnded):
            # response body completed, let's exit the loop
            print(f'Stream {event.stream_id} has finished')
            print("Caching data")
            cache[event.stream_id] = body
            # print(event.stream_id, body.decode())
            response_stream_ended = True
        if isinstance(event, h2.events.PushedStreamReceived):
            print(f'Got server push from stream {event.pushed_stream_id}')
            print("Received PUSH headers: " + str(event.headers))
    # send any pending data to the server
    s.sendall(c.data_to_send())

print("Normal Response - ESPOO map fully received:")
print(cache[1].decode())

time.sleep(5)
print("Entering Helsinki area after 5s. Fetching received Pushed HELSINKI map:")
out = cache[2].decode()
# RAW received data if needed
# print(out)

decoder = json.JSONDecoder()
espoo_map, i = decoder.raw_decode(out)
helsinki_map, _ = decoder.raw_decode(out[i:])
push_response_json = json.dumps(helsinki_map)
helsinki_map_json = json.loads(push_response_json)
print(helsinki_map_json['push_body'])


# tell the server we are closing the h2 connection
c.close_connection()
s.sendall(c.data_to_send())

# close the socket
s.close()