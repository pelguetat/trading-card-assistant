import threading
import core.identify_cards_world as main_script
import queue
from concurrent.futures import ThreadPoolExecutor
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Global flag to signal threads to terminate
terminate_flag = threading.Event()


def main():
    logging.info("Starting main function")
    frame_queue = queue.Queue()

    with ThreadPoolExecutor() as executor:
        logging.info("Submitting process_video task to ThreadPoolExecutor")
        executor.submit(main_script.process_video, frame_queue, terminate_flag)


if __name__ == "__main__":
    logging.info("Script started")
    main()
    logging.info("Script finished")
