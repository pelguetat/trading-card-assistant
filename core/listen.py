import pyaudio
import numpy as np
from transformers import pipeline

device = "mps"

classifier = pipeline(
    "audio-classification", model="MIT/ast-finetuned-speech-commands-v2", device=device
)


def normalize_audio(audio):
    """Normalize the audio to have zero mean and unit variance."""
    audio = audio - np.mean(audio)
    audio = audio / np.std(audio)
    return audio


def wake_word_detector(
    wake_word="marvin",
    prob_threshold=0.7,  # Adjusted threshold to reduce sensitivity
    chunk_length_s=2.0,
    stream_chunk_s=0.25,
    debug=True,
    terminate_flag=None,
):
    if wake_word not in classifier.model.config.label2id.keys():
        raise ValueError(
            f"Wake word {wake_word} not in set of valid class labels, pick a wake word in the set {classifier.model.config.label2id.keys()}."
        )

    sampling_rate = classifier.feature_extractor.sampling_rate
    chunk_size = int(sampling_rate * stream_chunk_s)

    p = pyaudio.PyAudio()

    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sampling_rate,
        input=True,
        frames_per_buffer=chunk_size * 2,
    )

    print("Listening for wake word...")
    audio_buffer = np.zeros(int(sampling_rate * chunk_length_s), dtype=np.int16)

    try:
        while not terminate_flag.is_set():

            while True:
                audio_chunk = np.frombuffer(
                    stream.read(chunk_size, exception_on_overflow=False), dtype=np.int16
                )
                audio_buffer = np.roll(audio_buffer, -chunk_size)
                audio_buffer[-chunk_size:] = audio_chunk

                # Normalize the audio buffer
                normalized_audio = normalize_audio(audio_buffer)

                prediction = classifier(normalized_audio)
                prediction = prediction[0]
                if debug:
                    print(prediction)
                if prediction["label"] == wake_word:
                    if prediction["score"] > prob_threshold:
                        return True
        return False
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        if stream.is_active():
            stream.stop_stream()
            stream.close()
            p.terminate()
