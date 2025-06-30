from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from bina_ekle_penceresi import BinaEklePenceresi
from binalarim_penceresi import BinalarimPenceresi
from odeme_ekrani import OdemeEkrani

class KullaniciPaneli(QWidget):
    def __init__(self, kullanici):
        super().__init__()
        self.user = kullanici
        self.setWindowTitle(f"Kullanıcı Paneli - {self.user[1]} {self.user[2]}")
        self.setGeometry(200, 200, 400, 400)

        self.bina_ekle_penceresi = None
        self.binalarim_penceresi = None
        self.odeme_penceresi = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        lbl_hoşgeldin = QLabel(f"Hoşgeldiniz, {self.user[1]} {self.user[2]}")
        lbl_hoşgeldin.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(lbl_hoşgeldin)

        self.btn_yeni_bina = QPushButton("Yeni Bina Ekle")
        self.btn_yeni_bina.clicked.connect(self.yeni_bina_ac)
        layout.addWidget(self.btn_yeni_bina)

        self.btn_binalarim = QPushButton("Binalarımı Göster")
        self.btn_binalarim.clicked.connect(self.binalarimi_ac)
        layout.addWidget(self.btn_binalarim)

        self.btn_odeme = QPushButton("Ödeme Ekranı")
        self.btn_odeme.clicked.connect(self.odeme_ekrani_ac)
        layout.addWidget(self.btn_odeme)

        self.setLayout(layout)

    def yeni_bina_ac(self):
        self.bina_ekle_penceresi = BinaEklePenceresi(self.user[0])
        self.bina_ekle_penceresi.show()

    def binalarimi_ac(self):
        self.binalarim_penceresi = BinalarimPenceresi(self.user[0])
        self.binalarim_penceresi.show()

    def odeme_ekrani_ac(self):
        self.odeme_penceresi = OdemeEkrani(self.user[0])
        self.odeme_penceresi.show()

    def binalari_yenile(self):
        if self.binalarim_penceresi:
            self.binalarim_penceresi.yukle()
