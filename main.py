import threading
import identify_cards_world as main_script
import queue
from concurrent.futures import ThreadPoolExecutor
from langgraph_main import langgraph_start
from dotenv import load_dotenv
import os
import tkinter as tk
import logging
import cProfile
from audio_commands import process_audio_commands

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Pokemon Trainer"

# Global flag to signal threads to terminate
terminate_flag = threading.Event()


def main():
    logging.info("Starting main function")
    frame_queue = queue.Queue()

    with ThreadPoolExecutor() as executor:
        logging.info("Submitting process_video task to ThreadPoolExecutor")
        executor.submit(main_script.process_video, frame_queue, terminate_flag)

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
            langgraph_thread = threading.Thread(
                target=langgraph_start, args=(frame_queue, terminate_flag)
            )
            langgraph_thread.start()
            logging.info("LangGraph thread started")

        start_button = tk.Button(
            main_frame, text="Start LangGraph", command=on_button_click
        )
        start_button.pack(pady=20)

        # Create a canvas to display the video frames
        canvas = tk.Canvas(main_frame, width=1280, height=720)
        canvas.pack()

        # Run the display_frames function in a separate thread
        display_thread = threading.Thread(
            target=main_script.display_frames,
            args=(frame_queue, canvas, root, terminate_flag),
        )
        display_thread.start()
        logging.info("Display frames thread started")

        # Create and start a thread for process_audio_commands
        audio_thread = threading.Thread(
            target=process_audio_commands,
            daemon=True,
            args=(frame_queue, terminate_flag),
        )
        audio_thread.start()
        logging.info("Audio commands thread started")

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
