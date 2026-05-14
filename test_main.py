import cv2
import time
from hand_tracking import HandTracker

def main():
    # Kamera yakalayıcıyı başlat (Genelde index 0 ana kameradır)
    cap = cv2.VideoCapture(0)
    
    # HandTracker nesnesini oluştur
    tracker = HandTracker(smoothing_window=5)
    
    # FPS hesaplama için zaman değişkeni
    prev_time = 0

    print("Uygulama başlatıldı. Çıkmak için 'q' tuşuna basın.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Kameradan görüntü alınamadı.")
            break

        # 1. Görüntüyü yatayda çevir (Ayna efekti)
        frame = cv2.flip(frame, 1)

        # 2. İşaret parmağı koordinatlarını al
        coords = tracker.get_finger_position(frame)

        # 3. Eğer parmak bulunduysa ekrana çiz
        if coords:
            x, y = coords
            # Mavi renkte (BGR: 255, 0, 0) içi dolu bir daire çiz
            cv2.circle(frame, (x, y), 15, (255, 0, 0), cv2.FILLED)
            # Koordinatları görselleştir (Opsiyonel)
            cv2.putText(frame, f"({x}, {y})", (x + 20, y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # 4. FPS Hesapla ve ekrana yazdır
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time
        cv2.putText(frame, f"FPS: {int(fps)}", (20, 50), 
                    cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)

        # 5. Pencereyi göster
        cv2.imshow("Hand Tracking Test - Piano Tiles Modülü", frame)

        # 'q' tuşuna basıldığında döngüden çık
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Kaynakları temizle
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
