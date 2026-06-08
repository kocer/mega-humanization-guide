# Katkı Rehberi

Bu projeye katkı yapmak için aşağıdaki adımları izleyin.

## Akış

1. **Fork** edin (sağ üst köşe → Fork).
2. Fork'unuzda yeni bir branch açın:
   ```bash
   git checkout -b ozellik/yeni-ozellik
   ```
3. Değişikliğinizi yapın, commit edin.
4. **Pull Request** açın — hedef branch: **`develop`**.
5. PR incelenip onaylandıktan sonra merge edilir.

## Kurallar

- PR'lar `develop` branch'ini hedeflemeli (`main`'i değil).
- `main` ve `develop`'a direkt push kapalıdır; tüm değişiklikler PR ile gelir.
- Her PR en az **1 onay** gerektirir.
- PR açıklamasında ne değiştiğini ve nedenini kısaca yazın.

## Branch Yapısı

- `main` → kararlı, yayınlanan sürüm.
- `develop` → aktif geliştirme. Katkılar buraya gelir.
