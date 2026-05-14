import pygame
import pygame.gfxdraw
import sys
import math
import random
import cv2
from typing import List, Tuple, Dict, Any

from physics_core import BallEntity, PhysicsEngine, BallManager, BallColor
from hand_tracking import HandTracker
from piano_sounds import create_piano_sounds

# --- 1. BAŞLANGIÇ VE AYARLAR ---
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

GENISLIK = 800
YUKSEKLIK = 600
FPS = 60
ARKA_PLAN_RENGI = (20, 20, 25)  # Biraz daha koyu pro hissiyat
SURE_LIMITI = 120 * 1000  # 2 dakika (ms cinsinden)

ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK))
pygame.display.set_caption("Fizik Motoru: Pro Oyun Mekanikleri")
saat = pygame.time.Clock()

pygame.mixer.set_num_channels(8)
try:
    piyano_sesi = pygame.mixer.Sound("piyano-kısa.mp3")
except FileNotFoundError:
    piyano_sesi = None

# Piano notalarını yükle
piyano_sesleri = create_piano_sounds()

# Renk-Nota Mapping
RENK_NOTA_MAP = {
    BallColor.BLUE: "C",
    BallColor.GREEN: "E",
    BallColor.YELLOW: "G",
    BallColor.PURPLE: "A",
    BallColor.WHITE: "D",
    BallColor.RED: "B",
    BallColor.BLACK: "F",
}

# --- 2. RENK SABİTLERİ (RGB) ---
RGB_COLORS = {
    BallColor.BLUE: (50, 150, 255),  # Parlak Mavi
    BallColor.GREEN: (50, 255, 100),  # Neon Yeşil
    BallColor.YELLOW: (255, 230, 50),  # Altın Sarı
    BallColor.PURPLE: (200, 50, 255),  # Neon Mor
    BallColor.BLACK: (100, 100, 100),  # Gri/Siyah
    BallColor.WHITE: (255, 255, 255),  # Beyaz
    BallColor.RED: (255, 50, 50),  # Tehlike Kırmızı
}

# --- 3. UI VE OYUN DURUM DEĞİŞKENLERİ ---
pygame.font.init()
# Daha "Gaming" hissi için fontlar
oyun_fontu = pygame.font.SysFont("Impact", 32)
buyuk_font = pygame.font.SysFont("Impact", 64)
emoji_font = pygame.font.SysFont("Segoe UI Emoji", 32)

guncel_skor = 0
can = 3
oyun_baslama_zamani = pygame.time.get_ticks()

# --- ANA HEDEF RENK SİSTEMİ ---
mevcut_renkler = [
    BallColor.BLUE,
    BallColor.GREEN,
    BallColor.YELLOW,
    BallColor.PURPLE,
    BallColor.WHITE,
]
main_target_color = BallColor.BLUE  # Başlangıç rengi
current_theme_color = RGB_COLORS[main_target_color]
skor_animasyon_zamani = 0

animasyon_durumlari: Dict[str, Any] = {}


# --- 4. YARDIMCI SINIF VE FONKSİYONLAR ---
class EMAFilter:
    """MediaPipe koordinatlarındaki titremeleri azaltmak için EMA (Exponential Moving Average) filtresi."""

    def __init__(self, alpha: float = 0.3):
        self.alpha = alpha
        self.smoothed_coords: List[Tuple[float, float]] = []

    def update(
        self, current_coords: List[Tuple[float, float]]
    ) -> List[Tuple[float, float]]:
        if not self.smoothed_coords or len(self.smoothed_coords) != len(current_coords):
            self.smoothed_coords = current_coords
            return self.smoothed_coords

        new_smoothed = []
        for (sx, sy), (cx, cy) in zip(self.smoothed_coords, current_coords):
            nx = self.alpha * cx + (1 - self.alpha) * sx
            ny = self.alpha * cy + (1 - self.alpha) * sy
            new_smoothed.append((nx, ny))

        self.smoothed_coords = new_smoothed
        return self.smoothed_coords


def map_coordinates(
    normalized_coords: List[Tuple[float, float]], width: int, height: int
) -> List[Tuple[float, float]]:
    return [(x * width, y * height) for x, y in normalized_coords]


def draw_glowing_ball(surface, x, y, radius, color_rgb, alpha=255):
    """Kürelere 'Glow' (parlama) efekti vererek profesyonel görünüm sağlar."""
    r, g, b = color_rgb

    # 3 katmanlı parlama (Dıştan içe)
    layers = 4
    for i in range(layers, 0, -1):
        # Dış katmanlar daha geniş ve daha şeffaf
        current_radius = int(radius * (1 + (i * 0.2)))
        current_alpha = int((alpha / layers) * (1 / i))
        pygame.gfxdraw.filled_circle(
            surface, int(x), int(y), current_radius, (r, g, b, current_alpha)
        )

    # Çekirdek (En iç kısım, tam opak)
    pygame.gfxdraw.aacircle(surface, int(x), int(y), int(radius), (r, g, b, alpha))
    pygame.gfxdraw.filled_circle(surface, int(x), int(y), int(radius), (r, g, b, alpha))

    # Merkeze hafif beyaz parlama (Highlight)
    highlight_radius = int(radius * 0.4)
    pygame.gfxdraw.filled_circle(
        surface,
        int(x) - int(radius * 0.2),
        int(y) - int(radius * 0.2),
        highlight_radius,
        (255, 255, 255, int(alpha * 0.6)),
    )


# --- 5. FİZİK YÖNETİCİSİ VE BAŞLATMA ---
manager = BallManager(screen_width=GENISLIK, screen_height=YUKSEKLIK)
ema_filter = EMAFilter(alpha=0.6)  # Daha hızlı tepki için alpha artırıldı (0.3 -> 0.6)
tracker = HandTracker(smoothing_window=3)  # Gecikmeyi azaltmak için pencere küçültüldü (5 -> 3)
cap = cv2.VideoCapture(0)


def on_hit(ball: BallEntity):
    global guncel_skor, can, main_target_color, current_theme_color, skor_animasyon_zamani

    if piyano_sesi:
        piyano_sesi.play()

    # Piano notası çal
    if ball.color in RENK_NOTA_MAP:
        nota = RENK_NOTA_MAP[ball.color]
        if nota in piyano_sesleri:
            try:
                piyano_sesleri[nota].play()
            except Exception as e:
                print(f"⚠️  Nota çalma hatası ({nota}): {e}")

    if ball.color == BallColor.RED:
        # Kırmızı vurulursa can gider
        can -= 1
    elif ball.color == main_target_color:
        # Ana hedef vurulursa puan gelir
        guncel_skor += ball.score_value
        skor_animasyon_zamani = pygame.time.get_ticks()
    else:
        # Nadir bir renk vurulursa, ana tema bu renge dönüşür
        main_target_color = ball.color
        current_theme_color = RGB_COLORS[main_target_color]
        guncel_skor += ball.score_value * 2  # Bonus puan
        skor_animasyon_zamani = pygame.time.get_ticks()

    # Fade-out UI Listesine Ekle
    animasyon_durumlari[ball.id] = {
        "x": ball.x,
        "y": ball.y,
        "radius": ball.radius,
        "color_rgb": RGB_COLORS[ball.color],
        "vurulma_zamani": pygame.time.get_ticks(),
        "surface": pygame.Surface(
            (ball.radius * 4, ball.radius * 4), pygame.SRCALPHA
        ),  # Glow için yüzey geniş tutuldu
    }


# --- 6. ANA DÖNGÜ ---
calisiyor = True
game_over = False

while calisiyor:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            calisiyor = False

    if not game_over:
        # --- ZORLUK VE SPAWN MANTIĞI ---
        gecen_oyun_suresi = (
            pygame.time.get_ticks() - oyun_baslama_zamani
        ) / 1000.0  # Saniye

        # Zamanla spawn sıklığı azalır ama kırmızıların ağırlığı artar
        # Base spawn ihtimali daha düşük (%2 - %3 arası)
        spawn_chance = max(0.015, 0.03 - (gecen_oyun_suresi / 5000))

        if random.random() < spawn_chance:
            zorluk = 1.0 + (gecen_oyun_suresi / 60.0)  # Her dakikada hız katlanır

            # Renk Seçimi (Weighted Random)
            # Zaman ilerledikçe Kırmızı ihtimali artar.
            red_weight = min(0.5, 0.1 + (gecen_oyun_suresi / 200.0))

            # Nadir renk (Main Target ve Kırmızı harici) ihtimali sabittir: %10
            rare_weight = 0.10

            # Kalan ihtimal Main Target'a aittir
            main_weight = 1.0 - (red_weight + rare_weight)

            rnd = random.random()
            if rnd < red_weight:
                secilen_renk = BallColor.RED
            elif rnd < red_weight + rare_weight:
                # Nadir renk seçimi
                uygun_nadirler = [
                    c
                    for c in mevcut_renkler
                    if c != main_target_color and c != BallColor.RED
                ]
                secilen_renk = random.choice(uygun_nadirler)
            else:
                secilen_renk = main_target_color

            # Top Yarıçapı Küçültüldü: 20.0
            manager.spawn_ball(
                radius=20.0,
                base_velocity=3.0,
                difficulty_multiplier=zorluk,
                color=secilen_renk,
            )

        manager.update()

        # --- EL TAKİBİ ENTEGRASYONU ---
        success, frame = cap.read()
        smoothed_pixel_coords = []
        camera_preview_surf = None

        if success:
            frame = cv2.flip(frame, 1)  # Ayna etkisi
            h, w, _ = frame.shape
            all_coords = tracker.get_fingers_positions(frame)

            if all_coords:
                # Kameradan gelen koordinatları oyun ekranına ölçekle
                pixel_coords = []
                for coords in all_coords:
                    norm_x = coords[0] / w
                    norm_y = coords[1] / h
                    pixel_coords.append((norm_x * GENISLIK, norm_y * YUKSEKLIK))
                
                smoothed_pixel_coords = ema_filter.update(pixel_coords)

            # Önizleme için frame'i hazırla
            small_frame = cv2.resize(frame, (160, 120))
            small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            camera_preview_surf = pygame.surfarray.make_surface(small_frame.swapaxes(0, 1))

        PhysicsEngine.check_collisions(
            manager.get_active_balls(), smoothed_pixel_coords, on_hit
        )

        if can <= 0:
            game_over = True

        # 2 dakika sonra game over
        if gecen_oyun_suresi * 1000 >= SURE_LIMITI:
            game_over = True

    # --- ÇİZİM ---
    ekran.fill(ARKA_PLAN_RENGI)

    # Arka planda hedef rengin hafif bir parlaması (Ambiance)
    pygame.gfxdraw.filled_circle(
        ekran, GENISLIK // 2, YUKSEKLIK // 2, 400, (*current_theme_color, 15)
    )

    if game_over:
        bitis_metni = buyuk_font.render("GAME OVER", True, current_theme_color)
        skor_metni = oyun_fontu.render(f"Skor: {guncel_skor}", True, (255, 255, 255))
        ekran.blit(
            bitis_metni,
            bitis_metni.get_rect(center=(GENISLIK // 2, YUKSEKLIK // 2 - 40)),
        )
        ekran.blit(
            skor_metni, skor_metni.get_rect(center=(GENISLIK // 2, YUKSEKLIK // 2 + 40))
        )
    else:
        # 1. Aktif Topları Çiz (Glow Efekti ile)
        # Efektlerin düzgün gözükmesi için surface kullanıyoruz
        for ball in manager.get_active_balls():
            if not ball.is_hit:
                # Topları doğrudan ekrana glow fonksiyonu ile çizemeyiz çünkü alpha blending doğrudan ana ekranda çalışmayabilir.
                # Geçici bir yüzey yaratıp oraya çizmek daha garantidir.
                temp_surface = pygame.Surface(
                    (ball.radius * 4, ball.radius * 4), pygame.SRCALPHA
                )
                draw_glowing_ball(
                    temp_surface,
                    ball.radius * 2,
                    ball.radius * 2,
                    ball.radius,
                    RGB_COLORS[ball.color],
                    alpha=255,
                )
                ekran.blit(
                    temp_surface,
                    (int(ball.x - ball.radius * 2), int(ball.y - ball.radius * 2)),
                )

        # 2. Fade-Out Animasyonları
        su_anki_zaman = pygame.time.get_ticks()
        silinecek_idler = []

        for b_id, anim_data in animasyon_durumlari.items():
            gecen_sure = su_anki_zaman - anim_data["vurulma_zamani"]

            if gecen_sure >= 1000:  # Fade-out süresi biraz kısaltıldı (Hızlı aksiyon)
                silinecek_idler.append(b_id)
            else:
                alpha = 255 - int((gecen_sure / 1000) * 255)
                yuzey = anim_data["surface"]
                yuzey.fill((0, 0, 0, 0))

                yaricap = anim_data["radius"]
                draw_glowing_ball(
                    yuzey,
                    yaricap * 2,
                    yaricap * 2,
                    yaricap,
                    anim_data["color_rgb"],
                    alpha=alpha,
                )

                ekran.blit(
                    yuzey,
                    (
                        int(anim_data["x"] - yaricap * 2),
                        int(anim_data["y"] - yaricap * 2),
                    ),
                )

        for b_id in silinecek_idler:
            del animasyon_durumlari[b_id]

        # 3. Can Göstergesi (Emoji)
        # Font emoji desteklemiyorsa kutu çıkar, ama Windows "Segoe UI Emoji" destekler.
        try:
            can_metni = emoji_font.render("❤️" * can, True, (255, 50, 50))
            ekran.blit(can_metni, (GENISLIK - 150, 20))
        except Exception:
            # Fallback (Eğer emojiler renderlanamazsa)
            can_metni = oyun_fontu.render(f"Can: {can}", True, (255, 50, 50))
            ekran.blit(can_metni, (GENISLIK - 120, 20))

        # Hedef Renk Göstergesi
        hedef_yazi = oyun_fontu.render("HEDEF RENK", True, (200, 200, 200))
        ekran.blit(hedef_yazi, (GENISLIK // 2 - hedef_yazi.get_width() // 2, 10))
        pygame.gfxdraw.filled_circle(ekran, GENISLIK // 2, 55, 10, current_theme_color)
        pygame.gfxdraw.aacircle(ekran, GENISLIK // 2, 55, 10, (255, 255, 255))

        # 4. Tema Renkli ve Animasyonlu Skor Göstergesi
        olcek_carpani = 1.0
        gecen_animasyon_suresi = su_anki_zaman - skor_animasyon_zamani

        if gecen_animasyon_suresi < 300:
            oran = gecen_animasyon_suresi / 300
            olcek_carpani = 1.0 + 0.5 * math.sin(oran * math.pi)

        skor_metni = oyun_fontu.render(
            f"Skor: {guncel_skor}", True, current_theme_color
        )

        if olcek_carpani > 1.0:
            orijinal_genislik, orijinal_yukseklik = skor_metni.get_size()
            yeni_genislik = int(orijinal_genislik * olcek_carpani)
            yeni_yukseklik = int(orijinal_yukseklik * olcek_carpani)
            skor_metni = pygame.transform.smoothscale(
                skor_metni, (yeni_genislik, yeni_yukseklik)
            )

        skor_kutusu = skor_metni.get_rect()
        skor_kutusu.center = (100, 40)

        ekran.blit(skor_metni, skor_kutusu)

        # 5. Kalan Süre Göstergesi
        kalan_sure_ms = max(0, SURE_LIMITI - int(gecen_oyun_suresi * 1000))
        dakika = kalan_sure_ms // 60000
        saniye = (kalan_sure_ms % 60000) // 1000
        sure_metni = oyun_fontu.render(f"⏱️  {dakika}:{saniye:02d}", True, (255, 200, 50))
        ekran.blit(sure_metni, (GENISLIK - 200, YUKSEKLIK - 50))

        # 6. Parmak İmlecini Çiz
        for p_x, p_y in smoothed_pixel_coords:
            pygame.gfxdraw.filled_circle(
                ekran, int(p_x), int(p_y), 12, (255, 255, 255, 180)
            )
            pygame.gfxdraw.aacircle(ekran, int(p_x), int(p_y), 12, (255, 255, 255))
            # Hedef belirteci
            pygame.gfxdraw.aacircle(ekran, int(p_x), int(p_y), 20, current_theme_color)

        # 7. Kamera Önizlemesini Çiz
        if camera_preview_surf:
            # Kenarlık
            pygame.draw.rect(ekran, (100, 100, 100), (8, YUKSEKLIK - 132, 164, 124), 2)
            ekran.blit(camera_preview_surf, (10, YUKSEKLIK - 130))
            # "CANLI" yazısı
            canli_metni = pygame.font.SysFont("Arial", 12, bold=True).render("LIVE CAMERA", True, (255, 0, 0))
            ekran.blit(canli_metni, (15, YUKSEKLIK - 125))

    pygame.display.flip()
    saat.tick(FPS)

pygame.quit()
cap.release()
cv2.destroyAllWindows()
sys.exit()
