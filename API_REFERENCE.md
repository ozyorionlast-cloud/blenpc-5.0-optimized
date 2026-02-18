# MF v5.1 API Referansı

Bu doküman, MF v5.1 motorunun ana sınıflarını, parametrelerini ve dönüş değerlerini detaylandırır.

## 1. `BuildingSpec` (Veri Yapısı)

Bina üretim parametrelerini tanımlayan ana sınıftır.

| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|------------|----------|
| `width` | `float` | - | Binanın X eksenindeki genişliği (metre). |
| `depth` | `float` | - | Binanın Y eksenindeki derinliği (metre). |
| `floors` | `int` | `1` | Kat sayısı. |
| `seed` | `int` | `None` | Deterministik üretim için rastgelelik anahtarı. |
| `roof_type` | `RoofType` | `RoofType.FLAT` | Çatı tipi (Enum). |

## 2. `RoofType` (Enum)

Desteklenen çatı tipleri:

- `RoofType.FLAT`: Düz çatı.
- `RoofType.HIP`: Kırma çatı (dört yöne eğimli).
- `RoofType.GABLED`: Beşik çatı (iki yöne eğimli).
- `RoofType.SHED`: Tek yöne eğimli çatı.

## 3. `generate` (Fonksiyon)

Üretim sürecini başlatan ana fonksiyondur.

**İmza:**
```python
def generate(spec: BuildingSpec, output_dir: Path) -> GenerationOutput:
```

**Dönüş Değeri (`GenerationOutput`):**
- `floors`: Her katın istatistiklerini içeren liste.
- `roof_type`: Kullanılan çatı tipi.
- `glb_path`: Üretilen ana GLB dosyasının yolu.
- `export_manifest`: Üretim detaylarını içeren JSON dosyasının yolu.

## 4. `GenerationOutput` Detayları

Her kat için (`FloorOutput`) şu bilgiler sağlanır:
- `room_count`: Odaların sayısı.
- `door_count`: Üretilen kapı sayısı.
- `window_count`: Üretilen pencere sayısı.
- `wall_segment_count`: Toplam duvar parçası sayısı.

## 5. Konfigürasyon Sabitleri (`config.py`)

Global ayarları değiştirmek için kullanılır:
- `STORY_HEIGHT`: Kat yüksekliği (Varsayılan: 3.2m).
- `WALL_THICKNESS`: Duvar kalınlığı (Varsayılan: 0.2m).
- `WINDOW_SILL_HEIGHT`: Pencere denizlik yüksekliği (Varsayılan: 1.0m).
- `TEXTURE_TILE_SIZE`: UV tiling ölçeği (Varsayılan: 2.0m).
