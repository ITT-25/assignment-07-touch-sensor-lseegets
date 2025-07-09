import pyrealsense2 as rs
import numpy as np
import cv2
import time
from keras.models import load_model
from pynput.keyboard import Controller, Key

label_map = {
    1: 'A',  2: 'B',  3: 'C',  4: 'D',  5: 'E',  6: 'F',  7: 'G',  8: 'H',  9: 'I',  10: 'J',
    11: 'K', 12: 'L', 13: 'M', 14: 'N', 15: 'O', 16: 'P', 17: 'Q', 18: 'R', 19: 'S', 20: 'T',
    21: 'U', 22: 'V', 23: 'W', 24: 'X', 25: 'Y', 26: 'Z'
}

CALIBRATION_TIME = 3    # How long background calibration should be running
MIN_SIZE = 500      # The minimum size of the contour to be recognized as finger
MAX_SIZE = 5000     # The maximum size of the contour to be recognized as finger
TAP_THRESHOLD = 0.15    # The maximum duration a finger can make contact with the surface to be considered a tap
PROCESSING_TIME = 1     # Time until prediction after finger has been lifted off the surface

# Setting up the camera pipeline
pipeline = rs.pipeline()
time.sleep(2)
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

keyboard = Controller()
model = load_model("./letter_recognition.keras")

points = []     # The "drawn" points
prev_point = None   # The previously "drawn" point
clear_canvas_time = None    # Timer to keep track of when the canvas should be cleared
is_tap = True      # Will be set to False if the input turns out not to be a tap


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
    print("Calibration complete")
    return background


try:
    background = get_background(pipeline, CALIBRATION_TIME)
    touch_active = False    # Tracks whether a touch session is currently ongoing (i.e., finger has touched the surface and not released yet)
    touch_start = 0     # Saves the timestamp at the moment of touch
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if color_frame:
            color_image = np.asanyarray(color_frame.get_data())
            height, width = color_image.shape[:2]
            canvas = np.zeros((height, width, 3), np.uint8)
           # canvas = cv2.flip(color_image, 1)
            break

    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue
        color_image = np.asanyarray(color_frame.get_data())
        color_image = cv2.flip(color_image, 1)
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
            center = (x + w // 2, y + h // 2)
            points.append(center)
            if prev_point:
                cv2.line(canvas, prev_point, center, (255, 255, 255), thickness=3)
            prev_point = center

        else:
            prev_point = None

        # Once the surface is being touched, set touch_active = True and start tracking the time
        if finger_detected and not touch_active:
            touch_active = True
            touch_start = time.time()

        # If the finger is not touching the surface anymore and touch_active = True (i.e., the finger is being
        # lifted off the surface, ending the touch), calculate how long the touch lasted
        if not finger_detected and touch_active:
            touch_duration = time.time() - touch_start
            touch_active = False

            # If the touch duration is short enough, consider it a tap and simulate a SPACE key press.
            # Clear the canvas right away to avoid accidental prediction
            if is_tap and touch_duration < TAP_THRESHOLD:
                keyboard.press(Key.space)
                keyboard.release(Key.space)
                canvas[:] = 0
                points.clear()
                prev_point = None
                clear_canvas_time = None
                continue

            # If the touch was not a tap, set clear_canvas_time one second ahead of now
            clear_canvas_time = time.time() + PROCESSING_TIME
            is_tap = False      # Set to False so taps won't get triggered on accident (for example when writing lowercase "i")

        # When that extra second has passed, start the prediction process
        if clear_canvas_time and time.time() >= clear_canvas_time:
            # Convert the input to grayscale
            gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
            writing = cv2.findNonZero(gray_canvas)
            if writing is not None:
                # Get the bounding box of the writing
                x, y, w, h = cv2.boundingRect(writing)
                char = gray_canvas[y:y+h, x:x+w]

                # Create a black square and center the writing inside it (this is to avoid distortion when resizing)
                size = max(w, h)
                square = np.zeros((size, size))
                y_offset = (size - h) // 2
                x_offset = (size - w) // 2
                square[y_offset:y_offset + h, x_offset:x_offset + w] = char
                char = square

                # Resize and prepare the square for model input
                char = cv2.resize(char, (28, 28))
                char = char.astype("float32") / 255.
                char = char.reshape(1, 28, 28, 1)

                # Predict the input
                pred = model.predict(char)
                index = np.argmax(pred)
                predicted_char = label_map[index]

                print("Predicted: ", predicted_char)
                
                # Map the output to the corresponding key
                keyboard.press(predicted_char)
                keyboard.release(predicted_char)

            # Clear the canvas for the next letter
            canvas[:] = 0
            points.clear()
            prev_point = None
            clear_canvas_time = None
            is_tap = True

        frame = cv2.addWeighted(color_image, 1.0, canvas, 1.0, 0)
        cv2.imshow('frame', frame)

        # Wait for a key press and check if it's the 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()