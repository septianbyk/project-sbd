import mysql.connector
from mysql.connector import Error

# Konfigurasi Koneksi Database
DB_CONFIG = {
    'host': 'localhost',
    'database': 'db_sekolah',
    'user': 'root',
    'password': ''  # Sesuaikan jika MySQL kamu menggunakan password
}

def create_connection():
    """Membuat koneksi ke database MySQL"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"[ERROR] Gagal menyambungkan ke MySQL: {e}")
    return None