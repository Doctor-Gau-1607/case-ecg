#!/usr/bin/env python3
"""tai_nguon.py — chạy trong GitHub Actions: tải trang gốc + ảnh/video gốc của từng case ECG.

Đọc danh sách case ở  MAIN/du-lieu/danh-sach.json, ghi vào thư mục nhánh nguon:
  NGUON/<slug>/trang.html       trang gốc (có dòng "saved from url" để medguide.py biết URL)
  NGUON/<slug>/goc/<tên>        ảnh / video gốc, tên đặt đúng quy tắc của medguide.py
  NGUON/<slug>/nguon.json       số media, lỗi (nếu có), thời điểm tải
Case đã có nguon.json không lỗi thì bỏ qua (chạy lại được nhiều lần).
Tải chậm rãi: ~1 giây giữa hai trang, định danh rõ ràng bằng User-Agent.
"""
import json, os, subprocess, sys, time, tempfile, argparse
import urllib.request, urllib.error

ap = argparse.ArgumentParser()
ap.add_argument('--main', required=True)
ap.add_argument('--nguon', required=True)
ap.add_argument('--commit-moi', type=int, default=3, help='commit + push sau mỗi N case')
ap.add_argument('--gioi-han', type=int, default=0, help='chỉ tải N case (0 = tất cả)')
A = ap.parse_args()

UA = 'Mozilla/5.0 (compatible; MEDGUIDE-CaseECG/1.0; +https://github.com/Doctor-Gau-1607/case-ecg)'
MG = os.path.join(A.main, 'tools', 'medguide.py')
DS = json.load(open(os.path.join(A.main, 'du-lieu', 'danh-sach.json'), encoding='utf-8'))


PHIEN = 2   # đổi khi quy tắc đặt tên media đổi -> tải lại


def tai(url, lan=6):
    for t in range(lan):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read(), r.geturl()
        except urllib.error.HTTPError as e:
            loi = e
            if e.code == 404:
                break
            time.sleep((120 if e.code == 429 else 5) * (t + 1))   # 429: bị giới hạn tốc độ, chờ lâu
        except Exception as e:  # noqa
            loi = e
            time.sleep(5 * (t + 1))
    raise loi


def git(*a):
    subprocess.run(['git', '-C', A.nguon] + list(a), check=True)


def day_len(n):
    git('add', '-A')
    if subprocess.run(['git', '-C', A.nguon, 'diff', '--cached', '--quiet']).returncode != 0:
        git('commit', '-q', '-m', f'Tải nguồn: thêm {n} case')
        for t in range(3):
            if subprocess.run(['git', '-C', A.nguon, 'push', '-q', 'origin', 'HEAD:nguon']).returncode == 0:
                return
            time.sleep(10)
        sys.exit('push thất bại')


moi, xong_lo = 0, 0
for c in DS:
    if A.gioi_han and moi >= A.gioi_han:
        break
    d = os.path.join(A.nguon, c['slug'])
    nj = os.path.join(d, 'nguon.json')
    if os.path.exists(nj):
        cu = json.load(open(nj))
        if not cu.get('loi') and cu.get('phien') == PHIEN:
            continue
    import shutil
    shutil.rmtree(os.path.join(d, 'goc'), ignore_errors=True)
    os.makedirs(os.path.join(d, 'goc'), exist_ok=True)
    info = {'url': c['url'], 'loi': [], 'phien': PHIEN}
    try:
        body, cuoi = tai(c['url'])
        html = body.decode('utf-8', 'replace')
        open(os.path.join(d, 'trang.html'), 'w', encoding='utf-8').write(
            f'<!-- saved from url=({len(cuoi)}){cuoi} -->\n' + html)
        with tempfile.TemporaryDirectory() as w:
            r = subprocess.run([sys.executable, MG, 'trich', '--src', os.path.join(d, 'trang.html'),
                                '--work', w, '--chon', 'div.post-body'], capture_output=True, text=True)
            info['trich'] = r.stdout.strip().splitlines()[-4:] + r.stderr.strip().splitlines()[-3:]
            media = json.load(open(os.path.join(w, 'media.json'))) if r.returncode == 0 else []
            if r.returncode != 0:
                info['loi'].append('trich lỗi')
        for m in media:
            f = os.path.join(d, 'goc', m['name'])
            if os.path.exists(f) and os.path.getsize(f) > 0:
                continue
            try:
                data, _ = tai(m['url'])
                open(f, 'wb').write(data)
            except Exception as e:  # noqa
                info['loi'].append(f"{m['url']} {e}")
            time.sleep(0.2)
        info['so_media'] = len(media)
    except Exception as e:  # noqa
        info['loi'].append(f"trang: {e}")
    info['luc'] = time.strftime('%Y-%m-%d %H:%M:%S')
    json.dump(info, open(nj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(c['slug'], 'media', info.get('so_media'), 'lỗi', len(info['loi']), flush=True)
    moi += 1; xong_lo += 1
    time.sleep(20)
    if xong_lo >= A.commit_moi:
        day_len(xong_lo); xong_lo = 0
day_len(xong_lo)
print('Xong lượt này:', moi, 'case')
