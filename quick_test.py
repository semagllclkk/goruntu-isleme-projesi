#!/usr/bin/env python
"""Hızlı modül test script'i"""

print("=" * 60)
print("🧪 MODÜLLERİ TEST EDIYORUZ")
print("=" * 60)

# 1. Physics Core
print("\n✓ Physics Core modülünü kontrol ediyorum...")
try:
    from physics_core import BallEntity, PhysicsEngine, BallColor, COLOR_SCORES
    print(f"  ✅ BallColor renkleri: {[BallColor.BLUE, BallColor.GREEN, BallColor.YELLOW]}")
    print(f"  ✅ COLOR_SCORES hazır: {len(COLOR_SCORES)} renk tanımı")
    
    # Test ball oluştur
    test_ball = BallEntity(x=100, y=100, radius=10, color=BallColor.BLUE, velocity=5)
    print(f"  ✅ Test topu oluşturuldu: ID={test_ball.id[:8]}..., Renk={test_ball.color}")
except Exception as e:
    print(f"  ❌ HATA: {e}")

# 2. Hand Tracking
print("\n✓ Hand Tracking modülünü kontrol ediyorum...")
try:
    from hand_tracking import HandTracker
    print(f"  ✅ HandTracker sınıfı hazır")
    # Nesne oluştur
    tracker = HandTracker(smoothing_window=5)
    print(f"  ✅ HandTracker örneği oluşturuldu")
except Exception as e:
    print(f"  ❌ HATA: {e}")

# 3. Pygame
print("\n✓ Pygame modülünü kontrol ediyorum...")
try:
    import pygame
    print(f"  ✅ Pygame versiyonu: {pygame.version.vernum}")
except Exception as e:
    print(f"  ❌ HATA: {e}")

# 4. OpenCV
print("\n✓ OpenCV modülünü kontrol ediyorum...")
try:
    import cv2
    print(f"  ✅ OpenCV versiyonu: {cv2.__version__}")
except Exception as e:
    print(f"  ❌ HATA: {e}")

# 5. MediaPipe
print("\n✓ MediaPipe modülünü kontrol ediyorum...")
try:
    import mediapipe as mp
    print(f"  ✅ MediaPipe hazır")
except Exception as e:
    print(f"  ❌ HATA: {e}")

print("\n" + "=" * 60)
print("✅ TÜM MODÜLLERİ BAŞARIYLA KONTROL ETTİK!")
print("=" * 60)
