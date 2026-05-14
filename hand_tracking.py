import cv2
import mediapipe as mp
import numpy as np
from collections import deque
from typing import Tuple, Optional, List

class HandTracker:
    """
    Kamera görüntüsünden el takibi yaparak işaret parmakları koordinatlarını döndüren modül.
    SOLID prensiplerine uygun ve performans odaklı tasarlanmıştır.
    """
    
    def __init__(self, static_image_mode: bool = False, 
                 max_num_hands: int = 2, 
                 min_detection_confidence: float = 0.5, 
                 min_tracking_confidence: float = 0.5,
                 smoothing_window: int = 3):
        """
        MediaPipe Hands çözümünü ilklendirir.
        
        :param max_num_hands: Takip edilecek maksimum el sayısı.
        :param smoothing_window: Koordinat yumuşatma için kullanılacak kare sayısı.
        """
        # MediaPipe Hands bileşenlerini hazırla
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # Yumuşatma (Smoothing) için her el için ayrı koordinat kuyruğu
        self.smoothing_window = smoothing_window
        self.max_num_hands = max_num_hands
        # Her elin ID'sine göre (0, 1, ...) geçmişini tutar
        self.coordinate_histories = [deque(maxlen=smoothing_window) for _ in range(max_num_hands)]

    def get_fingers_positions(self, frame: np.ndarray) -> List[Tuple[int, int]]:
        """
        Gelen karedeki tüm tespit edilen ellerin işaret parmağı uçlarının (landmark 8) piksel koordinatlarını döner.
        
        :param frame: OpenCV BGR karesi.
        :return: (x, y) piksel koordinatlarından oluşan liste.
        """
        # Performans için: BGR -> RGB dönüşümü (MediaPipe RGB bekler)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Performans: Eğer görüntü çok büyükse MediaPipe'ı yormamak için küçültüyoruz
        # Ancak koordinatları orijinal frame boyutuna göre hesaplayacağımız için 
        # sadece işlem yapılacak görüntüyü (rgb_frame) küçültmek yeterli.
        processing_w, processing_h = 640, 480
        if frame.shape[1] > processing_w:
            rgb_frame = cv2.resize(rgb_frame, (processing_w, processing_h))
            
        # İşlemi hızlandırmak için frame'in yazılabilirliğini geçici olarak kapatıyoruz
        rgb_frame.flags.writeable = False 
        results = self.hands.process(rgb_frame)
        rgb_frame.flags.writeable = True
        
        finger_positions = []
        
        if results.multi_hand_landmarks:
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                if i >= self.max_num_hands:
                    break
                    
                # İşaret parmağı ucu (Index Finger Tip) -> Landmark ID: 8
                index_finger_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                
                # Normalize koordinatları piksel koordinatlarına çevir
                h, w, _ = frame.shape
                cx, cy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
                
                # Yumuşatma uygula (her el için kendi geçmişi ile)
                smoothed_coords = self._apply_smoothing(i, cx, cy)
                finger_positions.append(smoothed_coords)
        
        # Eğer bir el kaybolursa o elin geçmişini temizle (basit mantık: tespit edilenlerden fazlasını temizle)
        num_detected = len(results.multi_hand_landmarks) if results.multi_hand_landmarks else 0
        for i in range(num_detected, self.max_num_hands):
            self.coordinate_histories[i].clear()
            
        return finger_positions

    def get_finger_position(self, frame: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Geriye dönük uyumluluk için: Sadece ilk elin pozisyonunu döner.
        """
        positions = self.get_fingers_positions(frame)
        return positions[0] if positions else None

    def _apply_smoothing(self, hand_index: int, x: int, y: int) -> Tuple[int, int]:
        """
        Titremeyi (jitter) önlemek için hareketli ortalama (Moving Average) uygular.
        """
        history = self.coordinate_histories[hand_index]
        history.append((x, y))
        
        # Kuyruktaki tüm x ve y değerlerinin ortalamasını al
        avg_x = int(np.mean([p[0] for p in history]))
        avg_y = int(np.mean([p[1] for p in history]))
        
        return avg_x, avg_y

    def __del__(self):
        """Kaynakları serbest bırak."""
        self.hands.close()

