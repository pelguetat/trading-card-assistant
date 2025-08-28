import subprocess as sp
import numpy as np
import cv2

command = [
    "ffmpeg",
    "-rtsp_transport",
    "tcp",
    "-i",
    "rtsp://192.168.0.21:8080/h264.sdp",
    "-f",
    "rawvideo",
    "-pix_fmt",
    "yuv420p",
    "-vcodec",
    "rawvideo",
    "-vsync",
    "1",
    "-r",
    "30",  # Match source 30fps
    "-bufsize",
    "18M",  # Match source bitrate
    "-maxrate",
    "18M",
    "-",
]

# Calculate buffer size for YUV420p format
# YUV420p uses 12 bits per pixel (1.5 bytes)
width, height = 1920, 1080  # Changed from 4K to 1080p
frame_size = width * height * 3 // 2  # For YUV420p

pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, bufsize=10**8)

while True:
    # Read YUV420p frame
    raw_image = pipe.stdout.read(frame_size)

    if not raw_image:
        stderr = pipe.stderr.read()
        print(f"No frame data received. FFmpeg error: {stderr.decode()}")
        continue

    try:
        # Convert YUV420p to BGR
        frame = np.frombuffer(raw_image, dtype=np.uint8)
        yuv = frame.reshape((height * 3 // 2, width))

        # Convert YUV420p to BGR
        bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)

        cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
        cv2.imshow("frame", bgr)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    except Exception as e:
        print(f"Frame processing error: {e}")
        continue

pipe.terminate()
cv2.destroyAllWindows()
