from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,
    QScrollArea, QHBoxLayout
)
from veritabani import veritabani_baglan

class BinaEklePenceresi(QWidget):
    def __init__(self, kullanici_id):
        super().__init__()
        self.kullanici_id = kullanici_id
        self.setWindowTitle("Yeni Bina Ekle")
        self.setGeometry(300, 300, 500, 600)
        self.kat_girisleri = []
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.bina_adi = QLineEdit()
        self.bina_adi.setPlaceholderText("Bina Adı")
        self.adres = QLineEdit()
        self.adres.setPlaceholderText("Adres")
        self.kat_sayisi = QLineEdit()
        self.kat_sayisi.setPlaceholderText("Kat Sayısı")
        self.kat_sayisi.textChanged.connect(self.kat_olustur)

        self.layout.addWidget(self.bina_adi)
        self.layout.addWidget(self.adres)
        self.layout.addWidget(self.kat_sayisi)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll)

        self.btn_kaydet = QPushButton("Kaydet")
        self.btn_kaydet.clicked.connect(self.kaydet)
        self.layout.addWidget(self.btn_kaydet)

        self.setLayout(self.layout)

    def kat_olustur(self):
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.kat_girisleri.clear()

        try:
            kat_sayi = int(self.kat_sayisi.text())
        except:
            return

        for kat in range(1, kat_sayi + 1):
            kat_widget = QWidget()
            kat_layout = QVBoxLayout(kat_widget)

            lbl = QLabel(f"{kat}. Kat - Daire Sayısı:")
            daire_input = QLineEdit()
            daire_input.setPlaceholderText("Daire Sayısı")
            daire_input.textChanged.connect(self.daire_olustur)
            kat_layout.addWidget(lbl)
            kat_layout.addWidget(daire_input)

            self.scroll_layout.addWidget(kat_widget)
            self.kat_girisleri.append((kat, daire_input, kat_layout, []))

    def daire_olustur(self):
        for kat, daire_input, kat_layout, daire_kutular in self.kat_girisleri:
            for kutu in daire_kutular:
                kutu.setParent(None)
            daire_kutular.clear()

            try:
                adet = int(daire_input.text())
                if adet <= 0:
                    continue
            except:
                continue

            for i in range(adet):
                daire_no = kat * 100 + i + 1
                hbox = QHBoxLayout()
                lbl = QLabel(f"Daire {daire_no} Fiyat:")
                fiyat_input = QLineEdit()
                fiyat_input.setPlaceholderText("₺")
                fiyat_input.setText("10000")
                hbox.addWidget(lbl)
                hbox.addWidget(fiyat_input)

                h_widget = QWidget()
                h_widget.setLayout(hbox)
                kat_layout.addWidget(h_widget)
                daire_kutular.append(fiyat_input)

    def kaydet(self):
        bina_adi = self.bina_adi.text().strip()
        adres = self.adres.text().strip()
        try:
            kat_sayi = int(self.kat_sayisi.text())
        except:
            QMessageBox.warning(self, "Hata", "Kat sayısı geçerli değil.")
            return

        if not bina_adi or not adres:
            QMessageBox.warning(self, "Hata", "Bina adı ve adres boş olamaz.")
            return

        conn = veritabani_baglan()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO binalar (kullanici_id, bina_adi, adres, kat_sayisi, daire_sayisi)
                VALUES (?, ?, ?, ?, ?)
            """, (self.kullanici_id, bina_adi, adres, kat_sayi, 0))
            bina_id = cur.lastrowid

            toplam_daire = 0
            for kat, daire_input, layout, daire_kutular in self.kat_girisleri:
                try:
                    adet = int(daire_input.text())
                    if adet <= 0:
                        continue
                except:
                    continue

                for i in range(adet):
                    daire_no = kat * 100 + i + 1
                    try:
                        fiyat = float(daire_kutular[i].text())
                    except:
                        fiyat = 10000

                    cur.execute("""
                        INSERT INTO daireler (bina_id, daire_no, kat, kapasite, fiyat)
                        VALUES (?, ?, ?, ?, ?)
                    """, (bina_id, str(daire_no), kat, 2, fiyat))
                    toplam_daire += 1

            cur.execute("UPDATE binalar SET daire_sayisi=? WHERE id=?", (toplam_daire, bina_id))
            conn.commit()
            QMessageBox.information(self, "Başarılı", "Bina ve daireler başarıyla kaydedildi.")
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))
        finally:
            conn.close()
