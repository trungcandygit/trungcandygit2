# Nhật ký chỉnh sửa đề cương

Tệp chính: `De_cuong_NCS_NguyenVanTrung.docx`. Tệp PDF chỉ là bản xem trước, xuất bằng LibreOffice.

## Cấu trúc theo hai bài mẫu (form DEM D2.2026, Trường Quốc tế)

Bìa → mục 1–3 → Mục lục, Danh mục bảng, Danh mục hình → 4. Đề cương sơ bộ dự kiến (4.1 Lý do chọn đề tài, câu hỏi và mục tiêu; 4.2 Tổng quan và khoảng trống; 4.3 Phương pháp / mô hình lý thuyết; 4.4 Đối tượng và phạm vi, đóng góp; 4.5 Bố cục luận án đến 3 chữ số) → 5 đến 11 theo form.

## Các vòng đã chạy

1. Viết lại theo cấu trúc mẫu. Bỏ mọi tham chiếu tới mục chưa xuất hiện (bản cũ nhắc mục 2.1, 3.1.2, 3.3, 3.5, 7 khi còn ở chương 1–2, và mục 7.2, 7.5 không tồn tại). Khái niệm được định nghĩa ngay ở lần dùng đầu.
2. Phản biện theo bộ ARS (academic-paper-reviewer: phương pháp, chuyên ngành, Devil's Advocate) và mục kiểm tra logic, góc nhìn người phản biện của awesome-ai-research-writing. Các sửa chính:
   - Nói rõ: cần 104 tuần ước lượng và 36 tháng kết quả ngoài mẫu mới chọn được mô hình, nên mức hối tiếc chỉ tính được từ khoảng năm thứ năm của mẫu (khoảng 28 cửa sổ đánh giá); khủng hoảng 2008 chủ yếu dùng để ước lượng chế độ.
   - Nói rõ thời điểm chọn mô hình: đầu mỗi cửa sổ đánh giá.
   - Sửa lập luận "Việt Nam phù hợp vì ít giai đoạn căng thẳng" (điều này làm kiểm định yếu đi, không phải lý do phù hợp).
   - Thêm "kể cả mã đã hủy niêm yết" để chống thiên lệch sống sót.
   - Bổ sung hai tài liệu đã xác minh: Pflug và cộng sự (2012), Kerkhof và cộng sự (2010).
3. Giảm viết tắt và tiếng Anh: bỏ CEQ, MCS, ILLIQ, ES, HAC, VIF, BMA, ARIMA, CPI, CAPM, ABC-MCMC, IMF và các ký hiệu Q1–Q3, G1–G4 trong phần thân; chỉ giữ HOSE, VN-Index, VN30, VN100, COVID-19 và tên văn bản (SR 11-7, Thông tư). Bỏ danh mục chữ viết tắt vì không còn cần. Khử văn mẫu AI theo awesome-ai-research-writing (去AI味, 润色) và stop-slop.
4. Proofreading theo awesome-thesis (Academic-Writing-Check: từ trùng, từ đệm, bị động, viết tắt, dấu câu) và writing_quality_check của ARS, chạy bằng `cong_cu/proofcheck.py`: sửa "chứng khóan" thành "chứng khoán", thống nhất "kỳ", "lý", "hóa"; chuyển khoảng 20 câu bị động sang chủ động; gạch ngang cho khoảng số; đối chiếu trích dẫn với danh mục tài liệu.
5. Hình: Hình 3 là SmartArt thật (Vertical Block List, quick style và màu mặc định của Office); Hình 1, 2 là Shape gốc của Word với style mặc định. Kiểm tra màu bằng skill dataviz: đạt; chữ trên khối cam đổi sang đen vì nền cam tương phản thấp với chữ trắng.
6. Dựng bản cuối: mục lục và danh mục có số trang, bảng không bị cắt dòng và lặp tiêu đề khi sang trang, công thức đánh số bên phải, tệp qua toàn bộ kiểm tra cấu trúc OOXML.

## Sửa theo góp ý sau khi mở bằng Word

- Chú thích bảng, hình không in đậm và danh mục bảng, hình bị lỗi: do style chú thích bị trùng tên khi chuyển đổi, Word dùng nhầm bản không định dạng. Đã đổi tên style cho khớp, danh mục dùng đúng style chú thích.
- Hình chuyển sang trắng đen: SmartArt dùng bảng màu Dark 1 Outline gốc của Office; Shape nền trắng, viền và mũi tên đen, ô "Đánh giá" ở Hình 2 nền xám nhạt để phân biệt.
- Bảng đen trắng, bỏ nền xám ở dòng tiêu đề; tiêu đề cột vẫn in đậm.
- Dòng "Nguồn" và ghi chú dưới bảng, hình: căn phải, in nghiêng.
- Danh mục tài liệu tham khảo: căn đều hai bên.

## Việc thí sinh cần tự làm

- Mở bằng Word, nếu được hỏi cập nhật trường (fields) thì chọn Yes để mục lục khớp dàn trang của Word.
- Điền: đơn vị công tác, người hướng dẫn, kiểm tra mã số chuyên ngành 9310116.01QTD (lấy theo bài mẫu cùng chương trình).
- Kiểm tra lại Hoang và Luu (2024), SSRN Working Paper No. 4867203: không truy cập được SSRN để xác minh.
- Mục 6 và 9 viết theo định hướng chung suy ra từ đề tài; nên chỉnh theo dự định thật của thí sinh.

## Dựng lại từ nguồn

```
python3 cong_cu/make_reference.py <reference pandoc giải nén> <M7 giải nén> reference.docx
python3 cong_cu/build.py <thư mục chứa de_cuong.md, refs_en.md, smartart/> out.docx pages.json
```
