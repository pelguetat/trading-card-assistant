import multiprocessing
import threading
import core.identify_cards_world as main_script
import queue
from multiprocessing import Pool, Process, Queue, Event
from core.langgraph_main import langgraph_start
from dotenv import load_dotenv
import os
import tkinter as tk
import logging
from core.audio_commands import process_audio_commands
from PIL import Image, ImageTk

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Pokemon Trainer"

# Global flag to signal threads to terminate
terminate_flag = ""


def main():
    logging.info("Starting main function")
    frame_queue = multiprocessing.Queue()

    video_process = Process(target=main_script.process_video, args=(frame_queue,))
    video_process.start()
    logging.info("Video process started")
    # Create a simple Tkinter window with a button
    global root
    root = tk.Tk()
    root.title("LangGraph Starter")
    logging.info("Tkinter window created")

    # Create a frame to hold the video and button
    main_frame = tk.Frame(root)
    main_frame.pack()

    video_label = tk.Label(main_frame)
    video_label.pack()


    def on_button_click():
        logging.info("Start LangGraph button clicked")
        langgraph_process = Process(
            target=langgraph_start, args=(frame_queue,)
        )
        langgraph_process.start()
        logging.info("LangGraph process started")


    start_button = tk.Button(
        main_frame, text="Start LangGraph", command=on_button_click
    )
    start_button.pack(pady=20)

    # Create a canvas to display the video frames
    canvas = tk.Canvas(main_frame, width=1280, height=720)
    canvas.pack()

    def update_frame():
        if not frame_queue.empty():
            data = frame_queue.get()
            if data is None:
                return
            frame, _, _, _ = data
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            canvas.imgtk = imgtk  # Keep a reference to avoid garbage collection
        root.after(30, update_frame)  # Schedule the next frame update

    update_frame()  # Start the frame update loop

    # Create and start a thread for process_audio_commands
    audio_process = Process(
        target=process_audio_commands,
        args=(frame_queue,),
    )
    audio_process.start()
    logging.info("Audio commands process started")


    def on_closing():
        logging.info("Closing application")
        terminate_flag.set()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Run the Tkinter event loop
    root.mainloop()
    logging.info("Tkinter event loop started")


if __name__ == "__main__":
    logging.info("Script started")
    main()
    logging.info("Script finished")
