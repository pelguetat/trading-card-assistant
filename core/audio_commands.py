from transformers import pipeline

from transformers.pipelines.audio_utils import ffmpeg_microphone_live
import sys
from core.langgraph_main import langgraph_start
from core.listen import wake_word_detector
from core.llm import LLMChat


transcriber = pipeline(
    "automatic-speech-recognition", model="openai/whisper-base.en", device="mps"
)


def transcribe(chunk_length_s=5.0, stream_chunk_s=1.0):
    sampling_rate = transcriber.feature_extractor.sampling_rate

    mic = ffmpeg_microphone_live(
        sampling_rate=sampling_rate,
        chunk_length_s=chunk_length_s,
        stream_chunk_s=stream_chunk_s,
    )

    print("Start speaking...")
    for item in transcriber(mic, generate_kwargs={"max_new_tokens": 128}):
        sys.stdout.write("\033[K")
        print(item["text"], end="\r")
        if not item["partial"][0]:
            break

    return item["text"]


def process_audio_commands(frame_queue, terminate_flag):
    while not terminate_flag.is_set():

        while wake_word_detector(debug=False, terminate_flag=terminate_flag):
            print("Listening!")
            transcription = transcribe()
            langgraph_start(user_input=transcription, frame_queue=frame_queue, terminate_flag=terminate_flag)
