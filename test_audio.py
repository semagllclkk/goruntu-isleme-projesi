#!/usr/bin/env python
"""Test ses sistemini ayır."""

import sys
import traceback

print("1. Pygame içeri aktar...")
try:
    import pygame
    print("   ✓ Pygame yüklü")
except Exception as e:
    print(f"   ✗ Pygame hatası: {e}")
    sys.exit(1)

print("\n2. Pygame mixer başlat (mono)...")
try:
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    print(f"   ✓ Mixer başlatıldı")
    print(f"   - Format: {pygame.mixer.get_init()}")
except Exception as e:
    print(f"   ✗ Mixer hatası: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n3. Piano seslerini oluştur...")
try:
    from piano_sounds import create_piano_sounds
    piyano_sesleri = create_piano_sounds()
    print(f"   ✓ {len(piyano_sesleri)} nota oluşturuldu: {list(piyano_sesleri.keys())}")
except Exception as e:
    print(f"   ✗ Ses oluşturma hatası: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n4. Bir notu çal (C)...")
try:
    if "C" in piyano_sesleri:
        piyano_sesleri["C"].play()
        print("   ✓ C notu çalıştırıldı")
        print("   (Ses çalmalıdır...)")
    else:
        print("   ✗ C notu bulunamadı")
except Exception as e:
    print(f"   ✗ Çalma hatası: {e}")
    traceback.print_exc()

print("\nTest tamamlandı.")
