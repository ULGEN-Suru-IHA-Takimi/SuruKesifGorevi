# Swarm Drone Features

Bu dokümantasyon, DroneCore projesine eklenen swarm (sürü) drone özelliklerini açıklar.

## 🚁 Swarm Mesaj Sistemi

### Genel Bakış
Swarm drone sistemi, birden fazla drone'ın birbirleriyle XBee üzerinden haberleşmesini ve koordineli iniş yapmasını sağlar.

### Nasıl Çalışır?

1. **ArUco Bulma ve Mesaj Gönderme**: Bir drone ArUco marker'ı bulduğunda ve üzerine iniş yaptığında, konum bilgilerini XBee üzerinden broadcast olarak gönderir.

2. **Mesaj Formatı**: 
   ```
   lat_scaled,lon_scaled,alt_scaled,command
   ```
   - `lat_scaled`: Latitude × 1,000,000 (integer)
   - `lon_scaled`: Longitude × 1,000,000 (integer)  
   - `alt_scaled`: Altitude × 10 (integer)
   - `command`: Komut kodu (1 = iniş komutu)

3. **Farklı Davranışlar**:
   - **ArUco Bulan Drone**: 5 metre ötesine gider ve mission'ı bitirir
   - **Swarm Mesajı Alan Drone**: Direkt bulunduğu yerde iniş yapar (hareket etmez)

### 🎯 Davranış Farkları

| Senaryo | Drone Davranışı | Sonuç |
|---------|----------------|--------|
| **ArUco Bulundu** | 5 metre ötesine git | Mission tamamlandı |
| **Swarm Mesajı Geldi** | Direkt bulunduğu yerde in | Koordineli iniş |

## 📁 Dosya Yapısı

### Ana Dosyalar
- `missions/swarm_discovery.py` - Ana swarm mission sınıfı
- `test/swarm_behavior_test.py` - Swarm davranış test aracı

### Servisler
- `services/xbee_service.py` - XBee haberleşme servisi

## 🚀 Kullanım

### 1. Swarm Discovery Mission'ı Çalıştırma

```python
from missions.swarm_discovery import SwarmDiscovery

# XBee port'unu belirtin
swarm_mission = SwarmDiscovery(xbee_port="/dev/ttyUSB0")

# Drone'a bağlanın
await swarm_mission.connect("udpin://0.0.0.0:14541", 50061)

# Mission'ı başlatın
await swarm_mission.square_oscillation_by_cam_fov(
    distance1=50.0,      # İleri-geri mesafe
    distance2=30.0,      # Yan mesafe  
    velocity=2.0,        # Hız (m/s)
    camera_fov_horizontal=60.0,
    camera_fov_vertical=40.0,
    image_width=640,
    image_height=480
)
```

### 2. Swarm Davranış Test Etme

```bash
cd test
python3 swarm_behavior_test.py
```

Test aracı ile:
- ArUco discovery mesajları gönderebilir
- Farklı davranışları gözlemleyebilir
- Swarm koordinasyonunu test edebilirsiniz

## 🔧 Konfigürasyon

### XBee Ayarları
- **Port**: `/dev/ttyUSB0` (Linux) veya `COM3` (Windows)
- **Baudrate**: 57600
- **Mesaj Formatı**: Broadcast

### Drone Ayarları
- **Minimum İrtifa**: 5m
- **Hedef İrtifa**: Mission'da belirtilen
- **Güvenlik Mesafesi**: 0.5m (iniş için)

## 📡 Mesaj Akışı

```
Drone A (ArUco bulur) → XBee Broadcast → Drone B, C, D...
     ↓
Precision Landing → Konum bilgisi gönder → Otomatik iniş
```

## ⚠️ Güvenlik Özellikleri

1. **Hata Yönetimi**: XBee bağlantısı başarısız olursa mission devam eder
2. **Emergency Landing**: Hata durumunda güvenli iniş
3. **Timeout Koruması**: 30 saniye maksimum bekleme süresi
4. **Koordinat Doğrulama**: Gelen mesajlar parse edilir ve doğrulanır

## 🧪 Test Senaryoları

### Senaryo 1: Tek Drone Test
1. Swarm discovery mission'ı başlat
2. ArUco marker'ı bul
3. Precision landing yap
4. XBee mesajı gönder

### Senaryo 2: İki Drone Test
1. İlk drone'ı swarm discovery ile başlat
2. İkinci drone'ı aynı mission ile başlat
3. İlk drone ArUco bulduğunda mesaj gönder ve 5 metre ötesine git
4. İkinci drone mesajı alıp direkt bulunduğu yerde iniş yap

### Senaryo 3: Davranış Test
1. `swarm_behavior_test.py` ile test mesajı gönder
2. Farklı davranışları gözlemle:
   - ArUco bulma: 5 metre ötesine git
   - Swarm mesajı: Direkt bulunduğu yerde in

## 🐛 Sorun Giderme

### XBee Bağlantı Sorunları
- Port numarasını kontrol edin
- Baudrate ayarını doğrulayın
- USB kablosunu kontrol edin

### Mesaj Alınamıyor
- XBee cihazlarının aynı ağda olduğundan emin olun
- Mesaj formatını kontrol edin
- Broadcast ayarlarını doğrulayın

### Otomatik İniş Çalışmıyor
- Drone'un GPS sinyalini kontrol edin
- Hedef koordinatları doğrulayın
- Mission state'ini kontrol edin

## 🔮 Gelecek Özellikler

- [ ] Çoklu drone koordinasyonu
- [ ] Dinamik swarm formation
- [ ] Gelişmiş collision avoidance
- [ ] Swarm mission planning
- [ ] Real-time swarm monitoring

## 📞 Destek

Sorun yaşadığınızda:
1. Log dosyalarını kontrol edin
2. Test araçlarını kullanın
3. XBee ayarlarını doğrulayın
4. Drone bağlantısını test edin
