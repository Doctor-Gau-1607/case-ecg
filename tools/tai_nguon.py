#!/usr/bin/env python3
"""tai_nguon.py — chạy trong GitHub Actions: tải trang gốc + ảnh/video gốc của từng case ECG.

Đọc danh sách case ở  MAIN/du-lieu/danh-sach.json, ghi vào thư mục nhánh nguon:
  NGUON/<slug>/trang.html       trang gốc (có dòng "saved from url" để medguide.py biết URL)
  NGUON/<slug>/goc/<tên>        ảnh / video gốc, tên đặt đúng quy tắc của medguide.py
  NGUON/<slug>/nguon.json       số media, lỗi (nếu có), thời điểm tải
Case đã có nguon.json không lỗi thì bỏ qua (chạy lại được nhiều lần).
Tải chậm rãi: ~1 giây giữa hai trang, định danh rõ ràng bằng User-Agent.
"""
import json, os, subprocess, sys, time, tempfile, argparse, shutil
import urllib.request, urllib.error

ap = argparse.ArgumentParser()
ap.add_argument('--main', required=True)
ap.add_argument('--nguon', required=True)
ap.add_argument('--commit-moi', type=int, default=3, help='commit + push sau mỗi N case')
ap.add_argument('--trang', default='', help='thư mục trang đã tải sẵn (nhánh trang), tên = path URL đổi / thành _')
ap.add_argument('--gioi-han', type=int, default=0, help='chỉ tải N case (0 = tất cả)')
A = ap.parse_args()

UA = 'Mozilla/5.0 (compatible; MEDGUIDE-CaseECG/1.0; +https://github.com/Doctor-Gau-1607/case-ecg)'
MG = os.path.join(A.main, 'tools', 'medguide.py')
DS = json.load(open(os.path.join(A.main, 'du-lieu', 'danh-sach.json'), encoding='utf-8'))


PHIEN = 2


def anh_mat(f):
    from PIL import Image, ImageDraw
    im = Image.new('RGB', (900, 160), (246, 248, 250))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 899, 159], outline=(200, 205, 212), width=2)
    d.text((30, 60), 'Image no longer available on the original page (ekgblog.com) - anh goc khong con tren trang nguon',
           fill=(90, 100, 115))
    fmt = 'PNG' if f.lower().endswith('.png') else ('GIF' if f.lower().endswith('.gif') else 'JPEG')
    im.save(f, fmt)   # đổi khi quy tắc đặt tên media đổi -> tải lại


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
        for t in range(5):
            if subprocess.run(['git', '-C', A.nguon, 'push', '-q', 'origin', 'HEAD:nguon']).returncode == 0:
                return
            # một lượt khác vừa đẩy: kéo về rồi đặt thay đổi của mình lên trên (trùng tệp thì giữ bản mình)
            subprocess.run(['git', '-C', A.nguon, 'pull', '-q', '--rebase', '-X', 'theirs', '--depth', '50', 'origin', 'nguon'])
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
    shutil.rmtree(os.path.join(d, 'goc'), ignore_errors=True)
    os.makedirs(os.path.join(d, 'goc'), exist_ok=True)
    info = {'url': c['url'], 'loi': [], 'phien': PHIEN}
    try:
        from urllib.parse import urlparse
        san = os.path.join(A.trang, urlparse(c['url']).path.lstrip('/').replace('/', '_')) if A.trang else ''
        if san and os.path.isfile(san):
            shutil.copy(san, os.path.join(d, 'trang.html'))     # trang đã tải sẵn: không gọi ekgblog
            info['trang_san'] = True
        else:
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
            thu = [m['url'], m['url'].replace('/s1600/', '/s0/'), m['url'].replace('/s1600/', '/s1600-h/')]
            xong = hong = False
            for u in dict.fromkeys(thu):
                try:
                    data, _ = tai(u)
                    open(f, 'wb').write(data); xong = True
                    break
                except urllib.error.HTTPError as e:
                    if e.code != 404:
                        info['loi'].append(f"{u} {e}"); hong = True; break
                except Exception as e:  # noqa
                    info['loi'].append(f"{u} {e}"); hong = True; break
            if not xong and not hong:
                # ảnh đã mất trên chính trang nguồn (404): thay bằng ảnh báo, không làm kẹt cả case
                anh_mat(f)
                info.setdefault('anh_mat', []).append(m['url'])
            time.sleep(0.2)
        info['so_media'] = len(media)
    except Exception as e:  # noqa
        info['loi'].append(f"trang: {e}")
    info['luc'] = time.strftime('%Y-%m-%d %H:%M:%S')
    json.dump(info, open(nj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(c['slug'], 'media', info.get('so_media'), 'lỗi', len(info['loi']), flush=True)
    moi += 1; xong_lo += 1
    time.sleep(1 if info.get('trang_san') else 20)
    if xong_lo >= A.commit_moi:
        day_len(xong_lo); xong_lo = 0
day_len(xong_lo)
print('Xong lượt này:', moi, 'case')
