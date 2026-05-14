import math
import uuid
import random
from typing import List, Tuple, Callable


class BallColor:
    BLUE = "Mavi"
    GREEN = "Yeşil"
    YELLOW = "Sarı"
    PURPLE = "Mor"
    BLACK = "Siyah"
    WHITE = "Beyaz"
    RED = "Kırmızı"


# Renklere göre atanmış puanlar
COLOR_SCORES = {
    BallColor.BLUE: 5,
    BallColor.GREEN: 4,
    BallColor.YELLOW: 3,
    BallColor.PURPLE: 7,
    BallColor.BLACK: 2,
    BallColor.WHITE: 1,
    BallColor.RED: -1,  # Can eksiltme veya eksi puan durumu için
}


class BallEntity:
    """
    Oyundaki her bir 'top' objesini temsil eden veri yapısı.
    """

    def __init__(self, x: float, y: float, radius: float, color: str, velocity: float):
        self.id: str = str(uuid.uuid4())
        self.x: float = x  # Normalleştirilmiş veya piksel cinsinden koordinat
        self.y: float = y
        self.radius: float = radius
        self.color: str = color
        self.velocity: float = velocity
        self.score_value: int = COLOR_SCORES.get(color, 0)
        self.is_hit: bool = False
        self.opacity: float = 1.0


class PhysicsEngine:
    """
    Fizik ve Çarpışma algılamalarından sorumlu motor (High Cohesion).
    UI'dan bağımsız saf matematiksel işlemleri içerir.
    """

    @staticmethod
    def _calculate_euclidean_distance(
        x1: float, y1: float, x2: float, y2: float
    ) -> float:
        """İki nokta arasındaki Öklid mesafesini hesaplar."""
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    @staticmethod
    def check_collisions(
        balls: List[BallEntity],
        finger_tip_coords: List[Tuple[float, float]],
        on_hit_callback: Callable[[BallEntity], None],
    ) -> None:
        """
        Ekranda olan tüm topları ve parmak ucu koordinatlarını karşılaştırır.
        Eğer çarpışma varsa on_hit_callback (Observer Pattern) tetiklenir.
        """
        for ball in balls:
            if ball.is_hit:
                continue  # Zaten vurulmuşsa kontrol etmeye gerek yok

            for finger_x, finger_y in finger_tip_coords:
                distance = PhysicsEngine._calculate_euclidean_distance(
                    ball.x, ball.y, finger_x, finger_y
                )

                # Çarpışma gerçekleşti mi? (d < radius + buffer)
                # Hassasiyeti artırmak için 15 piksellik bir tolerans (buffer) eklendi.
                if distance < (ball.radius + 15):
                    ball.is_hit = True
                    # 3. Modülün (fade-out) asenkron fonksiyonunu tetiklemek için callback çağrılır
                    on_hit_callback(ball)
                    break  # Bir top aynı anda sadece 1 kere hit olabilir


class BallManager:
    """
    Topların doğmasını (spawn) ve hareket etmesini (update) yöneten sınıf.
    """

    def __init__(self, screen_width: float, screen_height: float):
        self.balls: List[BallEntity] = []
        self.screen_width: float = screen_width
        self.screen_height: float = screen_height

    def spawn_ball(
        self,
        radius: float = 20.0,
        base_velocity: float = 2.0,
        difficulty_multiplier: float = 1.0,
        color: str = None,
    ) -> None:
        """
        Ekranın en tepesinde (y=0) rastgele x koordinatında bir top oluşturur.
        Zorluk seviyesi arttıkça velocity artabilir. Yeni doğan topun diğer toplarla örtüşmemesi sağlanır.
        """
        max_attempts = 10
        for _ in range(max_attempts):
            x = random.uniform(radius, self.screen_width - radius)
            y = 0.0

            # Örtüşme Kontrolü (Overlap Prevention)
            overlap = False
            for existing_ball in self.balls:
                # Sadece yeni doğan topun (y=0) etrafındakilerle mesafe kontrolü
                dist = math.sqrt(
                    (x - existing_ball.x) ** 2 + (y - existing_ball.y) ** 2
                )
                if dist < (radius + existing_ball.radius + 5):  # 5 piksel güvenlik payı
                    overlap = True
                    break

            if not overlap:
                # Güvenli bir nokta bulundu
                if color is None:
                    color = random.choice(list(COLOR_SCORES.keys()))

                velocity = base_velocity * difficulty_multiplier
                new_ball = BallEntity(
                    x=x, y=y, radius=radius, color=color, velocity=velocity
                )
                self.balls.append(new_ball)
                break  # Başarıyla doğdu, döngüden çık

    def update(self) -> None:
        """
        Tüm aktif topların y koordinatını velocity kadar artırır.
        Ekranın altına düşen topları bellekten temizler (Array leak önleme).
        """
        active_balls = []
        for ball in self.balls:
            ball.y += ball.velocity

            # Top ekranın tamamen altına inmediyse tutmaya devam et
            if ball.y - ball.radius < self.screen_height:
                active_balls.append(ball)
            # Ekran altına inenler otomatik olarak listeye dahil edilmez ve bellekten düşer.

        self.balls = active_balls

    def get_active_balls(self) -> List[BallEntity]:
        """Sadece çizilmesi gereken topları döndürür."""
        return self.balls
