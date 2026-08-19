# Notlar

Bu klasöre attığın `.txt` dosyaları sitede **Notlar** bölümünde, yana kaydırmalı kartlar
olarak görünür.

## Nasıl not eklenir

1. Notepad'i aç, notunu yaz.
2. Bu klasöre kaydet: `notlar/bir-isim.txt`
3. Commit'le ve push'la. Birkaç dakika içinde sitede görünür.

## Kurallar

| | |
|---|---|
| Uzunluk | 512 karakter. Fazlası kırpılır ve sonuna `…` konur. |
| Başlık | Dosya adı. `oyun-guncellemesi.txt` → **oyun guncellemesi** |
| Tarih | Dosya adında `2026-08-19-` gibi bir ön ek varsa o kullanılır, yoksa dosyanın repoya eklendiği commit tarihi. |
| Ömür | 30 gün. Dolunca dosya otomatik silinir ve kart siteden kalkar. |
| Sıra | En yeni not en solda. |

Satır sonları korunur, yani not içinde alt alta yazabilirsin.

## Örnek dosya adları

```
bugun-ne-yaptim.txt
2026-08-19-catwando-demo.txt
kisa-not.txt
```

## Nasıl çalışıyor

`.github/workflows/notlar.yml` her push'ta ve her gün çalışır:
`.github/scripts/notlar.py` bu klasörü tarar, 30 günü geçen `.txt` dosyalarını siler ve
kalanlardan `notlar/notlar.json` üretir. Site açılışta o dosyayı okur.

`notlar.json` elle düzenlenmez — her çalışmada baştan yazılır.

Silinen notlar git geçmişinde durmaya devam eder; `git log -- notlar/` ile geri bulabilirsin.
