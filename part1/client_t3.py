import json
import socket

import h2.connection
import h2.events

import constant
import util

socket.setdefaulttimeout(25)

# open a socket to the server and initiate TLS/SSL
s = socket.create_connection((constant.SERVER_NAME, constant.PORT))
# s = ctx.wrap_socket(s, server_hostname=SERVER_NAME)

c = h2.connection.H2Connection()
c.initiate_connection()
s.sendall(c.data_to_send())

uri = '/sendimage'
headers = [
    (':method', 'POST'),
    (':path', uri),
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
            cache[event.stream_id] = body
            response_stream_ended = True
        if isinstance(event, h2.events.PushedStreamReceived):
            print(f'Got server push from stream {event.pushed_stream_id}')
            print("Received PUSH headers: " + str(event.headers))
    # send any pending data to the server
    s.sendall(c.data_to_send())

print("Response from server")


# tell the server we are closing the h2 connection
c.close_connection()
s.sendall(c.data_to_send())

# close the socket
s.close()