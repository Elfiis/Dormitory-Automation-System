from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit
from veritabani import veritabani_baglan
from kayit_penceresi import KayitPenceresi
from kullanici_paneli import KullaniciPaneli

class Pencere(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Giriş / Kayıt")
        self.setGeometry(100, 100, 400, 200)

        self.conn = veritabani_baglan()
        self.cursor = self.conn.cursor()

        self.eposta = QLineEdit()
        self.eposta.setPlaceholderText("E-posta")

        self.sifre = QLineEdit()
        self.sifre.setPlaceholderText("Şifre")
        self.sifre.setEchoMode(QLineEdit.EchoMode.Password)

        self.btn_giris = QPushButton("Giriş Yap")
        self.btn_giris.clicked.connect(self.giris)

        self.btn_kayit = QPushButton("Kayıt Ol")
        self.btn_kayit.clicked.connect(self.kayit_ac)

        self.lbl = QLabel("Lütfen giriş yapın veya kayıt olun.")

        layout = QVBoxLayout()
        layout.addWidget(self.eposta)
        layout.addWidget(self.sifre)
        layout.addWidget(self.btn_giris)
        layout.addWidget(self.btn_kayit)
        layout.addWidget(self.lbl)
        self.setLayout(layout)

    def giris(self):
        eposta = self.eposta.text().strip()
        sifre = self.sifre.text().strip()

        self.cursor.execute("SELECT * FROM kullanicilar WHERE eposta=? AND sifre=?", (eposta, sifre))
        user = self.cursor.fetchone()

        if user:
            self.lbl.setText("Giriş başarılı!")
            self.kullanici_panel = KullaniciPaneli(user)
            self.kullanici_panel.show()
            self.close()
        else:
            self.lbl.setText("Hatalı e-posta veya şifre.")

    def kayit_ac(self):
        self.kayit_penceresi = KayitPenceresi()
        self.kayit_penceresi.show()

    def closeEvent(self, event):
        self.conn.close()
        event.accept()
