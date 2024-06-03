import uuid
from identify_cards import process_video  # Import the process_video function
from langgraph_main import _print_event, part_1_graph
from dotenv import load_dotenv
import os
from queue import Queue
import threading
from langchain_core.messages.ai import AIMessage


from llm import LLMChat

load_dotenv()
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Pokemon Trainer"


def langgraph_start(user_input):
    thread_id = "12345"

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }
    _printed = set()

    events = part_1_graph.stream(
        {
            "messages": (
                "user",
                user_input,
            )
        },
        config,
        stream_mode="values",
    )
    for event in events:
        _print_event(event, _printed)
        messages = event.get("messages")
        if messages and isinstance(messages, list) and messages[-1].type == "ai":
            llm = LLMChat()
            response = messages[-1].content
            llm.create_audio(response)
