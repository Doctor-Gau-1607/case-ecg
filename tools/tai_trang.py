#!/usr/bin/env python3
"""tai_trang.py — một "mảnh" của việc tải trang gốc (chỉ HTML, không ảnh) trong GitHub Actions.

Mỗi mảnh chạy trên một máy chủ riêng (IP riêng) nên ít bị ekgblog.com giới hạn tốc độ (429).
  python3 tai_trang.py --main main --manh 3 --tong 20 --out tr
Lấy các case có thứ tự % tong == manh, lưu tr/<path URL đổi / thành _>.
"""
import argparse, json, os, time, urllib.request, urllib.error
from urllib.parse import urlparse

ap = argparse.ArgumentParser()
ap.add_argument('--main', required=True)
ap.add_argument('--manh', type=int, required=True)
ap.add_argument('--tong', type=int, required=True)
ap.add_argument('--out', required=True)
A = ap.parse_args()
UA = 'Mozilla/5.0 (compatible; MEDGUIDE-CaseECG/1.0; +https://github.com/Doctor-Gau-1607/case-ecg)'
DS = json.load(open(os.path.join(A.main, 'du-lieu', 'danh-sach.json'), encoding='utf-8'))
os.makedirs(A.out, exist_ok=True)
ok = loi = 0
for i, c in enumerate(DS):
    if i % A.tong != A.manh or c['trang_thai'] == 'xong':
        continue
    ten = os.path.join(A.out, urlparse(c['url']).path.lstrip('/').replace('/', '_'))
    for t in range(4):
        try:
            req = urllib.request.Request(c['url'], headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                html = r.read().decode('utf-8', 'replace'); cuoi = r.geturl()
            open(ten, 'w', encoding='utf-8').write(f'<!-- saved from url=({len(cuoi)}){cuoi} -->\n' + html)
            ok += 1
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                break
            time.sleep(45 * (t + 1) if e.code == 429 else 5)
        except Exception:  # noqa
            time.sleep(5)
    else:
        loi += 1
    time.sleep(3)
print(f'Mảnh {A.manh}: tải được {ok} trang, lỗi {loi}')
