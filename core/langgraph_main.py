from datetime import datetime
import os
from typing import Annotated

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from typing_extensions import TypedDict

from langgraph.graph.message import AnyMessage, add_messages
from core.identify_cards_world import crop_and_save_images

from core.llm import LLMChat
from core.prompts import PROMPT
from core.similarity_search import SimilaritySearch
from langchain_core.tools import tool

from langchain_core.runnables import RunnableLambda
from langchain_core.messages import ToolMessage

from langgraph.prebuilt import ToolNode

from langgraph.graph import END, StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import ToolMessage
from langchain_core.runnables import ensure_config

from dotenv import load_dotenv
import queue

load_dotenv()
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Pokemon Trainer"


def langgraph_start(user_input, frame_queue, terminate_flag):
    import random

    while not terminate_flag.is_set():

        thread_id = str(random.randint(10000, 99999))
        config = {
            "configurable": {
                "thread_id": thread_id,
                "frame_queue": frame_queue,
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
            if (
                messages
                and isinstance(messages, list)
                and messages[-1].type == "ai"
                and not messages[-1].tool_calls
            ):
                llm = LLMChat()
                response = messages[-1].content
                llm.create_audio(response)


@tool
def card_identifier() -> str:
    """
    This tool identifies the card from the image and outputs the card metadata.
    There is no need to provide an image to use it."""
    config = ensure_config()
    configuration = config.get("configurable", {})
    frame_queue = configuration.get("frame_queue", None)
    if not frame_queue:
        raise ValueError("No frame_queue configured.")

    def get_multiple(frame_queue, n):
        """Retrieve up to n items from the queue."""
        items = []
        for _ in range(n):
            try:
                items.append(frame_queue.get())
            except queue.Empty:
                break
        return items

    five_frames = get_multiple(frame_queue, 5)
    cropped_images = crop_and_save_images(five_frames)
    # Do similarity search for the identified cards
    image_dir = "/Users/pabloelgueta/Documents/trading-card-assistant/images"
    json_file_path = "/Users/pabloelgueta/Documents/trading-card-assistant/pokemon-tcg-data-master/cards/en/"

    processor = SimilaritySearch(image_dir, json_file_path)
    results = processor.process_search_file(cropped_images)

    return results


@tool
def trigger_card_crop() -> None:
    """
    This tool triggers the card crop from the video feed.
    There is no need to provide an image to use it."""

    identify_cards.trigger_crop()
    return True


def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def _print_event(event: dict, _printed: set, max_length=1500):
    current_state = event.get("dialog_state")
    if current_state:
        print(f"Currently in: ", current_state[-1])
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            print(msg_repr)
            _printed.add(message.id)


def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            result = self.runnable.invoke(state)
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}

            else:
                break
        return {"messages": result}


llm = ChatOpenAI(model="gpt-4o", temperature=1)


assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a Pokemon Trading Card Game tutor. Your first step is to always call the 'identify_card' tool."
            "Don't return the whole metadata, just the card name."
            + "\nCurrent time: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())


# Our LLM doesn't have to know which nodes it has to route to. In its 'mind', it's just invoking functions.
assistant_runnable = assistant_prompt | llm.bind_tools([card_identifier])


builder = StateGraph(State)


# Define nodes: these do the work
builder.add_node("assistant", Assistant(assistant_runnable))
builder.add_node("tools", ToolNode([card_identifier]))
# Define edges: these determine how the control flow moves
builder.set_entry_point("assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition,
)
builder.add_edge("tools", "assistant")

# The checkpointer lets the graph persist its state
# this is a complete memory for the entire graph.
memory = SqliteSaver.from_conn_string(":memory:")
part_1_graph = builder.compile(checkpointer=memory)
