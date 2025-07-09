[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/BegzSP5S)

# Prerequisites

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
# Quick Guide

For a more detailed description, please refer to the *documentation.md* file.

## 1. Build a Camera-Based Touch Sensor

Run the program with the following commands:

```
py touch_input.py
py fitts_law.py [num_targets] [width] [distance] [id]   # Replace with actual values
```

Three windows will open: one pyglet window and two camera preview windows. Unless you are interested in thresholding and finger detection, you can ignore the camera windows.

To control the green cursor in the pyglet window, drag your fingertip across the sheet of paper. To select a red target, move the cursor over it and tap your finger on the surface. Once all targets have been hit, log data will be saved to a .csv file.

To close the preview windows, press the **Q** key. To exit the pyglet window, click the **X** button.

## 2. Touch-based Text Input

Run the program with the following commands:

```
cd text_input
py touch_input.py
```

A camera preview window will open. Drag your fingerpad over the surface. Your strokes will appear in white in the preview window. After you finish writing a character, pause for one second without touching the surface. The character will then be recognized and typed automatically. After that, you can proceed with the next character. Briefly tapping your finger on the surface once will simulate a **SPACE** keystroke.

To end the program, press the **Q** key.