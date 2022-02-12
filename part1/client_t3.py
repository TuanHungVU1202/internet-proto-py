import asyncio
import json
import socket

import h2.connection
import h2.events
from h2.exceptions import StreamClosedError, ProtocolError

import constant
import util


# HANDLE RESPONSE
#############################################
def handle_response(c, s):
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
    print(cache[1].decode())


def send_request(c, s):
    # Sending REQUESTS
    #############################################
    uri = '/sendimage'
    headers = [
        (':method', 'POST'),
        (':path', uri),
        (':authority', constant.SERVER_NAME),
        (':scheme', 'https'),
    ]

    # Convert image to b64 here
    # Send along with the coordinates
    imageb64 = util.get_serialized_img(constant.IMAGE_1)
    # print(c.DEFAULT_MAX_OUTBOUND_FRAME_SIZE)
    lat = 'lat12'
    long = 'long23'
    data = json.dumps(
        {"headers": headers, "image": imageb64, "lat": lat, "long": long}, indent=4
    ).encode("utf8")

    stream_id = 1
    end_stream = False
    c.send_headers(stream_id, headers, end_stream=end_stream)
    send_data2(s, c, data, stream_id)


def send_data2(s: socket.socket, c: h2.connection.H2Connection, data, stream_id: int):
    if not data:
        c.end_stream(stream_id)

    while len(data) > 0:
        window_size = c.local_flow_control_window(stream_id)
        max_frame_size = c.max_outbound_frame_size

        while window_size < 1:
            print("win size: " + str(window_size))
            received_data = s.recv(65536)
            if not received_data:
                break
            events = c.receive_data(received_data)
            for event in events:
                if isinstance(event, h2.events.WindowUpdated):
                    window_size = c.local_flow_control_window(stream_id)
            s.sendall(c.data_to_send())
        chunk_size = min(window_size, len(data), max_frame_size)
        end_stream = chunk_size >= len(data)
        print(chunk_size)
        print(len(data))
        c.send_data(stream_id, data[:chunk_size], end_stream)
        data = data[chunk_size:]


# def send_data(c, s, data, stream_id):
#     flow_control_futures = {}
#     while data:
#         while c.local_flow_control_window(stream_id) < 1:
#             try:
#                 wait_for_flow_control(stream_id, flow_control_futures)
#             except asyncio.CancelledError:
#                 return
#
#         chunk_size = min(
#             c.local_flow_control_window(stream_id),
#             len(data),
#             c.max_outbound_frame_size,
#         )
#
#         try:
#             c.send_data(
#                 stream_id,
#                 data[:chunk_size],
#                 end_stream=(chunk_size == len(data))
#             )
#         except (StreamClosedError, ProtocolError):
#             break
#
#         s.sendall(c.data_to_send())
#         data = data[chunk_size:]
#
#     print("END")
#
#
# async def wait_for_flow_control(stream_id, flow_control_futures):
#     f = asyncio.Future()
#     flow_control_futures[stream_id] = f
#     await f


def main():
    socket.setdefaulttimeout(25)

    # open a socket to the server and initiate TLS/SSL
    s = socket.create_connection((constant.SERVER_NAME, constant.PORT))
    # s = ctx.wrap_socket(s, server_hostname=SERVER_NAME)

    c = h2.connection.H2Connection()
    c.initiate_connection()
    s.sendall(c.data_to_send())
    #############################################

    # Send request
    send_request(c, s)
    # handle response
    # handle_response(c, s)
    # tell the server we are closing the h2 connection
    c.close_connection()
    s.sendall(c.data_to_send())
    # close the socket
    s.close()


if __name__ == '__main__':
    main()
