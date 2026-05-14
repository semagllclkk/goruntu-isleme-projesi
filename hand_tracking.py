import cv2
import mediapipe as mp
import numpy as np
from collections import deque
from typing import Tuple, Optional

class HandTracker:
    """
    Kamera görüntüsünden el takibi yaparak işaret parmağı koordinatlarını döndüren modül.
    SOLID prensiplerine uygun ve performans odaklı tasarlanmıştır.
    """
    
    def __init__(self, static_image_mode: bool = False, 
                 max_num_hands: int = 1, 
                 min_detection_confidence: float = 0.5, 
                 min_tracking_confidence: float = 0.5,
                 smoothing_window: int = 5):
        """
        MediaPipe Hands çözümünü ilklendirir.
        
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
        
        # Yumuşatma (Smoothing) için koordinat kuyruğu
        self.smoothing_window = smoothing_window
        self.coordinate_history = deque(maxlen=smoothing_window)

    def get_finger_position(self, frame: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Gelen karedeki işaret parmağı ucunun (landmark 8) piksel koordinatlarını döner.
        
        :param frame: OpenCV BGR karesi.
        :return: (x, y) piksel koordinatları veya parmak bulunamazsa None.
        """
        # Performans için: BGR -> RGB dönüşümü (MediaPipe RGB bekler)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # İşlemi hızlandırmak için frame'in yazılabilirliğini geçici olarak kapatabiliriz
        # rgb_frame.flags.writeable = False 
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            # Sadece ilk eli al (max_num_hands=1 olduğu için)
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # İşaret parmağı ucu (Index Finger Tip) -> Landmark ID: 8
            index_finger_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
            
            # Normalize koordinatları piksel koordinatlarına çevir
            h, w, _ = frame.shape
            cx, cy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
            
            # Yumuşatma uygula
            return self._apply_smoothing(cx, cy)
        
        # El bulunamazsa geçmişi temizle ve None dön
        self.coordinate_history.clear()
        return None

    def _apply_smoothing(self, x: int, y: int) -> Tuple[int, int]:
        """
        Titremeyi (jitter) önlemek için hareketli ortalama (Moving Average) uygular.
        """
        self.coordinate_history.append((x, y))
        
        # Kuyruktaki tüm x ve y değerlerinin ortalamasını al
        avg_x = int(np.mean([p[0] for p in self.coordinate_history]))
        avg_y = int(np.mean([p[1] for p in self.coordinate_history]))
        
        return avg_x, avg_y

    def __del__(self):
        """Kaynakları serbest bırak."""
        self.hands.close()
