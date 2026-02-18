# MF v5.1 Mimari Dokümantasyonu

Bu doküman, MF v5.1 prosedürel bina üretim motorunun iç yapısını, veri akışını ve temel algoritmalarını açıklar.

## 1. Modüler Tasarım

Motor, sorumlulukların ayrılması (separation of concerns) prensibine göre modüllere bölünmüştür:

| Modül | Sorumluluk |
|-------|------------|
| `datamodel.py` | Temel veri yapıları (`BuildingSpec`, `Rect`, `Room`, `WallSegment`). |
| `floorplan.py` | BSP (Binary Space Partitioning) algoritması ile kat planı üretimi. |
| `walls.py` | Kat planındaki odalardan ham duvar segmentlerinin oluşturulması. |
| `doors.py` / `windows.py` | Duvar segmentlerinin kapı ve pencere boşlukları için oyulması (carving). |
| `blender_mesh.py` | `bpy` ve `bmesh` kullanarak 3D geometri inşası, UV mapping ve material atama. |
| `collider.py` | Fizik motorları için basitleştirilmiş çarpışma (collision) mesh'i üretimi. |
| `engine.py` | Tüm süreci yöneten ana orkestratör. |

## 2. Veri Akışı

Üretim süreci şu adımları izler:

1.  **Input:** `BuildingSpec` (genişlik, derinlik, kat sayısı, seed).
2.  **Floorplan:** Her kat için deterministik BSP bölünmesi yapılır.
3.  **Adjacency:** Odaların birbirine ve koridora olan komşulukları hesaplanır.
4.  **Openings:** Kapı ve pencere konumları belirlenir.
5.  **Carving:** Duvar segmentleri, boşluklar için manifold-safe parçalara bölünür.
6.  **Mesh Generation:** Blender içinde 3D objeler oluşturulur.
7.  **Cleanup:** Üst üste binen vertex'ler birleştirilir, iç yüzeyler silinir.
8.  **Export:** Görsel ve collider mesh'leri GLB formatında dışa aktarılır.

## 3. Temel Algoritmalar

### BSP (Binary Space Partitioning)
Kat planı, bir dikdörtgenin (footprint) koridor merkezli olarak rekürsif olarak bölünmesiyle oluşturulur. Koridor, binanın omurgasını oluşturur ve odalar bu omurganın iki yanına yerleşir.

### Manifold-Safe Carving
Boolean işlemleri (difference/union) yerine, duvarlar pencere ve kapı boşluklarının etrafından dolaşacak şekilde küçük dikdörtgen prizmalara bölünür. Bu yöntem, oyun motorlarında sorun yaratan "non-manifold" geometrilerin oluşmasını engeller.

### World-Space UV Projection
Dokusuz (beyaz) binaları önlemek için, tüm yüzeylere dünya koordinatları baz alınarak otomatik UV projeksiyonu uygulanır. Bu, tile edilebilir (tekrarlanan) dokuların binalar üzerinde doğru ölçekte görünmesini sağlar.
