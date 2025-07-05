import pyrealsense2 as rs
import numpy as np
import cv2
import time
import socket
import json

IP = '127.0.0.1'
PORT = 5700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

CALIBRATION_TIME = 3    # How long background calibration should be running
MIN_SIZE = 500      # The minimum size of the contour to be recognized as finger
MAX_SIZE = 5000     # The maximum size of the contour to be recognized as finger
TAP_THRESHOLD = 0.15    # The maximum duration a finger can make contact with the surface to be considered a tap

pipeline = rs.pipeline()
time.sleep(2)
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)


# Background calibration
def get_background(pipeline, calibration_time):
    print("Calibrating. Make sure to keep the surface clear")
    bg_frames = []
    start = time.time()
    now = time.time()
    # During the calibration period, store the grayscale frames in an array
    while now - start < calibration_time:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if color_frame:
            color_image = np.asanyarray(color_frame.get_data())
            gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
            bg_frames.append(gray)
        now = time.time()
    # Average the frames to create a clean background image
    background = np.mean(bg_frames, axis=0).astype(np.uint8)
    print("Calibration done")
    return background


try:
    background = get_background(pipeline, CALIBRATION_TIME)
    touch_active = False    # Tracks whether a touch session is currently ongoing (i.e., finger has touched the surface and not released yet)
    touch_start = 0     # Saves the timestamp at the moment of touch
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue

        color_image = np.asanyarray(color_frame.get_data())
        # color_image = cv2.flip(color_image, 0)
        height, width = color_image.shape[:2]
        gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(gray, background)
        _, thresh = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        finger_detected = False     # Tracks whether a finger is touching the surface in the current frame
        active_contour = None     # The contour of the active finger

        # If a contour has the right size and is within bounds, consider it the tip of a finger and set it as the active contour
        for contour in contours:
            area = cv2.contourArea(contour)
            if MIN_SIZE < area < MAX_SIZE:
                x, y, w, h = cv2.boundingRect(contour)
                if 0 < x < width - w and 0 < y < height - h:
                    active_contour = contour
                    break

        # If an active contour exists, send movement data (also, draw the bounding box for visualization)
        if active_contour is not None:
            finger_detected = True
            x, y, w, h = cv2.boundingRect(active_contour)
            cv2.rectangle(color_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            message = json.dumps({"movement": {"x": x, "y": y}})
            sock.sendto(message.encode(), (IP, PORT))

        # Once the surface is being touched, set touch_active = True and start tracking the time
        if finger_detected and not touch_active:
            touch_active = True
            touch_start = time.time()

        # If the finger is not touching the surface anymore and touch_active = True (i.e., the finger is being
        # lifted off the surface after a touch session), calculate how long the touch lasted
        if not finger_detected and touch_active:
            touch_duration = time.time() - touch_start
            touch_active = False

            # If the touch duration is short enough, consider it a tap
            if touch_duration < TAP_THRESHOLD:
                message = json.dumps({"tap": 1})
                sock.sendto(message.encode(), (IP, PORT))
                time.sleep(0.2)
                message = json.dumps({"tap": 0})
                sock.sendto(message.encode(), (IP, PORT))


        cv2.imshow('frame', color_image)
        cv2.imshow('threshold', thresh)

        # Wait for a key press and check if it's the 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()