import threading
from queue import Queue
import cv2
import time


class RTSPStream:
    def __init__(self, url):
        self.cap = cv2.VideoCapture(url)
        self.q = Queue(maxsize=1)  # Only keep latest frame
        self.stop_flag = False

    def start(self):
        thread = threading.Thread(target=self._reader)
        thread.daemon = True
        thread.start()

    def _reader(self):
        while not self.stop_flag:
            ret, frame = self.cap.read()
            if not ret:
                continue
            if not self.q.empty():
                try:
                    self.q.get_nowait()  # Discard old frame
                except Queue.Empty:
                    pass
            self.q.put(frame)

    def read(self):
        return self.q.get()

    def stop(self):
        self.stop_flag = True
        self.cap.release()


stream = RTSPStream("rtsp://192.168.0.21:8080/h264.sdp")
stream.start()

while True:
    frame = stream.read()
    cv2.imshow("frame", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

stream.stop()
cv2.destroyAllWindows()
