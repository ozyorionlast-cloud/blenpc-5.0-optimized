# Görev Takip Listesi (Mühendislik Dönüşümü)

## Faz 1: Altyapı ve Doğrulama
- [x] `version_check.py` yazılması ve Blender 5.0.1 API'sinin test edilmesi
- [x] `config.py` içine tüm mimari ve teknik sabitlerin (GRID_UNIT vb.) eklenmesi
- [x] `_registry/` dizini altında temel JSON şemalarının (inventory, slots, tags) oluşturulması

## Faz 2: Çekirdek Motor (Slot & Asset)
- [x] `engine/slot_engine.py` geliştirilmesi (AABB, Slot yerleştirme)
- [x] `_registry/inventory.json` için basit kilit (lock) mekanizması
- [x] Tag tabanlı asset arama mantığının kurulması

## Faz 3: Mimari Atomlar ve Üretim
- [x] `atoms/wall.py` geliştirilmesi
    - [x] Golden Ratio BSP bölünmesi
    - [x] Trigonometrik slot/açı hesaplamaları
    - [x] Euler Manifold check entegrasyonu
- [x] `run_command.py` CLI arayüzünün tamamlanması

## Faz 4: Test ve Kalite Kontrol
- [ ] `tests/fixtures/` altına örnek input JSON'ların eklenmesi
- [ ] `pytest` ile headless Blender testlerinin koşturulması
- [ ] Sonuç raporlama sisteminin (output.json) doğrulanması
