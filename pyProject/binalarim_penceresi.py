from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QHBoxLayout, QPushButton, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from veritabani import veritabani_baglan
from daire_duzenle_penceresi import DaireDuzenlePenceresi

class BinalarimPenceresi(QWidget):
    def __init__(self, kid):
        super().__init__()
        self.kid = kid
        self.setWindowTitle("Binalarım")
        self.setGeometry(150, 150, 900, 600)
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
            SELECT id, bina_adi, adres
            FROM binalar
            WHERE kullanici_id=?
            ORDER BY bina_adi
        """, (self.kid,))
        binalar = cur.fetchall()

        for bina_id, adi, adres in binalar:
            self.bina_semasi_olustur(cur, bina_id, adi, adres)

        conn.close()

    def bina_semasi_olustur(self, cur, bina_id, adi, adres):
        self.scroll_layout.addWidget(QLabel(f"🏢 {adi} - 📍 {adres}"))
        cur.execute("""
            SELECT d.id, d.kat, d.daire_no, d.kapasite, d.fiyat,
                   (SELECT COUNT(*) FROM ogrenciler WHERE daire_id = d.id)
            FROM daireler d
            WHERE d.bina_id = ?
            ORDER BY d.kat DESC, d.daire_no
        """, (bina_id,))
        daireler = cur.fetchall()

        katlar = {}
        for daire_id, kat, daire_no, kapasite, fiyat, mevcut in daireler:
            if kat not in katlar:
                katlar[kat] = []
            katlar[kat].append((daire_id, daire_no, kapasite, mevcut, fiyat))

        for kat in sorted(katlar.keys(), reverse=True):
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(f"Kat {kat}:"))

            for daire_id, daire_no, kapasite, mevcut, fiyat in katlar[kat]:
                renk = "#2ecc71" if mevcut == 0 else "#e74c3c" if mevcut >= kapasite else "#bdc3c7"
                btn = QPushButton(f"{daire_no}\n{mevcut}/{kapasite}\n₺{fiyat:.0f}")
                btn.setFixedSize(100, 70)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {renk};
                        color: white;
                        font-weight: bold;
                        border-radius: 8px;
                    }}
                """)
                btn.clicked.connect(lambda _, d_id=daire_id, d_no=daire_no: self.daire_duzenle(d_id, d_no))
                hbox.addWidget(btn)

            btn_ekle = QPushButton("➕")
            btn_ekle.setFixedSize(40, 40)
            btn_ekle.clicked.connect(lambda _, b_id=bina_id, k=kat: self.yeni_daire_ekle(b_id, k))
            hbox.addWidget(btn_ekle)

            container = QWidget()
            container.setLayout(hbox)
            self.scroll_layout.addWidget(container)

    def daire_duzenle(self, daire_id, daire_no):
        self.ddp = DaireDuzenlePenceresi(daire_id, daire_no, self.yukle)
        self.ddp.show()

    def yeni_daire_ekle(self, bina_id, kat):
        daire_no, ok1 = QInputDialog.getInt(self, "Yeni Daire", f"{kat}. kat için daire numarası:", kat * 100 + 1)
        if not ok1:
            return
        kapasite, ok2 = QInputDialog.getInt(self, "Kapasite", "Daire kapasitesi:", 2)
        if not ok2:
            return
        fiyat, ok3 = QInputDialog.getDouble(self, "Fiyat", "Daire fiyatı (₺):", 10000.0, 0.0, 1000000.0, 2)
        if not ok3:
            return

        try:
            conn = veritabani_baglan()
            cur = conn.cursor()
            cur.execute("INSERT INTO daireler (bina_id, daire_no, kat, kapasite, fiyat) VALUES (?, ?, ?, ?, ?)",
                        (bina_id, daire_no, kat, kapasite, fiyat))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Başarılı", "Yeni daire eklendi.")
            self.yukle()
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))
