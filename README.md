# Hand Tracking - El Takibi Modülü 

Bu proje, MediaPipe ve OpenCV kütüphanelerini kullanarak gerçek zamanlı el takibi gerçekleştiren ve özellikle oyun geliştirme için tasarlanmış modüler bir yapıdır.

## 🚀 Özellikler

- **Hızlı ve Verimli:** MediaPipe'ın optimize edilmiş modellerini kullanarak yüksek FPS hızlarına ulaşır.
- **Titreme Önleyici (Smoothing):** Hareketli ortalama (Moving Average) algoritması sayesinde işaret parmağı takibindeki titremeleri minimize eder.
- **SOLID Prensipleri:** Kod yapısı genişletilebilir, okunabilir ve modüler bir yapıda tasarlanmıştır.
- **Gerçek Zamanlı Görselleştirme:** FPS sayacı ve koordinat göstergesi ile test imkanı sunar.

## 🛠 Gereksinimler

Projenin çalışması için aşağıdaki Python kütüphanelerine ihtiyaç vardır:

- Python 3.8+
- OpenCV (`opencv-python`)
- MediaPipe (`mediapipe`)
- NumPy (`numpy`)

## 📦 Kurulum

1.  Proje dizinine gidin:
    ```bash
    cd goruntu_isleme_projesi
    ```

2.  Gerekli kütüphaneleri yükleyin:
    ```bash
    pip install opencv-python mediapipe numpy
    ```

## 💻 Kullanım

### Test Uygulamasını Çalıştırma
El takibi modülünü hemen test etmek için `test_main.py` dosyasını çalıştırabilirsiniz:

```bash
python test_main.py
```
- Uygulamadan çıkmak için **'q'** tuşuna basmanız yeterlidir.

### Modülü Projenize Dahil Etme
`HandTracker` sınıfını kendi projelerinizde şu şekilde kullanabilirsiniz:

```python
from hand_tracking import HandTracker
import cv2

tracker = HandTracker(smoothing_window=5)
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if success:
        # Koordinatları al (x, y)
        coords = tracker.get_finger_position(frame)
        if coords:
            print(f"Parmak Pozisyonu: {coords}")
```

## 📂 Proje Yapısı

- `hand_tracking.py`: El takibi mantığını ve `HandTracker` sınıfını içeren ana modül.
- `test_main.py`: Modülün performansını ve doğruluğunu test eden görsel arayüz.
- `debug_mediapipe.py`: MediaPipe kurulumu ve yollarını kontrol etmek için yardımcı betik.

## 📝 Notlar

- **Performans:** En iyi sonuç için yeterli ışıklandırma olan bir ortamda test yapılması önerilir.
- **Yumuşatma (Smoothing):** `HandTracker` sınıfını ilklendirirken `smoothing_window` değerini değiştirerek hassasiyeti ayarlayabilirsiniz (Daha yüksek değer = daha az titreme, daha fazla gecikme).

---
*Bu proje görüntü işleme çalışmaları kapsamında geliştirilmiştir.*
