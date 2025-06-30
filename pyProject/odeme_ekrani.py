from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from veritabani import veritabani_baglan
from odeme_duzenle_penceresi import OdemeDuzenlePenceresi
import sqlite3

def veritabani_odeme_tipi_kontrol():
    conn = sqlite3.connect("veritabani.db")
    cur = conn.cursor()
    try:
        cur.execute("SELECT odeme_tipi FROM odemeler LIMIT 1")
    except sqlite3.OperationalError:
        cur.execute("ALTER TABLE odemeler ADD COLUMN odeme_tipi TEXT DEFAULT 'Nakit'")
        conn.commit()
    conn.close()

class OdemeEkrani(QWidget):
    def __init__(self, kullanici_id):
        super().__init__()
        veritabani_odeme_tipi_kontrol()
        self.kullanici_id = kullanici_id
        self.setWindowTitle("Ödeme Ekranı")
        self.setGeometry(200, 200, 800, 600)
        self.detay_pencereler = []
        self.init_ui()
        self.yukle()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
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

    def yukle(self):
        self.temizle()
        conn = veritabani_baglan()
        cur = conn.cursor()

        cur.execute("""
            SELECT b.id, b.bina_adi, b.adres
            FROM binalar b
            WHERE b.kullanici_id=?
            ORDER BY b.bina_adi
        """, (self.kullanici_id,))
        binalar = cur.fetchall()

        for bina_id, adi, adres in binalar:
            self.scroll_layout.addWidget(QLabel(f"🏢 {adi} - 📍 {adres}"))

            cur.execute("""
                SELECT d.id, d.kat, d.daire_no
                FROM daireler d
                WHERE d.bina_id=?
                ORDER BY d.kat DESC, d.daire_no
            """, (bina_id,))
            daireler = cur.fetchall()

            katlar = {}
            for daire_id, kat, daire_no in daireler:
                if kat not in katlar:
                    katlar[kat] = []
                katlar[kat].append((daire_id, daire_no))

            for kat in sorted(katlar.keys(), reverse=True):
                hbox = QHBoxLayout()
                hbox.addWidget(QLabel(f"Kat {kat}:"))
                for daire_id, daire_no in katlar[kat]:
                    btn = QPushButton(f"Daire {daire_no}")
                    btn.clicked.connect(self._daire_odeme_handler(daire_id, daire_no))
                    hbox.addWidget(btn)
                self.scroll_layout.addLayout(hbox)

        conn.close()

    def _daire_odeme_handler(self, d_id, d_no):
        return lambda: self.daire_odeme_goster(d_id, d_no)

    def daire_odeme_goster(self, daire_id, daire_no):
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

        detay = QWidget()
        detay.setWindowTitle(f"Daire {daire_no} - Ödeme Detayları")
        layout = QVBoxLayout(detay)

        conn = veritabani_baglan()
        cur = conn.cursor()
        cur.execute("""
            SELECT o.ogrenci_id, g.ad, g.soyad, o.toplam_tutar, o.odenen_tutar, o.odeme_tipi
            FROM odemeler o
            JOIN ogrenciler g ON g.id = o.ogrenci_id
            WHERE g.daire_id=?
        """, (daire_id,))
        ogrenciler = cur.fetchall()
        conn.close()

        if not ogrenciler:
            layout.addWidget(QLabel("📭 Bu daireye ait ödeme bilgisi yok."))
        else:
            for i, (ogr_id, ad, soyad, toplam, odenen, tipi) in enumerate(ogrenciler, start=1):
                kalan = toplam - odenen
                renk = "#2ecc71" if kalan <= 0 else "#e74c3c" if odenen == 0 else "#bdc3c7"
                hbox = QHBoxLayout()
                lbl = QLabel(f"👤 Öğrenci {i}: {ad} {soyad} - Kalan: ₺{kalan:.2f} ({tipi})")
                lbl.setStyleSheet(f"color: {renk}; font-weight: bold;")
                hbox.addWidget(lbl)

                btn = QPushButton("Düzenle")
                btn.clicked.connect(lambda _, oid=ogr_id, isim=f"{ad} {soyad}": self.odeme_duzenle(oid, isim))
                hbox.addWidget(btn)
                layout.addLayout(hbox)

        detay.setLayout(layout)
        detay.show()
        self.detay_pencereler.append(detay)

    def odeme_duzenle(self, ogrenci_id, ad_soyad):
        self.odeme_pencere = OdemeDuzenlePenceresi(ogrenci_id, ad_soyad, self.yukle)
        self.odeme_pencere.show()
