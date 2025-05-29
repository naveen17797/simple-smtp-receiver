import socket

SERVER = '127.0.0.1'
PORT = 2525


def send(sock, line):
    print(f"CLIENT SENDING: {line}")
    sock.sendall((line + '\r\n').encode())


def recv(sock):
    resp = sock.recv(1024).decode().strip()
    print(f"SERVER SENT: {resp}")
    return resp


def main():
    print("Simple SMTP CLI Client")

    from_addr = "a@gmail.com"
    to_addr = "b@b.com"
    subject = "foo"

    body = "test"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER, PORT))

        recv(sock)  # 220 greeting

        send(sock, "HELO client.local")
        recv(sock)

        send(sock, f"MAIL FROM:<{from_addr}>")
        recv(sock)

        send(sock, f"RCPT TO:<{to_addr}>")
        recv(sock)

        send(sock, "DATA")
        recv(sock)

        send(sock, f"Subject: {subject}")
        send(sock, "\n")
        send(sock, f"{body}")
        send(sock, ".")
        recv(sock)

        send(sock, "QUIT")
        recv(sock)


if __name__ == "__main__":
    main()
