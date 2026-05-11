-- ============================================================
--  FILE   : db_sekolah.sql
--  DBMS   : MySQL 8.x / MariaDB 10.x
--  Deskripsi : Database Sistem Manajemen Sekolah
--              Entitas  : guru, siswa, mata_pelajaran
--              Relasi   : guru (1) --< mata_pelajaran (N)
--  Cara Pakai :
--    mysql -u root -p < db_sekolah.sql
--    ATAU import lewat phpMyAdmin / MySQL Workbench
-- ============================================================

-- ── 0. BUAT & PILIH DATABASE ─────────────────────────────
DROP DATABASE IF EXISTS db_sekolah;
CREATE DATABASE db_sekolah
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE db_sekolah;

-- ── 1. TABEL GURU ────────────────────────────────────────
CREATE TABLE guru (
    id_guru     INT          NOT NULL AUTO_INCREMENT,
    nip         VARCHAR(20)  NOT NULL COMMENT 'Nomor Induk Pegawai',
    nama        VARCHAR(100) NOT NULL,
    jabatan     VARCHAR(50)  NOT NULL,
    no_telepon  VARCHAR(15)  DEFAULT NULL,
    email       VARCHAR(100) DEFAULT NULL,
    PRIMARY KEY (id_guru),
    UNIQUE KEY uq_nip (nip)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Data tenaga pengajar';

-- ── 2. TABEL SISWA ───────────────────────────────────────
CREATE TABLE siswa (
    id_siswa      INT           NOT NULL AUTO_INCREMENT,
    nis           VARCHAR(15)   NOT NULL COMMENT 'Nomor Induk Siswa',
    nama          VARCHAR(100)  NOT NULL,
    kelas         VARCHAR(15)   NOT NULL COMMENT 'Contoh: X-IPA-1',
    jenis_kelamin ENUM('L','P') NOT NULL COMMENT 'L=Laki-laki P=Perempuan',
    alamat        TEXT          DEFAULT NULL,
    PRIMARY KEY (id_siswa),
    UNIQUE KEY uq_nis (nis)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Data peserta didik';

-- ── 3. TABEL MATA PELAJARAN ──────────────────────────────
CREATE TABLE mata_pelajaran (
    id_mapel    INT              NOT NULL AUTO_INCREMENT,
    kode_mapel  VARCHAR(10)      NOT NULL COMMENT 'Contoh: MTK, BIN, FIS',
    nama_mapel  VARCHAR(100)     NOT NULL,
    id_guru     INT              NOT NULL COMMENT 'FK ke tabel guru',
    kkm         TINYINT UNSIGNED NOT NULL DEFAULT 75
                                 COMMENT 'Kriteria Ketuntasan Minimal 0-100',
    PRIMARY KEY (id_mapel),
    UNIQUE KEY uq_kode (kode_mapel),
    CONSTRAINT fk_mapel_guru
        FOREIGN KEY (id_guru)
        REFERENCES guru (id_guru)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Data mata pelajaran beserta guru pengampu';

-- ============================================================
--  DATA SAMPLE
-- ============================================================

INSERT INTO guru (nip, nama, jabatan, no_telepon, email) VALUES
('197801012005011001','Budi Santoso, S.Pd.','Guru Matematika','081234567801','budi.santoso@sekolah.sch.id'),
('198203152006022002','Siti Rahayu, S.Pd.','Guru Bahasa Indonesia','081234567802','siti.rahayu@sekolah.sch.id'),
('197905202007011003','Ahmad Fauzi, S.Si.','Guru Fisika','081234567803','ahmad.fauzi@sekolah.sch.id'),
('198511102010012004','Dewi Lestari, S.Pd.','Guru Bahasa Inggris','081234567804','dewi.lestari@sekolah.sch.id'),
('199001252015011005','Rizki Pratama, S.Kom.','Guru Informatika','081234567805','rizki.pratama@sekolah.sch.id');

INSERT INTO siswa (nis, nama, kelas, jenis_kelamin, alamat) VALUES
('2024001','Aldi Firmansyah','X-IPA-1','L','Jl. Melati No. 12, Surakarta'),
('2024002','Bella Anggraini','X-IPA-1','P','Jl. Mawar No. 5, Surakarta'),
('2024003','Cahyo Nugroho','X-IPA-2','L','Jl. Kenanga No. 8, Surakarta'),
('2024004','Diana Putri','X-IPS-1','P','Jl. Anggrek No. 3, Surakarta'),
('2024005','Eko Saputro','X-IPS-1','L','Jl. Dahlia No. 17, Surakarta'),
('2024006','Fitria Handayani','XI-IPA-1','P','Jl. Flamboyan No. 9, Surakarta'),
('2024007','Galih Wicaksono','XI-IPA-1','L','Jl. Cempaka No. 21, Surakarta'),
('2024008','Hana Safitri','XI-IPS-2','P','Jl. Nusa Indah No. 4, Surakarta'),
('2024009','Irwan Setiawan','XII-IPA-1','L','Jl. Kamboja No. 6, Surakarta'),
('2024010','Julia Ramadhani','XII-IPS-1','P','Jl. Bougenville No. 11, Surakarta');

INSERT INTO mata_pelajaran (kode_mapel, nama_mapel, id_guru, kkm) VALUES
('MTK','Matematika',1,75),
('BIN','Bahasa Indonesia',2,75),
('FIS','Fisika',3,70),
('KIM','Kimia',3,70),
('BING','Bahasa Inggris',4,75),
('INF','Informatika',5,78),
('BIO','Biologi',3,72),
('BIND','Bahasa Inggris Adv',4,80);

-- ============================================================
--  VIEWS
-- ============================================================

CREATE OR REPLACE VIEW v_mapel_guru AS
SELECT mp.id_mapel, mp.kode_mapel, mp.nama_mapel,
       g.nama AS nama_guru, g.nip AS nip_guru, mp.kkm
FROM mata_pelajaran mp
JOIN guru g ON mp.id_guru = g.id_guru
ORDER BY mp.id_mapel;

CREATE OR REPLACE VIEW v_beban_mengajar AS
SELECT g.id_guru, g.nip, g.nama, g.jabatan,
       COUNT(mp.id_mapel) AS jumlah_mapel
FROM guru g
LEFT JOIN mata_pelajaran mp ON g.id_guru = mp.id_guru
GROUP BY g.id_guru, g.nip, g.nama, g.jabatan
ORDER BY jumlah_mapel DESC;

-- ============================================================
--  VERIFIKASI
-- ============================================================
SELECT 'guru'          AS tabel, COUNT(*) AS jumlah FROM guru
UNION ALL
SELECT 'siswa',                  COUNT(*)           FROM siswa
UNION ALL
SELECT 'mata_pelajaran',         COUNT(*)           FROM mata_pelajaran;
