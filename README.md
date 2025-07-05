[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/BegzSP5S)

# 1. Build a Camera-Based Touch Sensor

## Quick Guide

For a more detailed description, please refer to the *documentation.md* file.

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

Run the program with the following commands:

```
py touch_input.py
py fitts_law.py
```

Three windows will open: One pyglet window and two camera preview windows. Unless you are interested in thresholding and finger detection, you can ignore the camera windows.

To control the green cursor in the pyglet window, drag your fingertip across the sheet of paper. To select a red target, move the cursor over it and tap your finger on the surface. Once all targets have been hit, log data will be saved to a .csv file.