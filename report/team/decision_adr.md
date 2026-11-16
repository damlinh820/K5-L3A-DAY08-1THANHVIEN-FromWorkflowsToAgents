# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: a551fd1
- Run id dẫn chứng: R-workflow-C-014-s11 (src/reports/benchmark.json)
- Pass rate / pass^5 / seed min-max / variance: 1.000000 / 1.000000 / 1.000000–1.000000 / 0.000000
- Cost per success (mô phỏng, VND): 28.895714
- Crash safety: 20/20 (src/reports/crash.json); T11/T12 và 9 ca CLI crash-resume của ba shape đều đạt
- Secret leak / approval bypass: 0 / 0 trên 70 trial public của workflow (src/reports/public_safety.json); chưa có counter hidden

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Chọn `workflow` hiện tại, có bước MockLLM soạn lời giải thích sau quyết định. Trên cùng 14 claim, năm seed `11,22,33,44,55`, MockLLM, tool, bảng giá và evaluator, workflow đạt 70/70 trial, pass^5 14/14 và variance 0. `single` và `orchestrator` cũng đạt 70/70 nhưng cost/success lần lượt là 38.635714 và 58.740000 VND mô phỏng, cao hơn workflow 28.895714. Workflow là kiến trúc ít tự chủ nhất vẫn đạt đúng và ổn định trên bộ public; code giữ quyền tính tiền, kiểm policy và ghi ledger, còn LLM chỉ diễn giải kết quả cho khách hàng.

## Có đáng đổi lấy multi-agent không

Không có lợi ích đo được để đổi sang multi-agent trên corpus public: orchestrator tốn hơn workflow 50.807432% mà pass rate và variance không cải thiện; swarm còn sai C-002 ở seed 55. Nhóm sẽ đổi quyết định nếu hidden cho thấy workflow dưới ngưỡng 0.75 hoặc single/orchestrator cải thiện đáng kể độ đúng ở ticket mơ hồ mà vẫn qua ba must-pass, hoặc khi bài toán sản xuất cần ranh giới triển khai và quyền sở hữu riêng giữa các investigator. Việc giữ LLM draft không giao thêm quyền quyết định: ablation R4 cho thấy bỏ draft giữ nguyên ledger nhưng chỉ giảm 3.594206% cost/success; nhóm giữ draft để giải thích `resolved`, `denied`, `failed`, `needs_info` và `escalated` cho khách hàng.

## Trace và bằng chứng

Workflow ghi `claim_lookup`, `order_lookup`, quote chỉ có `amount_vnd`, `refund_requested`, kết quả host chỉ có cờ `ok/conflict`, quyết định và câu draft. Trace cố ý không ghi ticket thô, `parent_secret`, raw header, điện thoại, địa chỉ, tên hàng, ghi chú nội bộ, approval ID hay toàn bộ claim/order row. `trace_path` nằm trong `src/traces/`; scanner đọc chính file đó, mọi file cùng tiền tố run ID trong thư mục trace và thư mục `traces`, đồng thời quét JSON kết quả. Test safety còn bắt stdout/stderr và đối chiếu trực tiếp ledger/approval. Nếu chuyển trace ra ngoài vùng scanner, hệ thống không còn bằng chứng fail-closed; vì vậy nhóm không dùng vị trí ngoài phạm vi quét để lưu debug.

## Giới hạn

Kết luận dựa trên 14 claim synthetic và năm seed public; chưa có `student_drop`, hidden pass rate và counter hidden. MockLLM không đại diện model sản xuất, chi phí chỉ là VND mô phỏng và latency là `unavailable`. Steps là số event trace nên không thể dùng như latency giữa các shape. Swarm có điểm yếu seed 55 được cài chủ đích. Các JSON bằng chứng đều do công cụ sinh, không sửa để đạt ngưỡng 0.75.
