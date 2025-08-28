import base64
from datetime import datetime
import os
from openai import OpenAI
from regex import B
from core.models import BoardState
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_vertexai import ChatVertexAI


def update_board_state():
    pass

def send_frames_to_llm(frames):
    time = datetime.now().strftime("%H:%M:%S")
    prompt = [
        {"type": "text", "text": "Your job is to look at the images of Pokemon Trading Card game board attached and based on the schema, update the board state by outputting a json file with the schema that reflect all of the changes since the last update."
            + "\nCurrent time: {time}.",}
    ]

    for image in frames:
        # image_path = image["file"]
        # base64_image = encode_image(image_path)
        prompt.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image}",
                },
            },
        )
    messages = [
        {
            "role": "user",
            "content": prompt,
        }
    ]

    llm = ChatVertexAI(model="gemini-1.5-pro-001")
    tools = [BoardState,]
    llm_with_tools = llm.bind_tools(tools)
    # Our LLM doesn't have to know which nodes it has to route to. In its 'mind', it's just invoking functions.
    runnable = llm_with_tools
    board_update = runnable.invoke(messages)
    return board_update

# Open the image file and encode it as a base64 string
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
