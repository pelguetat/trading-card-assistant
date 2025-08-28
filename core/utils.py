
import queue

def get_multiple(frame_queue, n):
    """Retrieve up to n items from the queue."""
    items = []
    for _ in range(n):
        try:
            items.append(frame_queue.get())
        except queue.Empty:
            break
    return items