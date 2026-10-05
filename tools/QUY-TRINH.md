# Quy trình một lượt dịch Case ECG

Mỗi lượt (tác vụ hẹn giờ) dịch các case kế tiếp (**làm liên tục khoảng 45–50 phút mỗi lượt, không giới hạn số case; nhận theo đợt `chuan-bi --so 10` — mỗi lần gọi là nhận thêm case mới; case đã nhận mà chưa kịp làm thì trả về "chua" cuối lượt**) của ECG Blog (Ken Grauer, ekgblog.com — tác giả đã cho phép) sang tiếng Việt, dựng trang theo khung MEDGUIDE và đẩy lên `main` của repo `Doctor-Gau-1607/case-ecg`. Trang công khai: `https://doctor-gau-1607.github.io/case-ecg/` (được nhúng trong MEDGUIDE, mục Cận lâm sàng → ECG → Case ECG).

- **Kho trang (từ 05/10/2026):** trang công khai của repo này đã vượt 1 GB nên trang + ảnh của các case nằm ở các kho `Doctor-Gau-1607/case-ecg-2` … `case-ecg-6` (Pages bật sẵn; kho chưa tạo thì `lam_case.py` báo lỗi quyền/không có repo → báo người dùng). `lam_case.py` **tự chọn kho đầu tiên còn dưới 900 MB**, clone sparse vào `/home/claude/khoken/<kho>`, ghi `"kho"` + `"kb"` vào case; `day-len` đẩy mọi kho đã dùng rồi mới đẩy danh sách. Repo chính giữ `index.html`, `du-lieu/`, `tools/`, nhánh `nguon`, trang của 31 case cuối (#518–#548, không có khoá `kho`) và trang chuyển hướng cho link cũ của các case đã chuyển. Bị từ chối quyền với kho nào thì gọi `add_repo` (owner `Doctor-Gau-1607`, repo đó, access `push`).
- **Bài mới:** workflow "Tải nguồn case ECG" (mỗi 6 giờ) chạy `tools/bai_moi.py` dò nguồn tin ekgblog.com, thêm case mới (tiêu đề có "#N") vào cuối danh sách với trạng thái `chua`, rồi tải nguồn. Lượt dịch hằng tuần (7:00 thứ Hai, giờ Việt Nam) dịch các case đó.

Nguồn (trang + ảnh gốc) đã được GitHub Actions tải sẵn vào nhánh `nguon`. **Không tự tải từ ekgblog.com** (container không truy cập được, và không cần).

## 0. Chuẩn bị (mỗi lượt là một phiên mới)

```bash
cd /home/claude
git clone -q --depth 1 --filter=blob:none --sparse https://github.com/Doctor-Gau-1607/case-ecg case-ecg
cd case-ecg && git sparse-checkout set tools du-lieu
git config user.name "Doctor-Gau-1607"; git config user.email "doctor.gau96@gmail.com"
pip list 2>/dev/null | grep -qi beautifulsoup4 || pip install -q --break-system-packages beautifulsoup4 lxml pillow
python3 tools/lam_case.py tien-do
```
Clone hoặc push bị từ chối vì quyền: gọi tool `add_repo` (owner `Doctor-Gau-1607`, repo `case-ecg`, access `push`) rồi làm lại. Không tìm cách khác.

## 1. Nhận case
```bash
python3 tools/lam_case.py chuan-bi --so 10
```
In "KHÔNG CÒN CASE NÀO SẴN SÀNG" → dừng lượt, báo lại (hết việc hoặc nguồn chưa tải tới).

## 2. Dịch từng case
Với mỗi case: đọc `/home/claude/cv/<slug>/W/lo/lo-NNN.json`, dịch thành `lo-NNN.vi.json` **cùng id, cùng các trường**, chỉ thay chữ. Đọc `tools/thuat-ngu.md` trước khi dịch, dùng thống nhất; gặp thuật ngữ mới hay gặp thì **thêm vào** tệp này (một dòng).

Quy ước (người đọc là bác sĩ):
- Dịch **trọn vẹn**: không tóm tắt, không bỏ câu, không gộp/cắt khối, không thêm "Kết luận".
- Thuật ngữ tiếng Việt chuẩn, lần đầu trong bài kèm tiếng Anh trong ngoặc khi hay gặp trong y văn: "tăng gánh thất trái (LV strain)". Viết tắt quốc tế giữ nguyên: ECG, STEMI, LBBB, RBBB, AV, PR, QRS, QTc, LVH, RVH, LAA, RAA, RAD, LAD, AFib, VT, SVT, OMI…
- Tên chuyển đạo giữ nguyên: I, II, III, aVR, aVL, aVF, V1–V6.
- **Giữ nguyên mọi thẻ HTML và thuộc tính** (`<b>`, `<i>`, `<u>`, `<span class="c-do">`, `<a href>`, `<li>`, `<tr><td style=…>`). Chỉ dịch chữ bên trong; được đổi vị trí thẻ theo trật tự câu tiếng Việt. **Số thẻ mỗi loại phải bằng bản gốc.**
- **Giữ mọi con số** (tần số, mV, ms, số hình, "#73"…). Không đổi `>>` `≥` v.v.
- Nhãn hình: `Figure N` → "Hình N", `Table N` → "Bảng N", `Video N` → "Video N"; giữ nguyên số. `alts`/`caps` dịch đủ số phần tử.
- Tên sách/blog/người, tiêu đề link tới bài khác ("ECG Blog #73") giữ nguyên.
- Lời thoại, câu hỏi của tác giả dịch tự nhiên, giữ giọng dạy học.
- Hai trường tùy chọn, chỉ khi thật cần: `"nang": 3` (đoạn chỉ gồm một ý in đậm làm đầu mục → tiêu đề h3); `"note": true` (câu chốt tác giả nhấn mạnh → hộp nổi).
- Bài dài: có thể giao từng lô cho agent con, kèm nguyên tệp này và `thuat-ngu.md`; tự đọc lại chỗ nối.

Tiêu đề trang (`--title`): dịch tiêu đề tiếng Anh của bài (xem dòng "Tiêu đề:" in ở bước 1), giữ "ECG Blog #N" / số case; ví dụ "ECG Blog #548 — Hơn một gia đình…".
Từ khoá (`--tu-khoa`): 8–20 từ tiếng Việt + Anh về chẩn đoán/dấu hiệu chính để tìm kiếm.

## 2b. Case có ảnh "mất" (khoá `anh_mat` trong nguon.json) — KHÔNG đăng với ảnh báo
Người dùng xác nhận: ảnh gốc **không hề mất** — mở bằng trình duyệt thật (Chrome) vẫn thấy; lỗi 404 chỉ xảy ra khi máy chủ GitHub Actions tải. Vì vậy:
- Ngay sau `chuan-bi`, với mỗi slug vừa nhận, đọc `/home/claude/cv/_nguon/<slug>/nguon.json`. Có khoá `anh_mat` (danh sách URL ảnh gốc) → case đó cần **ảnh thật** trước khi dựng.
- **Có công cụ Claude in Chrome** (`mcp__claude-in-chrome__*`, đọc skill chrome-browser trước): mở trang gốc (`url` trong nguon.json) trong Chrome, lấy từng ảnh trong `anh_mat` (tên tệp đích xem `/home/claude/cv/<slug>/W/media.json`: khoá `url` → `name`). Có máy người dùng (device bash) thì thử tải trước bằng curl kèm User-Agent trình duyệt + `Referer: <url trang gốc>`; không được thì lấy qua Chrome (tải về máy rồi stage lên phiên). Chép ảnh thật đè lên `/home/claude/cv/_nguon/<slug>/goc/<name>` (thêm `/<slug>/` vào sparse-checkout của `_nguon` nếu cần), kiểm ảnh mở được và không phải ảnh báo; trong nguon.json đổi `anh_mat` → `anh_chrome` (giữ danh sách URL); commit + push lên nhánh `nguon` ("Ảnh gốc qua Chrome: <slug>"). Rồi dịch/dựng như thường.
- **Không có Chrome**: KHÔNG dịch, KHÔNG dựng case đó. Sửa `du-lieu/danh-sach.json` bằng Python: `trang_thai="cho_anh"`, xoá `giu_luc`, `ly_do="ảnh gốc 404 từ máy chủ — cần tải qua Chrome"`; commit "Chờ ảnh gốc qua Chrome: …" + `day-len`. (`chuan-bi` không nhận lại case `cho_anh`.) Ghi số lượng case `cho_anh` vào báo cáo.
- Lượt có Chrome: xử lý các case `cho_anh` (số nhỏ trước) như trên, xong ảnh thì đặt lại `trang_thai="chua"` để dịch bình thường.
- Thông báo: KHÔNG gửi thông báo cho người dùng về các case `cho_anh` ở từng lượt (chỉ ghi trong báo cáo). Chỉ khi `chuan-bi` báo "KHÔNG CÒN CASE NÀO SẴN SÀNG" (đã dịch xong mọi case có thể) mới gửi MỘT thông báo gom danh sách các case còn sót (`cho_anh`, lỗi tải, `tra-lai`, trích lỗi) để người dùng tìm cách xử lý.
- Case ĐÃ đăng mà nguon.json có `anh_mat`: cũng lấy ảnh thật qua Chrome, đè vào `_nguon/<slug>/goc/` rồi `dung` lại (bản dịch `lo-*.vi.json` giữ nguyên nếu còn; nếu không, kéo trang đã đăng về đối chiếu).

## 3. Dựng + kiểm
```bash
python3 tools/lam_case.py dung --slug <slug> --title "<tiêu đề tiếng Việt>" --tu-khoa "<từ khoá>"
```
- `CHƯA ĐẠT` (LỖI số thẻ lệch, khối chưa dịch, y hệt bản gốc…): sửa `lo-*.vi.json`, chạy lại.
- Đọc từng dòng `CẢNH BÁO` (số thiếu/thừa, còn câu tiếng Anh dài): sửa nếu đúng là sót.
- Không sửa được sau 3 lần: `python3 tools/lam_case.py tra-lai --slug <slug> --ly-do "<vì sao>"` và làm case khác.

## 4. Đẩy lên
```bash
python3 tools/lam_case.py day-len
python3 tools/lam_case.py tien-do
```
Đẩy **sau mỗi case xong** cũng được (an toàn hơn nếu lượt bị ngắt giữa chừng).

## 5. Báo cáo cuối lượt
Một đoạn ngắn: case nào xong (số + tiêu đề tiếng Việt), case nào trả lại và lý do, tiến độ tổng (xong/tổng), có lỗi gì cần người xem.

## Không được làm
- Không sửa giao diện `index.html`, không động tới repo MEDGUIDE (`Dr.Gau`), không xoá case đã xong.
- Không đổi `tools/medguide.py`, `tools/tai_nguon.py`, workflow — nếu thấy lỗi công cụ, ghi vào báo cáo.
- Không thêm dòng "Bản dịch tiếng Việt của bài…" hay "Bấm vào hình để phóng to" (công cụ đã tự bỏ).
