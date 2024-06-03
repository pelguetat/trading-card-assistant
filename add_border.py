import cv2
import numpy as np


def add_measured_border(
    image_path, border_width=50, tick_interval=100, text_color=(0, 0, 0)
):
    """Adds a measured border with x/y axes and tick marks to an image.

    Args:
        image_path: Path to the input image.
        border_width: Width of the border in pixels.
        tick_interval: Distance between tick marks in pixels.
        text_color: BGR color of the text.

    Returns:
        The modified image with the border.
    """

    img = cv2.imread(image_path)
    original_height, original_width = img.shape[:2]

    # Create a canvas for the bordered image
    bordered_img = (
        np.ones(
            (original_height + 2 * border_width, original_width + 2 * border_width, 3),
            dtype=np.uint8,
        )
        * 255
    )  # Make the border white
    bordered_img[border_width:-border_width, border_width:-border_width] = (
        img  # Place original image in the center
    )

    # Add x-axis ticks and labels
    for x in range(0, original_width, tick_interval):
        cv2.line(
            bordered_img,
            (x + border_width, border_width),
            (x + border_width, border_width - 5),
            text_color,
            1,
        )
        cv2.putText(
            bordered_img,
            str(x),
            (x + border_width - 10, border_width - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            text_color,
            1,
        )

    # Add y-axis ticks and labels
    for y in range(0, original_height, tick_interval):
        cv2.line(
            bordered_img,
            (border_width, y + border_width),
            (border_width - 5, y + border_width),
            text_color,
            1,
        )
        cv2.putText(
            bordered_img,
            str(y),
            (border_width - 30, y + border_width + 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            text_color,
            1,
        )

    return bordered_img


# Example Usage:
image_path = "/Users/pabloelgueta/Documents/Screenshot 2024-05-23 at 11.32.53.png"  # Replace with your image path
bordered_image = add_measured_border(image_path)
cv2.imwrite("bordered_image.jpg", bordered_image)  # Save the bordered image
