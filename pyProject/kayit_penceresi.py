import re
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from veritabani import veritabani_baglan

class KayitPenceresi(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kayıt Ol")
        self.setGeometry(150, 150, 400, 280)
        self.conn = veritabani_baglan()
        self.cur = self.conn.cursor()

        self.ad = QLineEdit()
        self.ad.setPlaceholderText("Ad")

        self.soyad = QLineEdit()
        self.soyad.setPlaceholderText("Soyad")

        self.yas = QLineEdit()
        self.yas.setPlaceholderText("Yaş")

        self.eposta = QLineEdit()
        self.eposta.setPlaceholderText("E-posta")

        self.adres = QLineEdit()
        self.adres.setPlaceholderText("Adres")

        self.sifre = QLineEdit()
        self.sifre.setPlaceholderText("Şifre")
        self.sifre.setEchoMode(QLineEdit.EchoMode.Password)

        self.btn = QPushButton("Kayıt Ol")
        self.btn.clicked.connect(self.kayit)

        self.lbl = QLabel()

        lay = QVBoxLayout()
        for w in [self.ad, self.soyad, self.yas, self.eposta, self.adres, self.sifre, self.btn, self.lbl]:
            lay.addWidget(w)
        self.setLayout(lay)

    def kayit(self):
        a = self.ad.text().strip()
        so = self.soyad.text().strip()
        y = self.yas.text().strip()
        e = self.eposta.text().strip()
        ad = self.adres.text().strip()
        s = self.sifre.text()

        if not all([a, so, y, e, ad, s]):
            return self.lbl.setText("Tüm alanlar dolu olmalı.")
        if not y.isdigit():
            return self.lbl.setText("Yaş sayısal olmalı.")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", e):
            return self.lbl.setText("Geçerli e-posta girin.")
        if len(s) < 8 or not re.search(r"[A-Z]", s) or not re.search(r"\W", s):
            return self.lbl.setText("Şifre 8+, BÜYÜK harf ve özel karakter içermeli.")

        try:
            self.cur.execute(
                "INSERT INTO kullanicilar(ad, soyad, yas, eposta, adres, sifre) VALUES(?, ?, ?, ?, ?, ?)",
                (a, so, int(y), e, ad, s)
            )
            self.conn.commit()
            self.lbl.setText("Kayıt başarılı!")
        except Exception as ex:
            self.lbl.setText("Bu e-posta zaten kayıtlı.")

    def closeEvent(self, event):
        self.conn.close()
        event.accept()
