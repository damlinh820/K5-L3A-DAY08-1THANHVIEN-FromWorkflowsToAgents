# Báo cáo cá nhân — 2A202603624_DamTuanLinh

## 1. Thông tin thành viên

- Họ tên: Đàm Tuấn Linh
- MSSV: 2A202603624
- Email: 26ai.linhdt3@vinuni.edu.vn
- GitHub: damlinh820

## 2. Phần việc phụ trách

Là thành viên duy nhất, tôi phụ trách toàn bộ ba shape học viên: workflow, single ReAct và orchestrator/handoff; đồng thời phụ trách durability, approval, trace safety, test, benchmark, ablation R4 và báo cáo.

## 3. Đóng góp cụ thể

- `b892e6b`: triển khai workflow cố định, giữ tính tiền trong code và dùng MockLLM để soạn phản hồi sau quyết định.
- `b3eb64c`: triển khai single agent với vòng ReAct tối đa 8 bước và tool chỉ đọc.
- `0e3287d`: triển khai orchestrator với handoff sanitize và investigator chỉ đọc.
- `9523182`: thêm `tests/test_shape_safety.py`, kiểm ticket override, approval, leak, idempotency và crash.
- `bb042dc`: thêm workflow_no_draft và 73 test ablation theo cặp.
- `a551fd1`: tạo benchmark chính thức và crash evidence bằng công cụ của lab.

Quyết định kỹ thuật chính là chọn workflow hiện tại: code sở hữu policy, số tiền và side effect; LLM chỉ diễn giải kết quả cho khách hàng. Quote luôn được truyền đầy đủ vào host để host áp trần theo đơn đúng một lần.

## 4. Bằng chứng

- Bảng đóng góp và các hash trong `TEAM.md`; lịch sử Git trên nhánh `main`.
- Test chính: `test_public_safety_independent_of_business_grading`, `test_ticket_cannot_override_structured_delay_or_policy`, `test_positive_quote_reaches_host_for_invalid_approval`, `test_cli_crash_then_resume_on_same_database`, `test_removing_draft_preserves_public_decisions_and_entire_money_state`.
- Run ID dẫn chứng: `R-workflow-C-014-s11` trong `src/reports/benchmark.json`.
- Kết quả: workflow pass 70/70 public trial, pass^5 14/14, variance 0; crash 20/20; safety public không có leak hoặc approval bypass.

## 5. Công cụ AI đã dùng

Tôi dùng Codex để đọc và đối chiếu tài liệu, hỗ trợ triển khai code, phân tích lỗi test, thiết kế test safety, chạy benchmark và chuẩn hóa báo cáo. Tôi không dùng AI để tạo số liệu giả: mọi số trong báo cáo được lấy từ JSON do CLI của lab sinh ra.

Tôi tự kiểm bằng `python -m pytest -q`, bộ `-m student`, crash suite 20/20, benchmark cùng corpus/seed, test ablation theo cặp và `python -m lab8.check_submission`. Tôi cũng kiểm Git diff để bảo đảm không sửa `metrics.py`, `durability.py`, `policy.py`, config hoặc data; kiểm trace/stdout không chứa secret và đối chiếu trực tiếp ledger/approval trong test safety.

## 6. Tự đánh giá

Tôi hoàn thành đủ ba kiến trúc, giữ đúng ranh giới code/model và xây được bằng chứng tái lập cho durability, safety và quyết định kiến trúc. Điểm cần cải thiện là chưa có `student_drop`, nên chưa tự kiểm được hành vi trên 40 claim hidden; MockLLM và corpus public nhỏ cũng chưa phản ánh chất lượng lời giải thích trong môi trường sản xuất. Nếu có thêm thời gian và dữ liệu, tôi sẽ chạy hidden self-check, đánh giá chất lượng thông báo khách hàng và thử thêm ticket mơ hồ bằng nhãn viết tay độc lập.
