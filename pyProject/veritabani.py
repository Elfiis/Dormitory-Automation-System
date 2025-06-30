import sqlite3
import os

def veritabani_baglan():
    db_file = "veritabani.db"

    try:
        if os.path.exists(db_file):
            test_conn = sqlite3.connect(db_file)
            test_conn.close()
    except:
        pass

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Kullanıcılar
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad TEXT NOT NULL,
            soyad TEXT NOT NULL,
            yas INTEGER NOT NULL,
            eposta TEXT NOT NULL UNIQUE,
            adres TEXT,
            sifre TEXT NOT NULL
        )
    """)

    # Binalar
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS binalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_id INTEGER NOT NULL,
            bina_adi TEXT NOT NULL,
            adres TEXT NOT NULL,
            kat_sayisi INTEGER NOT NULL,
            daire_sayisi INTEGER NOT NULL,
            FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(id)
        )
    """)

    # Daireler
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daireler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bina_id INTEGER NOT NULL,
            daire_no TEXT NOT NULL,
            kat INTEGER NOT NULL,
            kapasite INTEGER DEFAULT 2,
            fiyat REAL DEFAULT 10000,
            FOREIGN KEY (bina_id) REFERENCES binalar(id)
        )
    """)

    # Eğer kapasite alanı yoksa ekle
    try:
        cursor.execute("SELECT kapasite FROM daireler LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE daireler ADD COLUMN kapasite INTEGER DEFAULT 2")

    # Eğer fiyat alanı yoksa ekle
    try:
        cursor.execute("SELECT fiyat FROM daireler LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE daireler ADD COLUMN fiyat REAL DEFAULT 10000")

    # Öğrenciler
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ogrenciler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            daire_id INTEGER NOT NULL,
            ad TEXT NOT NULL,
            soyad TEXT NOT NULL,
            okul TEXT,
            sinif TEXT,
            telefon TEXT,
            tc_kimlik TEXT,
            FOREIGN KEY (daire_id) REFERENCES daireler(id)
        )
    """)

    # Ödemeler
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS odemeler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ogrenci_id INTEGER NOT NULL,
            toplam_tutar REAL NOT NULL DEFAULT 0,
            odenen_tutar REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (ogrenci_id) REFERENCES ogrenciler(id)
        )
    """)

    conn.commit()
    return conn
