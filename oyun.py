import pygame
import sys
import math

# --- 1. BAŞLANGIÇ VE AYARLAR ---
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

GENISLIK = 800
YUKSEKLIK = 600
FPS = 60
ARKA_PLAN_RENGI = (30, 30, 30)

ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK))
pygame.display.set_caption("El Takibi - Yaşam Döngüsü ve UI Modülü")
saat = pygame.time.Clock()

pygame.mixer.set_num_channels(8)
try:
    piyano_sesi = pygame.mixer.Sound("piyano-kısa.mp3")
except FileNotFoundError:
    piyano_sesi = None

# --- YENİ: ARAYÜZ (UI) VE SKOR DEĞİŞKENLERİ ---
pygame.font.init()
oyun_fontu = pygame.font.SysFont("Consolas", 24, bold=True)
guncel_skor = 0
skor_animasyon_zamani = 0  # Animasyonun ne zaman başladığını tutacak


# --- 3. YAŞAM DÖNGÜSÜ: DAİRE SINIFI ---
class Daire:
    def __init__(self, x, y, yaricap=40):
        self.x = x
        self.y = y
        self.yaricap = yaricap
        self.renk = (255, 100, 100)
        self.durum = "aktif"
        self.alpha = 255
        self.vurulma_zamani = 0
        self.yuzey = pygame.Surface((yaricap * 2, yaricap * 2), pygame.SRCALPHA)

    def vuruldu(self):
        if self.durum == "aktif":
            self.durum = "siliniyor"
            self.vurulma_zamani = pygame.time.get_ticks()
            if piyano_sesi:
                piyano_sesi.play()
            return True  # Vurulma başarılıysa True dön
        return False

    def guncelle(self):
        if self.durum == "siliniyor":
            su_anki_zaman = pygame.time.get_ticks()
            gecen_sure = su_anki_zaman - self.vurulma_zamani

            if gecen_sure >= 2000:
                self.durum = "silindi"
                self.alpha = 0
            else:
                self.alpha = 255 - int((gecen_sure / 2000) * 255)

    def ciz(self, ana_ekran):
        if self.durum != "silindi":
            self.yuzey.fill((0, 0, 0, 0))  # Yüzeyi her karede temizle

            # 1. KATMAN: İç Dolgu (Orijinal alphanın %20'si kadar şeffaf bir kırmızı)
            ic_alpha = int(self.alpha * 0.2)
            pygame.draw.circle(self.yuzey, (*self.renk, ic_alpha), (self.yaricap, self.yaricap), self.yaricap)

            # 2. KATMAN: Dış Halka (Tam belirgin renk, 3 piksel kalınlık)
            pygame.draw.circle(self.yuzey, (*self.renk, self.alpha), (self.yaricap, self.yaricap), self.yaricap, 3)

            # Yüzeyi ana ekrana kopyala
            ana_ekran.blit(self.yuzey, (self.x - self.yaricap, self.y - self.yaricap))


# Mock Veri Üretimi
daireler = [
    Daire(200, 300),
    Daire(400, 300),
    Daire(600, 300)
]

calisiyor = True

# --- 4. ANA DÖNGÜ ---
while calisiyor:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            calisiyor = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            fare_x, fare_y = event.pos
            for daire in daireler:
                if daire.durum == "aktif":
                    mesafe = math.sqrt((fare_x - daire.x) ** 2 + (fare_y - daire.y) ** 2)
                    if mesafe <= daire.yaricap:
                        # Eğer daire başarıyla vurulduysa skoru 10 artır
                        if daire.vuruldu():
                            guncel_skor += 10
                            skor_animasyon_zamani = pygame.time.get_ticks()

    # 1. Ekranı temizle
    ekran.fill(ARKA_PLAN_RENGI)

    # 2. Daireleri güncelle ve çiz
    for daire in daireler:
        daire.guncelle()
        daire.ciz(ekran)

    # --- 3. YENİ: ANİMASYONLU SKORU EKRANA ÇİZME ---
    su_anki_zaman = pygame.time.get_ticks()
    olcek_carpani = 1.0  # Varsayılan boyut
    gecen_animasyon_suresi = su_anki_zaman - skor_animasyon_zamani

    # Eğer puan alınmasının üzerinden 300 milisaniyeden az zaman geçtiyse yazıyı büyüt
    if gecen_animasyon_suresi < 300:
        oran = gecen_animasyon_suresi / 300
        # Sinüs dalgası kullanarak yumuşak bir şişme/inme efekti yaratıyoruz
        olcek_carpani = 1.0 + 0.5 * math.sin(oran * math.pi)

    # Önce yazıyı normal boyutta hazırla
    skor_metni = oyun_fontu.render(f"Skor: {guncel_skor}", True, (255, 255, 255))

    # Ölçek çarpanı 1.0'dan büyükse yazıyı o oranda büyüt
    if olcek_carpani > 1.0:
        orijinal_genislik, orijinal_yukseklik = skor_metni.get_size()
        yeni_genislik = int(orijinal_genislik * olcek_carpani)
        yeni_yukseklik = int(orijinal_yukseklik * olcek_carpani)
        skor_metni = pygame.transform.smoothscale(skor_metni, (yeni_genislik, yeni_yukseklik))

    # Yazıyı sol üstten değil, "Merkezden" sabitleyerek ekrana koy.
    # Böylece yazı büyürken sağa veya aşağı kaymaz, olduğu yerde patlar.
    skor_kutusu = skor_metni.get_rect()
    skor_kutusu.center = (100, 40)  # Ekrandaki sabit merkezi (X=100, Y=40)

    ekran.blit(skor_metni, skor_kutusu)
    # -----------------------------------------------

    # 4. Ekranı tazele ve FPS'i bekle
    pygame.display.flip()
    saat.tick(FPS)

pygame.quit()
sys.exit()