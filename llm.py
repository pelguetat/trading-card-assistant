import base64
import json
import os
import pyaudio
from openai import OpenAI
from dotenv import load_dotenv
import requests


class LLMChat:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Initialize PyAudio
        self.p = pyaudio.PyAudio()

        # Define stream parameters
        self.audio_stream = self.p.open(
            format=pyaudio.paInt16, channels=1, rate=24000, output=True
        )

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def create_image_completion(self, images):
        image_1 = images[0]["file"]
        metadata_1 = images[0]["metadata"]
        image_2 = images[1]["file"]
        metadata_2 = images[1]["metadata"]
        image_3 = images[2]["file"]
        metadata_3 = images[2]["metadata"]

        content = [
            {"type": "text", "text": "Give me the names of the following Pokemon:"}
        ]

        for image in images:
            image_path = image["file"]
            base64_image = self.encode_image(image_path)
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                    },
                },
            )
        messages = [
            {
                "role": "user",
                "content": content,
            }
        ]

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            stream=True,
        )
        return response

    def generate_audio(self, image_and_metadata):
        response = self.create_image_completion(image_and_metadata)
        self.process_audio_response(response)

    def process_audio_response(self, response):
        sentences = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                print(content, end="")
                sentences += content
                if sentences.endswith((".", "!", "?")):
                    audio_response = self.client.audio.speech.create(
                        model="tts-1",
                        voice="echo",
                        input=sentences,
                        response_format="pcm",
                    )

                    sentences = ""

                    for audio_chunk in audio_response.iter_bytes(1024):
                        self.audio_stream.write(audio_chunk)

    def create_audio(self, response):
        audio_response = self.client.audio.speech.create(
            model="tts-1",
            voice="echo",
            input=response,
            response_format="pcm",
        )

        for audio_chunk in audio_response.iter_bytes(1024):
            self.audio_stream.write(audio_chunk)

    def close(self):
        # Close the PyAudio stream when done
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.p.terminate()

    def create_chat_completion(self, input_text):

        content = [{"type": "text", "text": input_text}]

        messages = [
            {
                "role": "user",
                "content": content,
            }
        ]

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            stream=True,
        )
        return response
