from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QHBoxLayout, QPushButton
)
from PyQt6.QtCore import Qt
from veritabani import veritabani_baglan
from ogrenci_ekle_penceresi import OgrenciEklePenceresi


class OgrenciEklemeSema(QWidget):
    def __init__(self, kullanici_id):
        super().__init__()
        self.kullanici_id = kullanici_id
        self.setWindowTitle("Öğrenci Ekleme - Bina Şeması")
        self.setGeometry(150, 150, 700, 700)
        self.init_ui()
        self.binalari_goster()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        self.lbl_baslik = QLabel("🏢 Binalar")
        self.lbl_baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_baslik.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.layout.addWidget(self.lbl_baslik)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll.setWidget(self.scroll_widget)

        self.layout.addWidget(self.scroll)

    def temizle(self):
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def binalari_goster(self):
        self.temizle()
        conn = veritabani_baglan()
        cur = conn.cursor()

        cur.execute("SELECT id, bina_adi FROM binalar WHERE kullanici_id=?", (self.kullanici_id,))
        binalar = cur.fetchall()

        for bina_id, bina_adi in binalar:
            self.scroll_layout.addWidget(QLabel(f"🏢 {bina_adi}"))
            self.bina_semasi_olustur(cur, bina_id)

        conn.close()

    def bina_semasi_olustur(self, cur, bina_id):
        cur.execute("""
            SELECT d.id, d.kat, d.daire_no, d.kapasite,
                   (SELECT COUNT(*) FROM ogrenciler WHERE daire_id = d.id)
            FROM daireler d
            WHERE d.bina_id = ?
            ORDER BY d.kat DESC, d.daire_no
        """, (bina_id,))
        daireler = cur.fetchall()

        katlar = {}
        for daire_id, kat, daire_no, kapasite, mevcut in daireler:
            if kat not in katlar:
                katlar[kat] = []
            katlar[kat].append((daire_id, daire_no, kapasite, mevcut))

        for kat in sorted(katlar.keys(), reverse=True):
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
                btn.clicked.connect(lambda _, did=daire_id, dno=daire_no: self.ogrenci_ekle(did, dno))
                hbox.addWidget(btn)

            container = QWidget()
            container.setLayout(hbox)
            self.scroll_layout.addWidget(container)

    def ogrenci_ekle(self, daire_id, daire_no):
        self.ogr_ekle = OgrenciEklePenceresi(daire_id, daire_no)
        self.ogr_ekle.show()
