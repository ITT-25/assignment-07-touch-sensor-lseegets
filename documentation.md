# 1. Build a Camera-Based Touch Sensor

## Initial Difficulties

I started working on this assignment using my old laptop, since that was all I had available at the time. I had to use the short USB cable that came with the camera, and when I tried connecting the camera, my laptop would not recognize it. I spent hours thinking the camera or the cable had a loose connection. *Sometimes*, after carefully unplugging and plugging it back in and not moving the camera too much, it would work. Since I couldn't swap the camera, I tried to make do. Later, after switching to my desktop computer, I realized that the issue was not with the camera or the cable. It was my laptop not supplying enough power for the camera to function properly.


## Design Decisions

The USB cable that came with the camera was not long enough to reach inside the carboad box from my laptop. So, I poked a hole through the box to feed the cable through.

In the beginning, I simply placed the camera on the bottom of the box, but later I realized that using the tripod greatly reduced noise since it limited the view to just the sheet of paper. Extending the tripod legs outward to get the camera as close to the ground as possible still maintained a wide enough field of view. Additionally, I taped the piece of paper to the acrylic to keep it from shifting.

Camera inside the box    |  Box covered with acrylic and paper sheets
-------------------------|-------------------------
![](./img/cam.jpg)  |  ![](./img/box.jpg)

To avoid false positives from palms or other large objects, any contact detected at the edges of the camera frame is ignored.

To detect taps, I first tried using different bounding box size thresholds around the fingertip, which was not reliable. I ended up using a time-based approach: when a finger touches the surface, a timer starts, and if the finger is lifted within a certain time threshold, the movement is registered as a tap.

## How To Use

### Prerequisites

**Note**: This program was developed and tested with Python 3.11.x.

- Create and run a virtual environment (on Windows):
    ```
    py -m venv venv
    venv\Scripts\activate
    ```

- Install requirements:

    ```
    pip install -r requirements.txt
    ```

### Usage

To learn about setting up the hardware, please refer to the [Setup](#design-decisions) section.

Run the program with the following commands:

```
py touch_input.py
py fitts_law.py
```

Three windows will open: One pyglet window and two camera preview windows. The two camera windows display the threshold image and the color image with a bounding box drawn around a detected fingertip.

To control the green cursor in the pyglet window, drag your fingertip across the sheet of paper. To select a red target, move the cursor over it and tap your finger on the surface. Once all targets have been hit, log data will be saved to a .csv file.