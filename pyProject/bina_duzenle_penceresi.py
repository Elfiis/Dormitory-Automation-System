from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton,
    QScrollArea, QFormLayout, QLineEdit, QHBoxLayout, QMessageBox)
from veritabani import veritabani_baglan

class BinaDuzenlePenceresi(QWidget):
    def __init__(self, kullanici_id):
        super().__init__()
        self.kullanici_id = kullanici_id
        self.setWindowTitle("Bina Güncelle")
        self.setGeometry(350, 350, 600, 600)
        self.init_ui()
        self.binalari_yukle()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.cmb_binalar = QComboBox()
        self.cmb_binalar.currentIndexChanged.connect(self.daireleri_yukle)
        self.layout.addWidget(self.cmb_binalar)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll)

        self.btn_kaydet = QPushButton("Güncelle")
        self.btn_kaydet.clicked.connect(self.guncelle)
        self.layout.addWidget(self.btn_kaydet)

        self.setLayout(self.layout)

    def binalari_yukle(self):
        conn = veritabani_baglan()
        cur = conn.cursor()
        cur.execute("SELECT id, bina_adi FROM binalar WHERE kullanici_id=?", (self.kullanici_id,))
        self.binalar = cur.fetchall()
        conn.close()

        self.cmb_binalar.clear()
        for bina_id, bina_adi in self.binalar:
            self.cmb_binalar.addItem(bina_adi, bina_id)

    def daireleri_yukle(self):
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        bina_index = self.cmb_binalar.currentIndex()
        if bina_index == -1:
            return
        bina_id = self.cmb_binalar.currentData()

        conn = veritabani_baglan()
        cur = conn.cursor()
        cur.execute("SELECT id, daire_no, kat, kapasite, fiyat FROM daireler WHERE bina_id=? ORDER BY kat, daire_no", (bina_id,))
        self.daireler = cur.fetchall()
        conn.close()

        self.inputlar = {}
        for daire_id, daire_no, kat, kapasite, fiyat in self.daireler:
            form = QFormLayout()
            form.addRow(QLabel(f"Daire {daire_no} (Kat {kat})"))

            kapasite_input = QLineEdit(str(kapasite))
            fiyat_input = QLineEdit(str(fiyat))

            form.addRow("Kapasite:", kapasite_input)
            form.addRow("Fiyat (₺):", fiyat_input)

            self.scroll_layout.addLayout(form)
            self.inputlar[daire_id] = (kapasite_input, fiyat_input)

    def guncelle(self):
        bina_id = self.cmb_binalar.currentData()
        conn = veritabani_baglan()
        cur = conn.cursor()
        try:
            for daire_id, (kapasite_input, fiyat_input) in self.inputlar.items():
                try:
                    kapasite = int(kapasite_input.text())
                except:
                    kapasite = 2
                try:
                    fiyat = float(fiyat_input.text())
                except:
                    fiyat = 10000
                cur.execute("UPDATE daireler SET kapasite=?, fiyat=? WHERE id=?", (kapasite, fiyat, daire_id))
            conn.commit()
            QMessageBox.information(self, "Başarılı", "Daireler güncellendi!")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))
        finally:
            conn.close()
