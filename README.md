# Event Aggregator Service (UTS - Sistem Terdistribusi)


**Nama : Alifah Nur Aisyah**
**NIM: 11221069**  
**Kelas: Sistem Parallel dan Terdistribusi - A**

## Deskripsi Sitem
Aplikasi ini merupakan Event Aggregator Service yang dikembangkan menggunakan FastAPI dengan bahasa pemrograman Python 3.11. Sistem ini berfungsi untuk menerima dan mengelola event yang dikirim oleh berbagai sumber (publisher), kemudian melakukan deduplikasi dan idempotensi berdasarkan kombinasi unik dari pasangan (topic, event_id). Setiap event yang telah diverifikasi keunikannya akan disimpan secara persisten di basis data SQLite, sehingga data tetap terjaga meskipun sistem mengalami restart. Aplikasi ini di-containerize menggunakan Docker untuk memastikan portabilitas dan kemudahan deployment di berbagai lingkungan. Selain itu, sistem juga dilengkapi dengan unit test berbasis Pytest guna menjamin reliabilitas, stabilitas, serta kinerja dari setiap komponen utama yang terlibat dalam proses agregasi event.


## Fitur Utama 
**1. Endpoint API**
    - 'POST /publish' : Menerimana 1 atau batch event pada JSON.
    - 'GET /envents?topic=...' : Menampilkan semua event unik yang dicari (contoh, demo.topic)
    - 'GET /stats' : Menampilkan statistik sistem 
**2. Deduplication Store** : Menjamin idempotensi walau sistem restart
**3. At-least-once Delivery Simulation** : Mendeteksi duplikasi event
**4. Persistent Queue** :  menyimpan event sementara untuk konsumsi internal
**5. Dockerized Deployment** : siap dijalankan dalam container.


## Struktur Folder 
**UTS_EVENTAGGREGATOR**
- .pytest_cache
- data
    - dedup_store.db 
- simulate
    - simulate_async_events.py
- src
    - _pycache
    - dedup_store.py
    - event_queue.py
    - main.py
    - models.py
- test
    -_pycache 
    - __init__.py
    - conftest.py
    - test_api.py
    - test_dediplication.py
    - test_persistence.py
- .dockerignore
- dockerfile
- pytest.ini
- README.md
- requirements.txt


## Skema Event
**A. /publish**
```json
{
  "topic": "sensor.temp",
  "event_id": "evt_001",
  "timestamp": "2025-10-22T10:00:00Z",
  "source": "sensor_A",
  "payload": { "temperature": 29.5 }
}
```
**B. /events**
topic : simula.topic
** C. /stats**
execute (langsung)


## Menjalankan Aplikasi
**1. Menjalankan Main.app (server)**
- uvicorn src.main:app
**2. Jalankan unit test**
- pytest -v (pastikan server telah jalan)
- Semua test meliputi : 
    - Validasi skema event
    - Dedup duplikat event
    - Persistensi dedup setelah restart
    - Statistik sistem
    - Stress test (5.000+ event, 20% duplikat)
**3. Jalankan test 5000**
- python simulate_async_events.py 
**4. Build Docker Build**
- docker build -t uts-aggregator .
**5. Jalankan Run**
- docker run -p 8080:8080 uts-aggregator
**6.Akses Endpoint**
a. Endpoint : /publish
    Metode : POST
    Desk : kirim event atau batch event
b. Endpoint : /events
    Metode : GET
    Desk :  ambil semua event tersimpan
c. Endpoint : /events?topic=nama_topic
    Metode : GET
    Desk : filter event berdasarkan topic
d. Endpoint :  /stats
    Metode : GET
    Desk : statistik sistem


## Arsitektur Sederhana
Client (Publisher)
   ↓
[ /publish API ]
   ↓
DedupStore (SQLite)
   ↓
EventQueue (in-memory)
   ↓
Consumer / Stats

## Asumsi dan Batasan
- Dedup store menggunakan SQLite lokal (tidak terdistribusi).
- Event yang diterima tidak dihapus, hanya ditandai unik.
- Ordering tidak dijamin global, hanya per-topic.
- Sistem berjalan dalam mode at-least-once delivery, sehingga bisa menerima duplikasi.
- Queue bersifat in-memory, cocok untuk demo dan skala lokal.


## Video Demo (Link Youtube)
**https://youtu.be/4gXW3jF0bQU?si=DSftyvQVfUNMN6QY**
Menunjukkan:
- Build dan run Docker container
- Kirim event duplikat
- Verifikasi dedup di /stats
- Restart container, dedup tetap berfungsi

## Referensi
- Tanenbaum, A. S., & van Steen, M. (2017). Distributed Systems: Principles and Paradigms (2nd ed.). Pearson.