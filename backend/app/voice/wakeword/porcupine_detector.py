import pvporcupine
import pyaudio
import struct

class WakeWordDetector:
    def __init__(self, keywords=["computer", "hey assistant"]):
        self.porcupine = pvporcupine.create(
            access_key="YOUR_PORCUPINE_ACCESS_KEY",
            keywords=keywords
        )
        self.audio_stream = pyaudio.PyAudio().open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

    def listen_for_wake_word(self):
        """Blocks until wake word is detected"""
        while True:
            pcm = self.audio_stream.read(self.porcupine.frame_length)
            pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
            keyword_index = self.porcupine.process(pcm)
            if keyword_index >= 0:
                return True