# Mega Humanization Rehberi

🌍 **Diller / Languages:** Türkçe (bu dosya) · [**English** →](README.md)

> **⚙️ Bu dosyalar nasıl kullanılır — bir AI'ye verin.** Bu repo, *bir yapay zekâya
> verilmek üzere* yazıldı (ChatGPT, Claude, Gemini vb.). `MEGA_HUMANIZATION_GUIDE.md`
> dosyasını — özellikle §4 (tell kataloğu), §10 (hazır talimat bloğu) ve §11 (QA
> kontrol listesi) — modelin sistem/talimat promptuna yapıştırın, taslağınızı verin;
> AI tüm humanization pasını sizin için tekrar üretsin. Yönetmen sizsiniz, editör AI.
>
> **Not:** rehberin gövdesi (`MEGA_HUMANIZATION_GUIDE.md`) İngilizcedir — bilerek,
> çünkü AI'ler İngilizce talimatı en iyi uygular ve open-source erişimi geniş olsun.
> Türkçe'ye özgü teknikler rehberin §9.1 ekinde duruyor.

AI tarafından yazılmış metni, anlamı/yapıyı/kaliteyi bozmadan gerçekten insan
elinden çıkmış gibi okutmak için eksiksiz, tekrar kullanılabilir bir metodoloji.

Rehberi bir AI'ye sistem/talimat promptu olarak verdiğinizde yüksek kaliteli bir
humanization pası üretebilir: tespit-sinyali teorisi, gerçek önce→sonra örnekleriyle
bir AI "tell" kataloğu, burstiness mühendisliği, yerel ölçüm aracı, hedefli
de-flagging, kontrollü kusur ve kaynak bütünlüğü. Dilden bağımsız çekirdek + Türkçe'ye
özel ek.

## İçindekiler

- **[`MEGA_HUMANIZATION_GUIDE.md`](MEGA_HUMANIZATION_GUIDE.md)** — tam rehber
  (İngilizce). §0 (nasıl kullanılır), §1–§2 (zihinsel model + ses kalibrasyonu),
  §4 (tell kataloğu), §10 (hazır AI talimat bloğu), §11 (QA kapısı) ile başlayın.
- **[`humanizer_metrics.py`](humanizer_metrics.py)** — offline vekil metrikler
  (cümle uzunluğu burstiness'i, değişim katsayısı CV, tür-belirteç oranı TTR).
  Perplexity'yi **ölçmez** — yapısal bir koku testidir, kesin hüküm değil.

## Hızlı başlangıç

Bir metni ölç ve aynı türden gerçek bir insan örneğiyle karşılaştır:

```bash
python3 humanizer_metrics.py hedef.txt --baseline insan_ornegi.txt
```

Sonra rehberdeki §3 döngüsünü bir AI'ye uygulat: §4'ü katı kural, §11'i çıkış
kapısı olarak kullan.

## Yöntem özeti (rehberin damıtılmış hâli)

1. **Ses kalibrasyonu (§2):** örnek metinlerden parmak izi çıkar — cümle uzunluğu
   değişkenliği, bağlaçlar, alıntı giriş kalıbı, fiil dağarcığı, paragraf
   açılış/kapanış alışkanlıkları. Kusurlarını da taklit et; ama AI-telli kusurları
   taklit etme.
2. **İki-eksen modeli (§1):** dedektörler **perplexity** (öngörülebilirlik) ve
   **burstiness** (ritim değişkenliği) ölçer. Perplexity'yi öngörülemez/özgül
   ifadelerle elle düşür; burstiness'i kısa+uzun cümle karışımıyla yükselt.
3. **Tell kataloğu (§4):** yığılı antitez (en büyük tell), üçleme, formülsel paragraf
   kapanışı, şablon tez duyurusu, aforizma sonuç, tekdüze cümle, AI-kelimeleri,
   em-dash, alıntı entegrasyonu, tekdüze geçişler.
4. **Hedefli de-flag (§6):** dedektör bir cümleyi işaretlerse SADECE o cümleyi yeniden
   yaz; geri kalanına dokunma.
5. **Kaynak bütünlüğü (§8):** uydurma yok. Her atıf gerçek ve doğrulanmış olmalı;
   kaynakları gövdeye iç atıf olarak işle, sadece kaynakçaya park etme.
6. **Kontrollü kusur (§7):** çok az, gerçekçi, anlam bozmayan minör hatalar voice'u
   doğallaştırır — sorumluluk notuyla.
7. **Dur ve elle bitir:** son %1 garanti tek yolla gelir — insanın 2-3 cümleyi kendi
   sesiyle düzenlemesi.

## Dürüst uyarı

Hiçbir otomatik adım metni herhangi bir AI dedektöründen **geçer garanti** yapmaz —
yoğun akademik düzyazı doğası gereği düşük-burstiness'tir ve insan yazsa bile flag
yiyebilir. Dedektör skorları her iki yönde de kanıttır, ispat değil. Tek garantili
humanization, bir insanın birkaç cümleyi kendi sesiyle düzenlemesidir. Rehber bunu
defalarca, bilerek söyler.

## Lisans

The Unlicense (kamu malı). Ne istersen yap. Atıf makbule geçer, zorunlu değil.
