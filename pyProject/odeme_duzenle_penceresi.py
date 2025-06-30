from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox
from veritabani import veritabani_baglan

class OdemeDuzenlePenceresi(QWidget):
    def __init__(self, ogrenci_id, ad_soyad, yenile_callback=None):
        super().__init__()
        self.ogrenci_id = ogrenci_id
        self.ad_soyad = ad_soyad
        self.yenile_callback = yenile_callback
        self.setWindowTitle(f"{ad_soyad} - Ödeme Düzenle")
        self.setGeometry(400, 400, 350, 250)
        self.init_ui()
        self.yukle()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        self.lbl = QLabel(f"Öğrenci: {self.ad_soyad}")
        self.layout.addWidget(self.lbl)

        self.txt_toplam = QLineEdit()
        self.txt_toplam.setPlaceholderText("Toplam Tutar (₺)")
        self.layout.addWidget(self.txt_toplam)

        self.txt_odenen = QLineEdit()
        self.txt_odenen.setPlaceholderText("Ödenen Tutar (₺)")
        self.layout.addWidget(self.txt_odenen)

        self.cmb_tip = QComboBox()
        self.cmb_tip.addItems(["Nakit", "Taksit", "Kredi Kartı", "Tümü"])
        self.layout.addWidget(self.cmb_tip)

        self.btn_kaydet = QPushButton("Kaydet")
        self.btn_kaydet.clicked.connect(self.kaydet)
        self.layout.addWidget(self.btn_kaydet)

    def yukle(self):
        conn = veritabani_baglan()
        cur = conn.cursor()
        cur.execute("SELECT toplam_tutar, odenen_tutar, odeme_tipi FROM odemeler WHERE ogrenci_id=?", (self.ogrenci_id,))
        veri = cur.fetchone()
        conn.close()

        if veri:
            toplam, odenen, tip = veri
            self.txt_toplam.setText(str(toplam))
            self.txt_odenen.setText(str(odenen))
            index = self.cmb_tip.findText(tip)
            if index != -1:
                self.cmb_tip.setCurrentIndex(index)

    def kaydet(self):
        try:
            toplam = float(self.txt_toplam.text())
            odenen = float(self.txt_odenen.text())
            tip = self.cmb_tip.currentText()
        except:
            QMessageBox.warning(self, "Hata", "Tutar alanları geçerli sayı olmalı.")
            return

        if odenen > toplam:
            QMessageBox.warning(self, "Hata", "Ödenen, toplamdan fazla olamaz.")
            return

        conn = veritabani_baglan()
        cur = conn.cursor()
        cur.execute("""
            UPDATE odemeler
            SET toplam_tutar=?, odenen_tutar=?, odeme_tipi=?
            WHERE ogrenci_id=?
        """, (toplam, odenen, tip, self.ogrenci_id))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Başarılı", "Ödeme bilgisi güncellendi.")
        self.close()
        if self.yenile_callback:
            self.yenile_callback()
