"""
Piyano ses sentezleri oluşturan yardımcı modül.
Pygame mixer ile gerçek zamanlı piyano sesleri üretir.
"""

import pygame
import numpy as np
import io
import wave
import struct


class PianoSynthesizer:
    """Piyano notalarını synth ile üreten ses motoru."""
    
    def __init__(self, sample_rate=44100, duration=0.5):
        """
        :param sample_rate: Ses sampling rate (Hz)
        :param duration: Her nota için süre (saniye)
        """
        self.sample_rate = sample_rate
        self.duration = duration
        self.samples = int(sample_rate * duration)
        
        # Piyano notalarının frekansları (A0 ~ C8 arası)
        self.note_frequencies = {
            "C": 261.63,   # Orta C
            "D": 293.66,
            "E": 329.63,
            "F": 349.23,
            "G": 391.99,
            "A": 440.00,   # Standart A
            "B": 493.88,
        }
    
    def generate_sine_wave(self, frequency, amplitude=0.3):
        """
        Belirtilen frekansda sine wave (piyano benzer ses) oluştur.
        
        :param frequency: Frekans (Hz)
        :param amplitude: Ses genliği (0-1)
        :return: numpy array (samples)
        """
        t = np.linspace(0, self.duration, self.samples, False)
        waveform = amplitude * np.sin(2 * np.pi * frequency * t)
        
        # Fade-out efekti (sonunda yumuşak kapanış)
        fade_start = int(self.samples * 0.7)
        fade_envelope = np.ones(self.samples)
        fade_envelope[fade_start:] = np.linspace(1, 0, self.samples - fade_start)
        
        waveform *= fade_envelope
        
        return waveform
    
    def create_note_sound(self, note_name):
        """
        Piyano notası ses dosyası oluştur - memory'de WAV format.
        
        :param note_name: Not adı ("C", "D", "E", vs.)
        :return: pygame.mixer.Sound nesnesi
        """
        if note_name not in self.note_frequencies:
            raise ValueError(f"Geçersiz nota: {note_name}")
        
        frequency = self.note_frequencies[note_name]
        waveform = self.generate_sine_wave(frequency)
        
        # Numpy array'i 16-bit PCM'e dönüştür
        waveform_int16 = (waveform * 32767).astype(np.int16)
        
        # Stereo (2 channel) yapmak için mono waveform'u duplicate et
        # Pygame stereo kullanıyor - her channel'a aynı ses koy
        stereo_waveform = np.repeat(waveform_int16[:, np.newaxis], 2, axis=1)
        
        # BytesIO buffer'ında WAV dosyası oluştur
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            # 2 channels (stereo), 2 bytes per sample (16-bit), sample rate
            wav_file.setnchannels(2)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            
            # Raw audio data
            wav_file.writeframes(stereo_waveform.tobytes())
        
        wav_buffer.seek(0)
        
        # Pygame Sound nesnesi oluştur
        sound = pygame.mixer.Sound(wav_buffer)
        
        return sound
    
    def create_all_notes(self):
        """Tüm notalar için ses dosyaları oluştur."""
        sounds = {}
        for note in self.note_frequencies.keys():
            try:
                sounds[note] = self.create_note_sound(note)
            except Exception as e:
                print(f"⚠️  Not '{note}' ses dosyası oluşturulamadı: {e}")
        
        return sounds


def create_piano_sounds():
    """Başlangıçta piyano seslerini oluştur ve döndür."""
    synthesizer = PianoSynthesizer(sample_rate=44100, duration=0.3)
    return synthesizer.create_all_notes()

