from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QScrollArea, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from veritabani import veritabani_baglan

class OdaDurumuPenceresi(QWidget):
    def __init__(self, kullanici_id):
        super().__init__()
        self.kullanici_id = kullanici_id
        self.setWindowTitle("Oda Doluluk Durumu")
        self.setGeometry(200, 200, 800, 600)
        self.init_ui()
        self.binalari_goster()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)

        self.layout.addWidget(QLabel("🏢 Binalarınız"))
        self.layout.addWidget(self.scroll)

    def binalari_goster(self):
        conn = veritabani_baglan()
        cur = conn.cursor()

        cur.execute("SELECT id, bina_adi FROM binalar WHERE kullanici_id=?", (self.kullanici_id,))
        binalar = cur.fetchall()

        for bina_id, bina_adi in binalar:
            btn = QPushButton(f"🏢 {bina_adi}")
            btn.setStyleSheet("padding: 10px; font-weight: bold;")
            btn.clicked.connect(lambda _, bid=bina_id, badi=bina_adi: self.katlari_goster(bid, badi))
            self.scroll_layout.addWidget(btn)

        conn.close()

    def katlari_goster(self, bina_id, bina_adi):
        kat_pencere = QWidget()
        kat_pencere.setWindowTitle(f"{bina_adi} - Katlar")
        kat_layout = QVBoxLayout(kat_pencere)

        conn = veritabani_baglan()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT kat FROM daireler WHERE bina_id=? ORDER BY kat", (bina_id,))
        katlar = cur.fetchall()
        conn.close()

        for (kat_no,) in katlar:
            btn = QPushButton(f"Kat {kat_no}")
            btn.clicked.connect(lambda _, k=kat_no: self.daireleri_goster(bina_id, bina_adi, k))
            kat_layout.addWidget(btn)

        kat_pencere.setLayout(kat_layout)
        kat_pencere.show()

    def daireleri_goster(self, bina_id, bina_adi, kat_no):
        daire_pencere = QWidget()
        daire_pencere.setWindowTitle(f"{bina_adi} - {kat_no}. Kat Daireleri")
        daire_layout = QVBoxLayout(daire_pencere)

        conn = veritabani_baglan()
        cur = conn.cursor()

        cur.execute("""
            SELECT d.id, d.daire_no, d.kapasite,
            (SELECT COUNT(*) FROM ogrenciler o WHERE o.daire_id = d.id) AS mevcut
            FROM daireler d
            WHERE d.bina_id = ? AND d.kat = ?
            ORDER BY d.daire_no
        """, (bina_id, kat_no))

        daireler = cur.fetchall()
        conn.close()

        kutu_layout = QHBoxLayout()
        for daire_id, daire_no, kapasite, mevcut in daireler:
            btn = QPushButton(f"Daire {daire_no}\n{mevcut}/{kapasite}")
            renk = "#4CAF50"  # yeşil
            if mevcut == kapasite:
                renk = "#e74c3c"  # kırmızı
            elif mevcut > 0:
                renk = "#bdc3c7"  # gri

            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {renk};
                    color: white;
                    padding: 10px;
                    border-radius: 8px;
                    font-size: 14px;
                    min-width: 100px;
                    min-height: 60px;
                }}
            """)
            btn.clicked.connect(lambda _, id=daire_id, no=daire_no: self.ogrencileri_goster(id, no))
            kutu_layout.addWidget(btn)

        daire_layout.addLayout(kutu_layout)
        daire_pencere.setLayout(daire_layout)
        daire_pencere.show()

    def ogrencileri_goster(self, daire_id, daire_no):
        ogr_pencere = QWidget()
        ogr_pencere.setWindowTitle(f"Daire {daire_no} - Öğrenciler")
        layout = QVBoxLayout(ogr_pencere)

        conn = veritabani_baglan()
        cur = conn.cursor()
        cur.execute("SELECT ad, soyad, okul, sinif FROM ogrenciler WHERE daire_id=?", (daire_id,))
        ogrenciler = cur.fetchall()
        conn.close()

        if not ogrenciler:
            layout.addWidget(QLabel("📭 Bu daireye ait öğrenci bulunmamaktadır."))
        else:
            for ad, soyad, okul, sinif in ogrenciler:
                layout.addWidget(QLabel(f"👤 {ad} {soyad} - {okul} / {sinif}"))

        ogr_pencere.setLayout(layout)
        ogr_pencere.show()
