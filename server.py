import socket

from validation import get_spf_records, is_ip_authorized

HOST = '127.0.0.1'
PORT = 2525
MAILBOX_FILE = 'mailbox.txt'

def send(conn, response):
    conn.sendall((response + '\r\n').encode())

def receive_line(conn, buffer):
    while b'\r\n' not in buffer:
        data = conn.recv(1024)
        if not data:
            return None, buffer
        buffer += data
    line, sep, rest = buffer.partition(b'\r\n')
    return line.decode(), rest


def save_email(sender, recipients, message_lines):
    with open(MAILBOX_FILE, 'a') as f:
        f.write(f"From: {sender or 'unknown'}\n")
        f.write(f"To: {', '.join(recipients) or 'unknown'}\n")
        f.write("Message:\n")
        f.write("\n".join(message_lines) + "\n")
        f.write("=" * 40 + "\n")

def handle_smtp(conn):
    send(conn, "220 MinimalSMTP Ready")

    sender = ''
    recipients = []
    message_lines = []
    data_mode = False
    buffer = b""
    while True:
        line, buffer = receive_line(conn, buffer)
        if not line:
            break

        print(f"Client: {line}")

        if data_mode:
            print("Data mode turned on, receiving subject.")
            print(f"line: {line}")
            if line == ".":
                save_email(sender, recipients, message_lines)
                send(conn, "250 OK")
                data_mode = False
                message_lines.clear()
            else:
                message_lines.append(line)
            continue

        if line.upper().startswith("MAIL FROM:"):
            sender = line[10:].strip().strip('<>')
            validate_spf(conn, sender)
        elif line.upper().startswith("RCPT TO:"):
            recipients.append(line[8:].strip())
            send(conn, "250 OK")

        elif line.upper() == "DATA":
            send(conn, "354 End with . on a line")
            data_mode = True

        elif line.upper() == "QUIT":
            send(conn, "221 Bye")
            break

        else:
            send(conn, "250 OK")  # Just acknowledge everything else


def validate_spf(conn, sender):
    sender_domain = sender.split('@')[-1]
    peer_ip = conn.getpeername()[0]
    print(sender_domain, peer_ip)
    auth_result = is_ip_authorized(sender_domain, peer_ip)
    print("Auth result:", auth_result)
    if auth_result is True:
        send(conn, "250 OK")
    elif auth_result is False:
        send(conn, "550 5.7.1 SPF check failed: unauthorized sender IP")
        conn.close()
    else:  # auth_result is None (e.g., DNS failure)
        send(conn, "451 4.3.0 Temporary DNS failure while checking SPF")
        conn.close()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(1)
        print(f"SMTP server running on {HOST}:{PORT}")
        conn, addr = server.accept()
        print(f"Connection from {addr}")
        with conn:
            handle_smtp(conn)

if __name__ == "__main__":
    main()