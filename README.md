# 🎯 VisionStrike: Hand-Tracking Physics Game

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.0%2B-green?style=for-the-badge&logo=python&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Latest-orange?style=for-the-badge)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red?style=for-the-badge&logo=opencv&logoColor=white)

## 📖 Proje Özeti
**VisionStrike**, bilgisayar görüşü (Computer Vision) ve fizik tabanlı etkileşimi birleştiren yenilikçi bir arcade oyunudur. Kameradan alınan gerçek zamanlı el hareketleri verileriyle, ekranda dinamik olarak üretilen fiziksel objelerle etkileşime girebilirsiniz. Klasik donanım (mouse/klavye) bağımlılıklarını ortadan kaldıran bu proje, insan-bilgisayar etkileşiminde (HCI) sürükleyici ve yeni nesil bir deneyim sunmayı hedeflemektedir.

---

## 🏗️ Teknik Mimari ve Roller
Proje, sürdürülebilirliği ve performansı maksimize etmek adına profesyonel yazılım geliştirme standartlarına (SOLID) uygun olarak modüler bir yapıda tasarlanmıştır. Sistem üç ana bileşenden oluşur:

### 👁️ 1. Görüntü İşleme (Computer Vision)
- **MediaPipe Entegrasyonu:** El eklem noktalarının (landmarks) milisaniyeler içinde yüksek hassasiyetle tespiti.
- **Titreme Önleyici (Smoothing):** Hareketli ortalama (Moving Average) algoritması sayesinde işaret parmağı takibindeki titremeleri minimize eden filtreleme sistemi.
- **Koordinat Eşleme:** Kamera uzayından alınan 3D koordinat vektörlerinin, oyun ekranı (2D) uzayına anlık olarak normalize edilmesi ve izdüşümünün alınması.

### ⚛️ 2. Fizik ve Matematik Motoru
Oyun içi etkileşimler, performansı optimize edilmiş özel bir fizik motoru tarafından yönetilir:
- **Çarpışma Algılama:** El koordinatları ile nesne merkezleri arasındaki etkileşim, Öklid mesafesi formülü ile hesaplanarak $O(1)$ karmaşıklığında tespit edilir:
  $$d = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$$
- **Yerçekimi Simülasyonu:** Nesnelerin kütleçekim kuvvetiyle aşağı doğru ivmelenmesi, kinematik denklemlerle simüle edilerek doğal bir düşüş hissi yaratılması.
- **Rastgele Nesne Üretimi (Spawning):** Nesnelerin ekranda üst üste binmesini engelleyen (overlap-free) ve RNG tabanlı akıllı spawn mekanizması.

### 🎭 3. Yaşam Döngüsü ve UI (Lifecycle & UI)
- **Asenkron Efektler:** Etkileşime girilen hedeflerin ekrandan aniden silinmesi yerine, asenkron fade-out (karararak kaybolma) ve parlama (glow) efektleriyle yumuşak geçişlerin sağlanması.
- **Pygame Entegrasyonu:** Çerçeve hızı bağımsız (delta-time tabanlı) akıcı bir render döngüsü ve UI katmanı.
- **Ses Motoru:** Nesne çarpışmaları anında tetiklenen, oyunun atmosferini zenginleştiren piyano notası tabanlı dinamik ses motoru.

---

## 🎮 Oyun Mekanikleri ve Puanlama Tablosu
Oyun, farklı renkteki kürelerin yakalanmasına dayalı dinamik bir risk ve ödül sistemi içerir. Hedefin rengine göre kazanılan puanlar değişirken, kırmızı küreler hayatta kalma mücadelesini zorlaştırır.

| Hedef Rengi | Puan Katsayısı | Rol ve Etki |
| :---: | :---: | :--- |
| 🟣 **Mor** | **+7** | Nadir çıkan, çok yüksek değerli hedef. |
| 🔵 **Mavi** | **+5** | Yüksek puanlı premium hedef. |
| 🟢 **Yeşil** | **+4** | Dengeli skor kazandıran ana hedeflerden. |
| 🟡 **Sarı** | **+3** | Yaygın ve standart hedef. |
| ⚫ **Siyah** | **+2** | Düşük puanlı dolgu hedef. |
| ⚪ **Beyaz** | **+1** | En düşük puanlı zayıf hedef. |
| 🔴 **Kırmızı** | **-1 CAN** | **TEHLİKE:** Yakalandığında oyuncudan bir can eksiltir. Uzak durulmalıdır! |

---

## 🛠️ Kullanılan Teknolojiler & Gereksinimler
Modern bilgisayar görüşü yeteneklerini sağlam bir oyun altyapısıyla birleştirmek için aşağıdaki teknoloji yığını kullanılmıştır:
- **Python (3.8+):** Mimari omurgayı oluşturan temel dil.
- **Pygame:** Yüksek performanslı 2D render motoru ve ses yönetimi.
- **MediaPipe:** Gerçek zamanlı makine öğrenmesi ve el takibi çözümü.
- **OpenCV (opencv-python):** Web kamerasından frame yakalama ve düşük seviyeli görüntü manipülasyonu.
- **NumPy:** Yüksek performanslı matematiksel dizilim ve matris işlemleri.

## 📦 Kurulum ve Çalıştırma
1. Proje dizinine gidin:
   ```bash
   cd goruntu_isleme_projesi
   ```
2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
   *(Alternatif olarak: `pip install opencv-python mediapipe numpy pygame`)*
3. **Test Uygulamasını Çalıştırma (El Takibi Modülü):**
   Sadece kamera ve el takibi altyapısını test etmek için:
   ```bash
   python test_main.py
   ```
   *(Uygulamadan çıkmak için 'q' tuşuna basmanız yeterlidir.)*

---

## 💻 Geliştiriciler İçin (Modül Kullanımı)
Görüntü işleme modülü (`HandTracker` sınıfı) diğer oyun dosyalarına kolayca entegre edilecek şekilde tasarlanmıştır:
```python
from hand_tracking import HandTracker
import cv2

# Yumuşatma değeri ile takip nesnesini başlat
tracker = HandTracker(smoothing_window=5)
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if success:
        # Gerçek zamanlı parmak koordinatlarını al (x, y)
        coords = tracker.get_finger_position(frame)
        if coords:
            print(f"Parmak Pozisyonu: {coords}")
```

## 📂 Proje Yapısı
- `hand_tracking.py`: El takibi mantığını ve `HandTracker` sınıfını içeren CV modülü.
- `test_main.py`: Görüntü işleme modülünün performansını ve doğruluğunu test eden görsel arayüz.
- `requirements.txt`: Proje bağımlılıklarının listesi.

## 👥 Geliştirici Ekip
Bu proje, yazılım mühendisliği prensipleri doğrultusunda modüler bir iş bölümü ile geliştirilmiştir:
- **Ayşen Çiftçi** - Görüntü İşleme (Computer Vision) ve El Takibi
- **Ayberk Erkan** - Fizik Motoru ve Oyun Matematiği
- **Sema Gül Çelik** - Arayüz (UI), Yaşam Döngüsü ve Ses Entegrasyonu
