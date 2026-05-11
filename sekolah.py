import mysql.connector
from mysql.connector import errorcode
import os

# ============================================================
#   SISTEM MANAJEMEN DATA SEKOLAH
#   Mata Kuliah  : Praktikum Sistem Basis Data
#   Topik        : Sekolah
#   Database     : MySQL
#   Entitas      : Siswa, Guru, Mata Pelajaran
# ============================================================

# ─────────────────────────────────────────────
#  KONFIGURASI KONEKSI MySQL
#  Sesuaikan host, user, password dengan
#  konfigurasi MySQL di komputer Anda
# ─────────────────────────────────────────────
DB_CONFIG = {
    "host"    : "localhost",
    "user"    : "root",
    "password": "",           # ganti sesuai password MySQL Anda
    "database": "db_sekolah",
    "charset" : "utf8mb4",
}


def get_connection():
    """Membuka dan mengembalikan koneksi ke MySQL."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("  [!] Username atau password MySQL salah.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("  [!] Database 'db_sekolah' belum ada. Jalankan init_database() terlebih dahulu.")
        else:
            print(f"  [!] Koneksi gagal: {err}")
        return None


def init_database():
    """Membuat database dan tabel jika belum ada."""
    try:
        # Koneksi tanpa memilih database dulu
        conn = mysql.connector.connect(
            host    =DB_CONFIG["host"],
            user    =DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            charset =DB_CONFIG["charset"],
        )
        cursor = conn.cursor()

        # Buat database
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS db_sekolah "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cursor.execute("USE db_sekolah")

        # ── Tabel GURU (dibuat lebih dulu karena direferensi mapel) ──
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS guru (
                id_guru     INT          NOT NULL AUTO_INCREMENT,
                nip         VARCHAR(20)  NOT NULL,
                nama        VARCHAR(100) NOT NULL,
                jabatan     VARCHAR(50)  NOT NULL,
                no_telepon  VARCHAR(15)  DEFAULT NULL,
                email       VARCHAR(100) DEFAULT NULL,
                PRIMARY KEY (id_guru),
                UNIQUE KEY uq_nip (nip)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ── Tabel SISWA ──
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS siswa (
                id_siswa      INT          NOT NULL AUTO_INCREMENT,
                nis           VARCHAR(15)  NOT NULL,
                nama          VARCHAR(100) NOT NULL,
                kelas         VARCHAR(15)  NOT NULL,
                jenis_kelamin ENUM('L','P') NOT NULL,
                alamat        TEXT         DEFAULT NULL,
                PRIMARY KEY (id_siswa),
                UNIQUE KEY uq_nis (nis)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ── Tabel MATA PELAJARAN ──
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mata_pelajaran (
                id_mapel    INT              NOT NULL AUTO_INCREMENT,
                kode_mapel  VARCHAR(10)      NOT NULL,
                nama_mapel  VARCHAR(100)     NOT NULL,
                id_guru     INT              NOT NULL,
                kkm         TINYINT UNSIGNED NOT NULL DEFAULT 75,
                PRIMARY KEY (id_mapel),
                UNIQUE KEY uq_kode (kode_mapel),
                CONSTRAINT fk_mapel_guru
                    FOREIGN KEY (id_guru) REFERENCES guru (id_guru)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("  [OK] Database dan tabel berhasil diinisialisasi.")

    except mysql.connector.Error as err:
        print(f"  [!] Gagal inisialisasi database: {err}")


# ─────────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────────
def cetak_garis(char="─", panjang=65):
    print(char * panjang)

def cetak_judul(teks):
    cetak_garis("═")
    print(f"  {teks}")
    cetak_garis("═")

def pause():
    input("\n  Tekan Enter untuk melanjutkan...")


# ══════════════════════════════════════════════
#  CRUD SISWA
# ══════════════════════════════════════════════

def view_siswa():
    cetak_judul("DATA SISWA")
    conn = get_connection()
    if not conn: pause(); return
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM siswa ORDER BY id_siswa")
    rows = cursor.fetchall()
    cursor.close(); conn.close()

    if not rows:
        print("  Belum ada data siswa.")
    else:
        print(f"  {'ID':<5} {'NIS':<12} {'Nama':<26} {'Kelas':<10} {'JK':<5} {'Alamat'}")
        cetak_garis()
        for r in rows:
            print(f"  {r[0]:<5} {r[1]:<12} {r[2]:<26} {r[3]:<10} {r[4]:<5} {r[5] or '-'}")
    pause()


def insert_siswa():
    cetak_judul("TAMBAH DATA SISWA")
    nis    = input("  NIS               : ").strip()
    nama   = input("  Nama              : ").strip()
    kelas  = input("  Kelas             : ").strip()
    jk     = input("  Jenis Kelamin (L/P): ").strip().upper()
    alamat = input("  Alamat            : ").strip()

    if not all([nis, nama, kelas, jk]):
        print("  [!] NIS, Nama, Kelas, dan Jenis Kelamin wajib diisi.")
        pause(); return
    if jk not in ("L", "P"):
        print("  [!] Jenis kelamin harus L atau P.")
        pause(); return

    try:
        conn = get_connection()
        if not conn: pause(); return
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO siswa (nis, nama, kelas, jenis_kelamin, alamat) VALUES (%s,%s,%s,%s,%s)",
            (nis, nama, kelas, jk, alamat or None)
        )
        conn.commit()
        cursor.close(); conn.close()
        print(f"  [OK] Siswa '{nama}' berhasil ditambahkan.")
    except mysql.connector.IntegrityError:
        print("  [!] NIS sudah terdaftar. Gunakan NIS yang berbeda.")
    except mysql.connector.Error as err:
        print(f"  [!] Error: {err}")
    pause()


def update_siswa():
    cetak_judul("UBAH DATA SISWA")
    view_siswa()
    try:
        id_siswa = int(input("  Masukkan ID Siswa yang ingin diubah : "))
    except ValueError:
        print("  [!] ID tidak valid."); pause(); return

    conn = get_connection()
    if not conn: pause(); return
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM siswa WHERE id_siswa = %s", (id_siswa,))
    row = cursor.fetchone()
    cursor.close(); conn.close()

    if not row:
        print("  [!] Data tidak ditemukan."); pause(); return

    print(f"\n  Data saat ini: NIS={row[1]} | Nama={row[2]} | Kelas={row[3]} | JK={row[4]} | Alamat={row[5]}")
    print("  (Kosongkan field jika tidak ingin mengubah)\n")

    nis    = input(f"  NIS           [{row[1]}] : ").strip() or row[1]
    nama   = input(f"  Nama          [{row[2]}] : ").strip() or row[2]
    kelas  = input(f"  Kelas         [{row[3]}] : ").strip() or row[3]
    jk_in  = input(f"  Jenis Kelamin [{row[4]}] : ").strip().upper()
    jk     = jk_in if jk_in in ("L", "P") else row[4]
    alamat = input(f"  Alamat        [{row[5]}] : ").strip() or row[5]

    try:
        conn = get_connection()
        if not conn: pause(); return
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE siswa SET nis=%s, nama=%s, kelas=%s, jenis_kelamin=%s, alamat=%s WHERE id_siswa=%s",
            (nis, nama, kelas, jk, alamat, id_siswa)
        )
        conn.commit()
        cursor.close(); conn.close()
        print("  [OK] Data siswa berhasil diperbarui.")
    except mysql.connector.IntegrityError:
        print("  [!] NIS sudah digunakan siswa lain.")
    except mysql.connector.Error as err:
        print(f"  [!] Error: {err}")
    pause()


def delete_siswa():
    cetak_judul("HAPUS DATA SISWA")
    view_siswa()
    try:
        id_siswa = int(input("  Masukkan ID Siswa yang ingin dihapus : "))
    except ValueError:
        print("  [!] ID tidak valid."); pause(); return

    conn = get_connection()
    if not conn: pause(); return
    cursor = conn.cursor()
    cursor.execute("SELECT nama FROM siswa WHERE id_siswa = %s", (id_siswa,))
    row = cursor.fetchone()

    if not row:
        cursor.close(); conn.close()
        print("  [!] Data tidak ditemukan."); pause(); return

    konfirmasi = input(f"  Yakin ingin menghapus '{row[0]}'? (y/n) : ").strip().lower()
    if konfirmasi == "y":
        cursor.execute("DELETE FROM siswa WHERE id_siswa = %s", (id_siswa,))
        conn.commit()
        print(f"  [OK] Data '{row[0]}' berhasil dihapus.")
    else:
        print("  Penghapusan dibatalkan.")
    cursor.close(); conn.close()
    pause()


# ══════════════════════════════════════════════
#  CRUD GURU
# ══════════════════════════════════════════════

def view_guru():
    cetak_judul("DATA GURU")
    conn = get_connection()
    if not conn: pause(); return
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM guru ORDER BY id_guru")
    rows = cursor.fetchall()
    cursor.close(); conn.close()

    if not rows:
        print("  Belum ada data guru.")
    else:
        print(f"  {'ID':<5} {'NIP':<15} {'Nama':<26} {'Jabatan':<22} {'Telepon':<15} {'Email'}")
        cetak_garis()
        for r in rows:
            print(f"  {r[0]:<5} {r[1]:<15} {r[2]:<26} {r[3]:<22} {r[4] or '-':<15} {r[5] or '-'}")
    pause()


def insert_guru():
    cetak_judul("TAMBAH DATA GURU")
    nip     = input("  NIP       : ").strip()
    nama    = input("  Nama      : ").strip()
    jabatan = input("  Jabatan   : ").strip()
    telepon = input("  No. Telp  : ").strip()
    email   = input("  Email     : ").strip()

    if not all([nip, nama, jabatan]):
        print("  [!] NIP, Nama, dan Jabatan wajib diisi.")
        pause(); return

    try:
        conn = get_connection()
        if not conn: pause(); return
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO guru (nip, nama, jabatan, no_telepon, email) VALUES (%s,%s,%s,%s,%s)",
            (nip, nama, jabatan, telepon or None, email or None)
        )
        conn.commit()
        cursor.close(); conn.close()
        print(f"  [OK] Guru '{nama}' berhasil ditambahkan.")
    except mysql.connector.IntegrityError:
        print("  [!] NIP sudah terdaftar.")
    except mysql.connector.Error as err:
        print(f"  [!] Error: {err}")
    pause()


def update_guru():
    cetak_judul("UBAH DATA GURU")
    view_guru()
    try:
        id_guru = int(input("  Masukkan ID Guru yang ingin diubah : "))
    except ValueError:
        print("  [!] ID tidak valid."); pause(); return

    conn = get_connection()
    if not conn: pause(); return
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM guru WHERE id_guru = %s", (id_guru,))
    row = cursor.fetchone()
    cursor.close(); conn.close()

    if not row:
        print("  [!] Data tidak ditemukan."); pause(); return

    print(f"\n  Data saat ini: NIP={row[1]} | Nama={row[2]} | Jabatan={row[3]}")
    print("  (Kosongkan field jika tidak ingin mengubah)\n")

    nip     = input(f"  NIP       [{row[1]}] : ").strip() or row[1]
    nama    = input(f"  Nama      [{row[2]}] : ").strip() or row[2]
    jabatan = input(f"  Jabatan   [{row[3]}] : ").strip() or row[3]
    telepon = input(f"  No. Telp  [{row[4]}] : ").strip() or row[4]
    email   = input(f"  Email     [{row[5]}] : ").strip() or row[5]

    try:
        conn = get_connection()
        if not conn: pause(); return
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE guru SET nip=%s, nama=%s, jabatan=%s, no_telepon=%s, email=%s WHERE id_guru=%s",
            (nip, nama, jabatan, telepon, email, id_guru)
        )
        conn.commit()
        cursor.close(); conn.close()
        print("  [OK] Data guru berhasil diperbarui.")
    except mysql.connector.IntegrityError:
        print("  [!] NIP sudah digunakan guru lain.")
    except mysql.connector.Error as err:
        print(f"  [!] Error: {err}")
    pause()


def delete_guru():
    cetak_judul("HAPUS DATA GURU")
    view_guru()
    try:
        id_guru = int(input("  Masukkan ID Guru yang ingin dihapus : "))
    except ValueError:
        print("  [!] ID tidak valid."); pause(); return

    conn = get_connection()
    if not conn: pause(); return
    cursor = conn.cursor()
    cursor.execute("SELECT nama FROM guru WHERE id_guru = %s", (id_guru,))
    row = cursor.fetchone()

    if not row:
        cursor.close(); conn.close()
        print("  [!] Data tidak ditemukan."); pause(); return

    # Cek FK — guru masih mengajar?
    cursor.execute("SELECT COUNT(*) FROM mata_pelajaran WHERE id_guru = %s", (id_guru,))
    if cursor.fetchone()[0] > 0:
        cursor.close(); conn.close()
        print("  [!] Guru masih terhubung ke Mata Pelajaran. Hapus mapelnya terlebih dahulu.")
        pause(); return

    konfirmasi = input(f"  Yakin menghapus '{row[0]}'? (y/n) : ").strip().lower()
    if konfirmasi == "y":
        cursor.execute("DELETE FROM guru WHERE id_guru = %s", (id_guru,))
        conn.commit()
        print(f"  [OK] Data '{row[0]}' berhasil dihapus.")
    else:
        print("  Penghapusan dibatalkan.")
    cursor.close(); conn.close()
    pause()


# ══════════════════════════════════════════════
#  CRUD MATA PELAJARAN
# ══════════════════════════════════════════════

def view_mapel():
    cetak_judul("DATA MATA PELAJARAN")
    conn = get_connection()
    if not conn: pause(); return
    cursor = conn.cursor()
    cursor.execute("""
        SELECT mp.id_mapel, mp.kode_mapel, mp.nama_mapel,
               g.nama AS nama_guru, mp.kkm
        FROM   mata_pelajaran mp
        JOIN   guru g ON mp.id_guru = g.id_guru
        ORDER  BY mp.id_mapel
    """)
    rows = cursor.fetchall()
    cursor.close(); conn.close()

    if not rows:
        print("  Belum ada data mata pelajaran.")
    else:
        print(f"  {'ID':<5} {'Kode':<10} {'Nama Mapel':<26} {'Pengampu':<26} {'KKM'}")
        cetak_garis()
        for r in rows:
            print(f"  {r[0]:<5} {r[1]:<10} {r[2]:<26} {r[3]:<26} {r[4]}")
    pause()


def insert_mapel():
    cetak_judul("TAMBAH MATA PELAJARAN")
    conn = get_connection()
    if not conn: pause(); return
    cursor = conn.cursor()
    cursor.execute("SELECT id_guru, nip, nama FROM guru ORDER BY id_guru")
    guru_list = cursor.fetchall()
    cursor.close(); conn.close()

    if not guru_list:
        print("  [!] Belum ada data guru. Tambahkan guru terlebih dahulu.")
        pause(); return

    print("  Daftar Guru Tersedia:")
    for g in guru_list:
        print(f"    ID={g[0]}  NIP={g[1]}  Nama={g[2]}")

    kode = input("\n  Kode Mapel  : ").strip()
    nama = input("  Nama Mapel  : ").strip()
    try:
        id_guru = int(input("  ID Guru     : "))
        kkm     = int(input("  KKM (0-100) : "))
    except ValueError:
        print("  [!] ID Guru dan KKM harus berupa angka."); pause(); return

    if not all([kode, nama]):
        print("  [!] Kode dan Nama Mapel wajib diisi."); pause(); return

    try:
        conn = get_connection()
        if not conn: pause(); return
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO mata_pelajaran (kode_mapel, nama_mapel, id_guru, kkm) VALUES (%s,%s,%s,%s)",
            (kode, nama, id_guru, kkm)
        )
        conn.commit()
        cursor.close(); conn.close()
        print(f"  [OK] Mata pelajaran '{nama}' berhasil ditambahkan.")
    except mysql.connector.IntegrityError as err:
        if err.errno == errorcode.ER_DUP_ENTRY:
            print("  [!] Kode mapel sudah digunakan.")
        else:
            print("  [!] ID Guru tidak valid (Foreign Key error).")
    except mysql.connector.Error as err:
        print(f"  [!] Error: {err}")
    pause()


def update_mapel():
    cetak_judul("UBAH MATA PELAJARAN")
    view_mapel()
    try:
        id_mapel = int(input("  Masukkan ID Mapel yang ingin diubah : "))
    except ValueError:
        print("  [!] ID tidak valid."); pause(); return

    conn = get_connection()
    if not conn: pause(); return
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mata_pelajaran WHERE id_mapel = %s", (id_mapel,))
    row = cursor.fetchone()
    cursor.close(); conn.close()

    if not row:
        print("  [!] Data tidak ditemukan."); pause(); return

    print(f"\n  Data saat ini: Kode={row[1]} | Nama={row[2]} | ID Guru={row[3]} | KKM={row[4]}")
    print("  (Kosongkan field jika tidak ingin mengubah)\n")

    kode = input(f"  Kode Mapel [{row[1]}] : ").strip() or row[1]
    nama = input(f"  Nama Mapel [{row[2]}] : ").strip() or row[2]
    try:
        ig_in  = input(f"  ID Guru    [{row[3]}] : ").strip()
        id_guru = int(ig_in) if ig_in else row[3]
        kkm_in = input(f"  KKM        [{row[4]}] : ").strip()
        kkm    = int(kkm_in) if kkm_in else row[4]
    except ValueError:
        print("  [!] ID Guru dan KKM harus berupa angka."); pause(); return

    try:
        conn = get_connection()
        if not conn: pause(); return
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE mata_pelajaran SET kode_mapel=%s, nama_mapel=%s, id_guru=%s, kkm=%s WHERE id_mapel=%s",
            (kode, nama, id_guru, kkm, id_mapel)
        )
        conn.commit()
        cursor.close(); conn.close()
        print("  [OK] Data mata pelajaran berhasil diperbarui.")
    except mysql.connector.IntegrityError:
        print("  [!] Kode mapel sudah digunakan atau ID Guru tidak valid.")
    except mysql.connector.Error as err:
        print(f"  [!] Error: {err}")
    pause()


def delete_mapel():
    cetak_judul("HAPUS MATA PELAJARAN")
    view_mapel()
    try:
        id_mapel = int(input("  Masukkan ID Mapel yang ingin dihapus : "))
    except ValueError:
        print("  [!] ID tidak valid."); pause(); return

    conn = get_connection()
    if not conn: pause(); return
    cursor = conn.cursor()
    cursor.execute("SELECT nama_mapel FROM mata_pelajaran WHERE id_mapel = %s", (id_mapel,))
    row = cursor.fetchone()

    if not row:
        cursor.close(); conn.close()
        print("  [!] Data tidak ditemukan."); pause(); return

    konfirmasi = input(f"  Yakin menghapus '{row[0]}'? (y/n) : ").strip().lower()
    if konfirmasi == "y":
        cursor.execute("DELETE FROM mata_pelajaran WHERE id_mapel = %s", (id_mapel,))
        conn.commit()
        print(f"  [OK] Mata pelajaran '{row[0]}' berhasil dihapus.")
    else:
        print("  Penghapusan dibatalkan.")
    cursor.close(); conn.close()
    pause()


# ─────────────────────────────────────────────
#  MENU
# ─────────────────────────────────────────────
def menu_siswa():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        cetak_judul("MENU SISWA")
        print("  1. Lihat Data Siswa")
        print("  2. Tambah Siswa")
        print("  3. Ubah Siswa")
        print("  4. Hapus Siswa")
        print("  0. Kembali")
        cetak_garis()
        pilihan = input("  Pilih : ").strip()
        if    pilihan == "1": view_siswa()
        elif  pilihan == "2": insert_siswa()
        elif  pilihan == "3": update_siswa()
        elif  pilihan == "4": delete_siswa()
        elif  pilihan == "0": break
        else: print("  Pilihan tidak valid."); pause()


def menu_guru():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        cetak_judul("MENU GURU")
        print("  1. Lihat Data Guru")
        print("  2. Tambah Guru")
        print("  3. Ubah Guru")
        print("  4. Hapus Guru")
        print("  0. Kembali")
        cetak_garis()
        pilihan = input("  Pilih : ").strip()
        if    pilihan == "1": view_guru()
        elif  pilihan == "2": insert_guru()
        elif  pilihan == "3": update_guru()
        elif  pilihan == "4": delete_guru()
        elif  pilihan == "0": break
        else: print("  Pilihan tidak valid."); pause()


def menu_mapel():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        cetak_judul("MENU MATA PELAJARAN")
        print("  1. Lihat Data Mata Pelajaran")
        print("  2. Tambah Mata Pelajaran")
        print("  3. Ubah Mata Pelajaran")
        print("  4. Hapus Mata Pelajaran")
        print("  0. Kembali")
        cetak_garis()
        pilihan = input("  Pilih : ").strip()
        if    pilihan == "1": view_mapel()
        elif  pilihan == "2": insert_mapel()
        elif  pilihan == "3": update_mapel()
        elif  pilihan == "4": delete_mapel()
        elif  pilihan == "0": break
        else: print("  Pilihan tidak valid."); pause()


def main():
    init_database()
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        cetak_garis("═")
        print("      SISTEM MANAJEMEN DATA SEKOLAH")
        print("        Praktikum Sistem Basis Data  |  MySQL")
        cetak_garis("═")
        print("  1. Data Siswa")
        print("  2. Data Guru")
        print("  3. Data Mata Pelajaran")
        print("  0. Keluar")
        cetak_garis()
        pilihan = input("  Pilih menu : ").strip()

        if    pilihan == "1": menu_siswa()
        elif  pilihan == "2": menu_guru()
        elif  pilihan == "3": menu_mapel()
        elif  pilihan == "0":
            print("\n  Terima kasih. Program selesai.\n")
            break
        else:
            print("  Pilihan tidak valid."); pause()


if __name__ == "__main__":
    main()
