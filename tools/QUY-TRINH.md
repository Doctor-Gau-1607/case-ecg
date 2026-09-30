# Quy trình một lượt dịch Case ECG

Mỗi lượt (tác vụ hẹn giờ) dịch **5 case** kế tiếp của ECG Blog (Ken Grauer, ekgblog.com — tác giả đã cho phép) sang tiếng Việt, dựng trang theo khung MEDGUIDE và đẩy lên `main` của repo `Doctor-Gau-1607/case-ecg`. Trang công khai: `https://doctor-gau-1607.github.io/case-ecg/` (được nhúng trong MEDGUIDE, mục Cận lâm sàng → ECG → Case ECG).

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
python3 tools/lam_case.py chuan-bi --so 5
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
