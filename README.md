# 🎯 VisionStrike: Hand-Tracking Physics Game

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.0%2B-green?style=for-the-badge&logo=python&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Latest-orange?style=for-the-badge)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red?style=for-the-badge&logo=opencv&logoColor=white)

## 📖 Proje Özeti
**VisionStrike**, bilgisayar görüşü ve fizik tabanlı etkileşimi birleştiren yenilikçi bir arcade oyunudur. Kameradan alınan gerçek zamanlı el hareketleri verileriyle, ekranda dinamik olarak üretilen fiziksel objelerle etkileşime girebilirsiniz. Klasik donanım (mouse/klavye) bağımlılıklarını ortadan kaldıran bu proje, insan-bilgisayar etkileşiminde (HCI) sürükleyici ve yeni nesil bir deneyim sunmayı hedeflemektedir.

---

## 🏗️ Teknik Mimari ve Roller

Proje, sürdürülebilirliği ve performansı maksimize etmek adına profesyonel yazılım geliştirme standartlarına uygun olarak modüler bir yapıda tasarlanmıştır.

### 👁️ 1. Görüntü İşleme (Computer Vision)
* **MediaPipe Entegrasyonu:** El eklem noktalarının (landmarks) milisaniyeler içinde yüksek hassasiyetle tespiti.
* **Koordinat Eşleme:** Kamera uzayından alınan 3D koordinat vektörlerinin, oyun ekranı (2D) uzayına anlık olarak normalize edilmesi ve izdüşümünün alınması.

### ⚛️ 2. Fizik ve Matematik Motoru
Oyun içi etkileşimler, performansı optimize edilmiş özel bir fizik motoru tarafından yönetilir:
* **Çarpışma Algılama:** El koordinatları ile nesne merkezleri arasındaki etkileşim, Öklid mesafesi formülü ile hesaplanarak O(1) karmaşıklığında tespit edilir:
  ```math
  d = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}
  ```
* **Yerçekimi Simülasyonu:** Nesnelerin kütleçekim kuvvetiyle aşağı doğru ivmelenmesi, kinematik denklemlerle simüle edilerek doğal bir düşüş hissi yaratılması.
* **Rastgele Nesne Üretimi (Spawning):** Nesnelerin ekranda üst üste binmesini engelleyen (overlap-free) ve RNG (Random Number Generator) tabanlı akıllı spawn mekanizması.

### 🎭 3. Yaşam Döngüsü ve UI (Lifecycle & UI)
* **Asenkron Efektler:** Etkileşime girilen hedeflerin ekrandan aniden silinmesi yerine, asenkron `fade-out` (karararak kaybolma) ve parlama (glow) efektleriyle yumuşak geçişlerin sağlanması.
* **Pygame Entegrasyonu:** Çerçeve hızı bağımsız (delta-time tabanlı) akıcı bir render döngüsü ve UI katmanı.
* **Ses Motoru:** Nesne çarpışmaları anında tetiklenen, oyunun atmosferini zenginleştiren piyano notası tabanlı dinamik ses motoru.

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

## 🛠️ Kullanılan Teknolojiler

Modern bilgisayar görüşü yeteneklerini sağlam bir oyun altyapısıyla birleştirmek için aşağıdaki teknoloji yığını kullanılmıştır:

* **Python:** Mimari omurgayı oluşturan temel dil.
* **Pygame:** Yüksek performanslı 2D render motoru ve ses yönetimi.
* **MediaPipe:** Google tarafından geliştirilen gerçek zamanlı makine öğrenmesi ve el takibi çözümü.
* **OpenCV:** Web kamerasından frame yakalama ve düşük seviyeli görüntü manipülasyonu.
