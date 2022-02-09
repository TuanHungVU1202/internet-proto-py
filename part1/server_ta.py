import asyncio
import io
import json
import re
import ssl
import collections
from typing import List, Tuple

from h2.config import H2Configuration
from h2.connection import H2Connection
from h2.events import (
    ConnectionTerminated, DataReceived, RemoteSettingsChanged,
    RequestReceived, StreamEnded, StreamReset, WindowUpdated
)
from h2.errors import ErrorCodes
from h2.exceptions import ProtocolError, StreamClosedError
from h2.settings import SettingCodes

import constant
import util

RequestData = collections.namedtuple('RequestData', ['headers', 'data'])


class H2Protocol(asyncio.Protocol):
    def __init__(self):
        config = H2Configuration(client_side=False, header_encoding='utf-8')
        self.conn: H2Connection = H2Connection(config=config)
        self.transport = None
        self.stream_data = {}
        self.flow_control_futures = {}

    def connection_made(self, transport: asyncio.Transport):
        self.transport = transport
        self.conn.initiate_connection()
        self.transport.write(self.conn.data_to_send())

    def connection_lost(self, exc):
        for future in self.flow_control_futures.values():
            future.cancel()
        self.flow_control_futures = {}

    def data_received(self, data: bytes):
        try:
            events = self.conn.receive_data(data)
        except ProtocolError as e:
            self.transport.write(self.conn.data_to_send())
            self.transport.close()
        else:
            self.transport.write(self.conn.data_to_send())
            for event in events:
                print(f'Got event {type(event)}')
                if isinstance(event, RequestReceived):
                    self.request_received(event.headers, event.stream_id)
                    print(event.headers)
                elif isinstance(event, DataReceived):
                    self.receive_data(event.data, event.stream_id)
                elif isinstance(event, StreamEnded):
                    self.stream_complete(event.stream_id)
                elif isinstance(event, ConnectionTerminated):
                    self.transport.close()
                elif isinstance(event, StreamReset):
                    self.stream_reset(event.stream_id)
                elif isinstance(event, WindowUpdated):
                    self.window_updated(event.stream_id, event.delta)
                elif isinstance(event, RemoteSettingsChanged):
                    if SettingCodes.INITIAL_WINDOW_SIZE in event.changed_settings:
                        self.window_updated(None, 0)
                self.transport.write(self.conn.data_to_send())

    def request_received(self, headers: List[Tuple[str, str]], stream_id: int):
        headers = collections.OrderedDict(headers)
        method = headers[':method']
        request_data = RequestData(headers, io.BytesIO())
        self.stream_data[stream_id] = request_data

    def stream_complete(self, stream_id: int):
        try:
            request_data = self.stream_data[stream_id]
        except KeyError:
            return
        method = request_data.headers[':method']
        path = request_data.headers[':path']
        # Part 1 - Topic 2
        if method == "GET" and re.search("^/route", path):
            print("entering route")
            self.defined_route_received(stream_id, request_data)


    def receive_data(self, data: bytes, stream_id: int):
        try:
            stream_data = self.stream_data[stream_id]
        except KeyError:
            self.conn.reset_stream(
                stream_id, error_code=ErrorCodes.PROTOCOL_ERROR
            )
        else:
            stream_data.data.write(data)

    def stream_reset(self, stream_id):
        if stream_id in self.flow_control_futures:
            future = self.flow_control_futures.pop(stream_id)
            future.cancel()

    async def send_data(self, data, stream_id):
        while data:
            while self.conn.local_flow_control_window(stream_id) < 1:
                try:
                    await self.wait_for_flow_control(stream_id)
                except asyncio.CancelledError:
                    return

            chunk_size = min(
                self.conn.local_flow_control_window(stream_id),
                len(data),
                self.conn.max_outbound_frame_size,
            )

            try:
                self.conn.send_data(
                    stream_id,
                    data[:chunk_size],
                    end_stream=(chunk_size == len(data))
                )
            except (StreamClosedError, ProtocolError):
                break

            self.transport.write(self.conn.data_to_send())
            data = data[chunk_size:]

    async def wait_for_flow_control(self, stream_id):
        f = asyncio.Future()
        self.flow_control_futures[stream_id] = f
        await f

    def window_updated(self, stream_id, delta):
        if stream_id and stream_id in self.flow_control_futures:
            f = self.flow_control_futures.pop(stream_id)
            f.set_result(delta)
        elif not stream_id:
            for f in self.flow_control_futures.values():
                f.set_result(delta)

            self.flow_control_futures = {}

    def defined_route_received(self, stream_id, request_data):
        espoo_map = util.parse_json_file(constant.ESPOO_MAP_PATH)
        headers = request_data.headers
        # body = request_data.data.getvalue().decode('utf-8')
        data = json.dumps(
            {"headers": headers, "body": espoo_map}, indent=4
        ).encode("utf8")

        response_headers = (
            (':status', '200'),
            ('content-type', 'application/json'),
            ('content-length', str(len(data))),
            ('server', constant.SERVER_NAME),
        )
        self.conn.send_headers(stream_id, response_headers)
        asyncio.ensure_future(self.send_data(data, stream_id))
        print(f'Sent response to stream {stream_id}')

        # Server push
        helsinki_map = util.parse_json_file(constant.HELSINKI_MAP_PATH)
        push_headers = [
            (':method', 'GET'),
            (':path', '/helsinki'),
            (':scheme', 'https'),
            (':authority', constant.SERVER_NAME),
        ]
        pushed_stream_id = self.conn.get_next_available_stream_id()
        self.conn.push_stream(stream_id, pushed_stream_id, push_headers)

        push_data = json.dumps(
            {"push_headers": headers, "push_body": helsinki_map}, indent=4
        ).encode("utf8")
        res_headers = (
            (':status', '200'),
            ('content-type', 'application/json'),
            ('server', constant.SERVER_NAME),
        )

        self.conn.send_headers(pushed_stream_id, res_headers)
        asyncio.ensure_future(self.send_data(push_data, pushed_stream_id))
        print(f'Sent server push to stream {pushed_stream_id}')


def main():
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.options |= (
            ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_COMPRESSION
    )
    # ssl_context.load_cert_chain(certfile="cert.crt", keyfile="cert.key")
    # ssl_context.set_alpn_protocols(["h2"])

    loop = asyncio.get_event_loop()
    coro = loop.create_server(H2Protocol, '127.0.0.1', 8443)
    server = loop.run_until_complete(coro)

    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == '__main__':
    main()
