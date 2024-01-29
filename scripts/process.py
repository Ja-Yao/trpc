from trpc import TRPCProcessor
import socket


def handle_close(p: TRPCProcessor, s: socket.socket):
    p.close()
    s.close()


if __name__ == "__main__":
    classes = {0: "Hand Open", 1: "Hand Close", 2: "No Movement", 3: "Wrist Extension", 4: "Wrist Flexion"}
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 12346))
    processor = TRPCProcessor()
    try:
        processor.run()
        while True:
            data, addr = sock.recvfrom(1024)  # Receive up to 1024 bytes
            gesture_class, prob = data.decode().split()  # Decode the received bytes
            try:
                print({"class": classes[int(gesture_class)], "confidence": f"{round(float(prob) * 100, 2)}%"})
            except KeyError:
                print({"class": "Unknown", "confidence": f"{round(float(prob) * 100, 2)}%"})
    except KeyboardInterrupt:
        handle_close(processor, sock)