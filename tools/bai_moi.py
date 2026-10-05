#!/usr/bin/env python3
"""bai_moi.py — chạy trong GitHub Actions: tìm bài MỚI trên ECG Blog của Ken Grauer (ekgblog.com, Blogger)
qua nguồn tin JSON của Blogger, thêm vào du-lieu/tat-ca-bai-blog.json; bài là case ECG (tiêu đề có số "#N")
thì thêm vào cuối du-lieu/danh-sach.json với trạng thái "chua" (lượt dịch hằng tuần sẽ dịch).

  python3 bai_moi.py --main main
"""
import argparse, html, json, os, re, sys, time, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument('--main', required=True)
ap.add_argument('--so-bai', type=int, default=50, help='số bài mới nhất để dò')
A = ap.parse_args()

FEED = 'https://www.ekgblog.com/feeds/posts/default?alt=json&max-results={}'
UA = 'Mozilla/5.0 (compatible; MEDGUIDE-CaseECG/1.0; +https://github.com/Doctor-Gau-1607/case-ecg)'
DS_P = os.path.join(A.main, 'du-lieu', 'danh-sach.json')
TC_P = os.path.join(A.main, 'du-lieu', 'tat-ca-bai-blog.json')
DS = json.load(open(DS_P, encoding='utf-8'))
TC = json.load(open(TC_P, encoding='utf-8'))


def chuan(u):
    return re.sub(r'^https?://(www\.)?', '', u.split('#')[0].split('?')[0]).rstrip('/').lower()


for t in range(4):
    try:
        req = urllib.request.Request(FEED.format(A.so_bai), headers={'User-Agent': UA})
        feed = json.load(urllib.request.urlopen(req, timeout=60))
        break
    except Exception as e:  # noqa
        loi = e; time.sleep(30 * (t + 1))
else:
    sys.exit(f'Không đọc được nguồn tin ekgblog: {loi}')

da_co = {chuan(x['url']) for x in TC} | {chuan(c['url']) for c in DS}
slug_co = {c['slug'] for c in DS}
moi_tc, moi_ds = [], []
for e in feed.get('feed', {}).get('entry', []):
    url = next((l['href'] for l in e.get('link', []) if l.get('rel') == 'alternate'), None)
    if not url or chuan(url) in da_co:
        continue
    da_co.add(chuan(url))
    tieu_de = html.unescape(e.get('title', {}).get('$t', '')).strip()
    ngay = e.get('published', {}).get('$t', '')[:10]
    moi_tc.append({'title': tieu_de, 'url': url, 'ngay': ngay})
    m = re.search(r'#\s*(\d+)', tieu_de)
    if not m:
        print('  (bỏ qua, không phải case đánh số):', tieu_de[:90]); continue
    so = int(m.group(1))
    video = re.search(r'\bvideo\b', tieu_de, re.I)
    nhan = f'#{so}' + (' Video' if video else '')
    slug = f'case-{so:03d}' + ('-video' if video else '')
    while slug in slug_co:
        slug += '-b'
    slug_co.add(slug)
    moi_ds.append({'url': url, 'tieu_de_en': tieu_de, 'nhan': nhan, 'slug': slug, 'trang_thai': 'chua', 'ngay_dang': ngay})

if not moi_tc:
    print('Không có bài mới.'); sys.exit(0)
TC = sorted(moi_tc, key=lambda x: x['ngay'], reverse=True) + TC      # tat-ca-bai-blog: mới nhất trước
json.dump(TC, open(TC_P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
stt = max(c['stt'] for c in DS)
for c in sorted(moi_ds, key=lambda x: (x['ngay_dang'], x['slug'])):  # danh-sach: cũ trước, mới sau
    stt += 1
    DS.append(dict(stt=stt, **c))
json.dump(DS, open(DS_P, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(f'Bài mới: {len(moi_tc)} (case thêm vào danh sách: {len(moi_ds)})')
for c in moi_ds:
    print(' ', c['nhan'], c['ngay_dang'], c['tieu_de_en'][:90])
