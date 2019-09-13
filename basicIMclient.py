import socket
import select
import sys
import instantmessage_pb2
import argparse
import struct

if __name__ == "__main__":
    # Code from tutorial
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', dest='servername', help='your client\'s hostname', required=True)
    parser.add_argument('-n', dest='nickname', help='your nickname', required=True)
    args = parser.parse_args()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((args.servername, 9999))

    read_handles = [sys.stdin, client_socket]
    try:
        while True:
            read_list, _, _ = select.select(read_handles, [], [])

            for s in read_list:
                # Receive message from server
                if s == client_socket:
                    total_length = 0
                    while total_length < 4:
                        message_length = s.recv(4)
                        total_length += len(message_length)
                    if message_length:
                        data = ''
                        message_length = struct.unpack('>I', message_length)[0]
                        data_length = 0
                        while data_length < message_length:
                            chunk = s.recv(8192).decode()
                            if not chunk:
                                data = None
                                break
                            else:
                                data += chunk
                                data_length += len(chunk)
                        instant_message = instantmessage_pb2.InstantMessage()
                        instant_message.ParseFromString(data.encode())
                        print("%s: %s\n" % (instant_message.nickname, instant_message.msg), flush=True)
                # Client input from keyboard
                else:
                    message = sys.stdin.readline()
                    # Client exit the chat room by input exit or Exit or eXit ...
                    if message.strip().lower() == 'exit':
                        client_socket.close()
                        sys.exit()
                    # Client input message and we serialize it and then send it to server
                    else:
                        instant_message = instantmessage_pb2.InstantMessage()
                        instant_message.nickname = args.nickname
                        instant_message.msg = message.strip()
                        msg = instant_message.SerializeToString()
                        client_socket.sendall(struct.pack('>I', len(msg)) + msg)
    except KeyboardInterrupt:
        client_socket.close()
        sys.exit()

