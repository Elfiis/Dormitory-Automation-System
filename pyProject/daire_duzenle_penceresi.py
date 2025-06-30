from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QHBoxLayout
)
from veritabani import veritabani_baglan


class DaireDuzenlePenceresi(QWidget):
    def __init__(self, daire_id, daire_no, yenile_callback=None):
        super().__init__()
        self.daire_id = daire_id
        self.daire_no = daire_no
        self.yenile_callback = yenile_callback  # doluluk güncellemesi için
        self.setWindowTitle(f"Daire {daire_no} Detayları")
        self.setGeometry(400, 400, 400, 500)
        self.init_ui()
        self.yukle()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        self.lbl_baslik = QLabel(f"🛏️ Daire {self.daire_no} Öğrencileri")
        self.layout.addWidget(self.lbl_baslik)

        self.lbl_doluluk = QLabel()
        self.layout.addWidget(self.lbl_doluluk)

        self.kapasite_input = QLineEdit()
        self.kapasite_input.setPlaceholderText("Kapasite")
        self.layout.addWidget(self.kapasite_input)

        self.fiyat_input = QLineEdit()
        self.fiyat_input.setPlaceholderText("Fiyat (₺)")
        self.layout.addWidget(self.fiyat_input)

        self.btn_kaydet = QPushButton("Daire Bilgilerini Kaydet")
        self.btn_kaydet.clicked.connect(self.kaydet)
        self.layout.addWidget(self.btn_kaydet)

        self.lbl_ogr = QLabel("👥 Öğrenciler:")
        self.layout.addWidget(self.lbl_ogr)

        self.ogrenci_kutular = []

        self.btn_yeni_ogrenci = QPushButton("➕ Yeni Öğrenci Ekle")
        self.btn_yeni_ogrenci.clicked.connect(self.yeni_ogrenci_ekle)
        self.layout.addWidget(self.btn_yeni_ogrenci)

    def yukle(self):
        self.temizle_ogrenciler()
        conn = veritabani_baglan()
        cur = conn.cursor()
        cur.execute("SELECT kapasite, fiyat FROM daireler WHERE id=?", (self.daire_id,))
        result = cur.fetchone()
        if not result:
            self.close()
            return
        kapasite, fiyat = result
        self.kapasite_input.setText(str(kapasite))
        self.fiyat_input.setText(str(fiyat))

        cur.execute("SELECT id, ad, soyad FROM ogrenciler WHERE daire_id=?", (self.daire_id,))
        ogrenciler = cur.fetchall()
        conn.close()

        mevcut = len(ogrenciler)
        self.lbl_doluluk.setText(f"Kapasite: {kapasite} | Mevcut: {mevcut} | Boş: {kapasite - mevcut}")

        for oid, ad, soyad in ogrenciler:
            hbox = QHBoxLayout()
            lbl = QLabel(f"{ad} {soyad}")
            sil_btn = QPushButton("🗑️ Sil")
            sil_btn.clicked.connect(lambda _, oid=oid: self.ogrenci_sil(oid))
            hbox.addWidget(lbl)
            hbox.addWidget(sil_btn)
            self.layout.addLayout(hbox)
            self.ogrenci_kutular.append(hbox)

    def temizle_ogrenciler(self):
        for kutu in self.ogrenci_kutular:
            for i in reversed(range(kutu.count())):
                widget = kutu.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
        self.ogrenci_kutular.clear()

    def ogrenci_sil(self, ogr_id):
        cevap = QMessageBox.question(self, "Silme", "Öğrenci silinsin mi?")
        if cevap.name == "Yes":
            conn = veritabani_baglan()
            cur = conn.cursor()
            cur.execute("DELETE FROM ogrenciler WHERE id=?", (ogr_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Silindi", "Öğrenci silindi.")
            self.yukle()
            if self.yenile_callback:
                self.yenile_callback()

    def yeni_ogrenci_ekle(self):
        conn = veritabani_baglan()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM ogrenciler WHERE daire_id=?", (self.daire_id,))
        mevcut = cur.fetchone()[0]
        cur.execute("SELECT kapasite FROM daireler WHERE id=?", (self.daire_id,))
        kapasite = cur.fetchone()[0]
        if mevcut >= kapasite:
            QMessageBox.warning(self, "Dolu", "Daire kapasitesi dolu!")
            return
        cur.execute("""
            INSERT INTO ogrenciler (ad, soyad, okul, sinif, daire_id)
            VALUES (?, ?, ?, ?, ?)
        """, ("Ad", "Soyad", "Okul", "Sınıf", self.daire_id))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Eklendi", "Yeni öğrenci eklendi (düzenleyin).")
        self.yukle()
        if self.yenile_callback:
            self.yenile_callback()

    def kaydet(self):
        try:
            kapasite = int(self.kapasite_input.text())
            fiyat = float(self.fiyat_input.text())
        except:
            QMessageBox.warning(self, "Hata", "Geçerli sayı girin.")
            return
        conn = veritabani_baglan()
        cur = conn.cursor()
        cur.execute("UPDATE daireler SET kapasite=?, fiyat=? WHERE id=?", (kapasite, fiyat, self.daire_id))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Başarılı", "Daire bilgileri güncellendi.")
        self.yukle()
        if self.yenile_callback:
            self.yenile_callback()
