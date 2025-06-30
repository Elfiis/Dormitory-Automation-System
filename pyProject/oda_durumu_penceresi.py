from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QScrollArea, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from veritabani import veritabani_baglan
from ogrenci_ekle_penceresi import OgrenciEklePenceresi


class OdaDurumuPenceresi(QWidget):
    def __init__(self, kullanici_id):
        super().__init__()
        self.kullanici_id = kullanici_id
        self.setWindowTitle("Bina Şeması - Oda Durumu")
        self.setGeometry(100, 100, 1000, 700)
        self.init_ui()
        self.binalari_goster()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        self.lbl_baslik = QLabel("🏢 Binalar")
        self.lbl_baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_baslik.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.layout.addWidget(self.lbl_baslik)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

    def temizle(self):
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

    def binalari_goster(self):
        self.temizle()
        conn = veritabani_baglan()
        cur = conn.cursor()
        cur.execute("SELECT id, bina_adi FROM binalar WHERE kullanici_id=?", (self.kullanici_id,))
        binalar = cur.fetchall()
        conn.close()

        for bina_id, bina_adi in binalar:
            lbl = QLabel(f"🏢 {bina_adi}")
            lbl.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
            self.scroll_layout.addWidget(lbl)
            self.bina_semasi_olustur(bina_id)

    def bina_semasi_olustur(self, bina_id):
        conn = veritabani_baglan()
        cur = conn.cursor()
        cur.execute("""
            SELECT d.id, d.kat, d.daire_no, d.kapasite,
                   (SELECT COUNT(*) FROM ogrenciler WHERE daire_id = d.id)
            FROM daireler d
            WHERE d.bina_id = ?
            ORDER BY d.kat DESC, d.daire_no
        """, (bina_id,))
        daireler = cur.fetchall()
        conn.close()

        katlar = {}
        for daire_id, kat, daire_no, kapasite, mevcut in daireler:
            if kat not in katlar:
                katlar[kat] = []
            katlar[kat].append((daire_id, daire_no, kapasite, mevcut))

        for kat in sorted(katlar.keys(), reverse=True):  # en üst kat en üstte
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(f"Kat {kat}:"))

            for daire_id, daire_no, kapasite, mevcut in katlar[kat]:
                renk = "#2ecc71" if mevcut == 0 else "#e74c3c" if mevcut >= kapasite else "#bdc3c7"
                btn = QPushButton(f"{daire_no}\n{mevcut}/{kapasite}")
                btn.setFixedSize(100, 60)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {renk};
                        color: white;
                        font-weight: bold;
                        border-radius: 8px;
                    }}
                    QPushButton:hover {{
                        background-color: #444;
                    }}
                """)
                btn.clicked.connect(lambda _, d_id=daire_id, d_no=daire_no: self.daire_detay_goster(d_id, d_no))
                hbox.addWidget(btn)

            container = QWidget()
            container.setLayout(hbox)
            self.scroll_layout.addWidget(container)

    def daire_detay_goster(self, daire_id, daire_no):
        detay = QWidget()
        detay.setWindowTitle(f"Daire {daire_no} Detayları")
        layout = QVBoxLayout(detay)

        conn = veritabani_baglan()
        cur = conn.cursor()
        cur.execute("SELECT kapasite FROM daireler WHERE id=?", (daire_id,))
        kapasite = cur.fetchone()[0]
        cur.execute("SELECT ad, soyad, okul, sinif FROM ogrenciler WHERE daire_id=?", (daire_id,))
        ogrenciler = cur.fetchall()
        conn.close()

        mevcut = len(ogrenciler)
        kalan = kapasite - mevcut
        layout.addWidget(QLabel(f"Kapasite: {kapasite} | Mevcut: {mevcut} | Boş: {kalan}"))

        if ogrenciler:
            for ad, soyad, okul, sinif in ogrenciler:
                layout.addWidget(QLabel(f"• {ad} {soyad} - {okul} / {sinif}"))
        else:
            layout.addWidget(QLabel("📭 Bu dairede öğrenci yok."))

        btn_ekle = QPushButton("👤 Yeni Öğrenci Ekle")
        btn_ekle.clicked.connect(lambda: self.ogrenci_ekle_penceresi_ac(daire_id, daire_no))
        layout.addWidget(btn_ekle)

        detay.setLayout(layout)
        detay.show()

    def ogrenci_ekle_penceresi_ac(self, daire_id, daire_no):
        self.ogrenci_ekle = OgrenciEklePenceresi(daire_id, daire_no)
        self.ogrenci_ekle.show()
