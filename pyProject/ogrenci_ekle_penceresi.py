from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from veritabani import veritabani_baglan

class OgrenciEklePenceresi(QWidget):
    def __init__(self, daire_id, daire_no, yenile_fonksiyonu=None):
        super().__init__()
        self.daire_id = daire_id
        self.daire_no = daire_no
        self.yenile_fonksiyonu = yenile_fonksiyonu
        self.setWindowTitle(f"Daire {daire_no} - Yeni Öğrenci")
        self.setGeometry(400, 400, 350, 400)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        self.lbl = QLabel(f"Yeni Öğrenci Ekle (Daire {self.daire_no})")
        self.layout.addWidget(self.lbl)

        self.ad_input = QLineEdit()
        self.ad_input.setPlaceholderText("Ad")
        self.layout.addWidget(self.ad_input)

        self.soyad_input = QLineEdit()
        self.soyad_input.setPlaceholderText("Soyad")
        self.layout.addWidget(self.soyad_input)

        self.tel_input = QLineEdit()
        self.tel_input.setPlaceholderText("Telefon")
        self.layout.addWidget(self.tel_input)

        self.okul_input = QLineEdit()
        self.okul_input.setPlaceholderText("Okul Adı")
        self.layout.addWidget(self.okul_input)

        self.sinif_input = QLineEdit()
        self.sinif_input.setPlaceholderText("Sınıf")
        self.layout.addWidget(self.sinif_input)

        self.kimlik_input = QLineEdit()
        self.kimlik_input.setPlaceholderText("Kimlik No")
        self.layout.addWidget(self.kimlik_input)

        self.kaydet_btn = QPushButton("Kaydet")
        self.kaydet_btn.clicked.connect(self.kaydet)
        self.layout.addWidget(self.kaydet_btn)

    def kaydet(self):
        ad = self.ad_input.text().strip()
        soyad = self.soyad_input.text().strip()
        tel = self.tel_input.text().strip()
        okul = self.okul_input.text().strip()
        sinif = self.sinif_input.text().strip()
        kimlik = self.kimlik_input.text().strip()

        if not all([ad, soyad, tel, okul, sinif, kimlik]):
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen tüm alanları doldurun.")
            return

        conn = veritabani_baglan()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO ogrenciler (ad, soyad, telefon, okul, sinif, kimlik, daire_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (ad, soyad, tel, okul, sinif, kimlik, self.daire_id))
        ogrenci_id = cur.lastrowid

        # Ödeme kaydı oluştur
        cur.execute("""
            INSERT INTO odemeler (ogrenci_id, toplam_tutar, odenen_tutar, odeme_tipi)
            VALUES (?, 0, 0, 'Nakit')
        """, (ogrenci_id,))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Başarılı", "Öğrenci başarıyla eklendi.")

        if self.yenile_fonksiyonu:
            self.yenile_fonksiyonu()

        self.close()
