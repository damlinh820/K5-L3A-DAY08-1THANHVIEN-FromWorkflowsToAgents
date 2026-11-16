# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: `1THANHVIEN`
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): `a551fd1`

## 2. Mục tiêu và cách tiếp cận

Bài toán yêu cầu xử lý cùng một claim hoàn phí bằng bốn kiến trúc, giữ tiền và side effect trong code, rồi chọn kiến trúc ít tự chủ nhất vẫn đáp ứng độ đúng và an toàn. Nhóm một thành viên triển khai tuần tự workflow, single ReAct và orchestrator; swarm có sẵn làm đối chứng. Mỗi shape được chặn bằng test riêng trước khi sang bước kế tiếp, sau đó kiểm idempotency, crash, approval, trace và benchmark trên cùng corpus/seed.

## 3. Giải pháp

`workflow` chạy thứ tự cố định: đọc claim qua view đã lọc, kiểm `order_id` và principal, tính quote từ order có cấu trúc/current policy, rồi gửi quote đầy đủ vào `issue_refund`. Host kiểm approval, trần theo đơn và idempotency. MockLLM chỉ nhận status/proposal sau quyết định để soạn lời giải thích cho khách hàng.

`single` dùng `run_react` tối đa 8 bước. Agent chỉ chọn tool đọc; hint parse từ ticket có thể khiến agent đọc thêm policy nhưng không thay dữ kiện order. Sau vòng lặp, code tính quote và gọi host.

`orchestrator` tạo `handoff.v1` chỉ chứa task, claim ID và allowlist tool đọc. Investigator đọc order, policy và refund history; coordinator tính quote và là thành phần duy nhất gọi host. Trace ghi handoff đã sanitize cùng các cờ/kết quả tối thiểu, không ghi parent context hoặc dữ liệu nhạy cảm.

Ở cả ba shape, tiền do `compute_compensation` quyết định, quote được truyền nguyên vẹn để host tự trừ refund trước đó. Trace không chứa ticket thô, secret, header, điện thoại, địa chỉ, tên hàng hay internal note. Connection luôn đóng trong `finally`; crash được truyền ra để retry dựa trên ledger.

## 4. Kết quả

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean/p95 steps |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| workflow | 1.000000 | 1.000000 | 1–1 | 0 | 28.895714 | 6.071429 / 7 |
| single | 1.000000 | 1.000000 | 1–1 | 0 | 38.635714 | 9.785714 / 11 |
| orchestrator | 1.000000 | 1.000000 | 1–1 | 0 | 58.740000 | 7.928571 / 9 |
| swarm | 0.985714 | 0.928571 | 0.928571–1 | 0.000816327 | 49.566957 | 2.8 / 3 |

Benchmark gồm 4 shape × 14 claim × 5 seed = 280 trial. Swarm sai duy nhất C-002/seed 55 vì tin số ngày trong ticket. Crash suite đạt 20/20; T11/T12 và 9 ca CLI crash-resume của ba shape tự viết đều đạt. Audit riêng trên 210 trial public có các counter secret, PII, context leak, approval bypass, ledger violation, trace error và exception đều bằng 0. Chưa có `student_drop`, nên không báo hidden pass rate.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Python trong sandbox không truy cập được runtime gốc; nhóm xác minh Python 3.11.9 đã cài, tạo `.venv` trong `src` và chạy test bằng môi trường đó. Baseline host thực tế là 54 test thay vì 52 như một dòng tài liệu. Lệnh `-k single` khớp cả tên hàm `test_public_single_run_cases`; nhóm đổi bộ lọc để chọn đúng 62 test single và giữ log lệnh gốc. Các cổng cuối đạt 391 test host, 248 test student và crash 20/20.

Nhóm thêm test ticket injection, approval thiếu/hết hạn/revoked/sai claim, amount conflict, unknown claim, ba crash window và quét trace/stdout độc lập. JSON report được tạo lại bằng CLI, không sửa tay.

## 6. Tổng hợp đóng góp

Một thành viên thực hiện toàn bộ implementation, safety test, benchmark, ablation và báo cáo. Hash và tên test cụ thể nằm trong `TEAM.md`; báo cáo cá nhân nằm tại `report/team/2A202603624_DamTuanLinh.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`; cost là mô phỏng. Public chỉ có 14 claim và swarm có điểm yếu seed 55 được thiết kế trước. Steps phụ thuộc cách ghi trace, không tương đương thời gian thực. Kết luận có thể đổi nếu hidden cho thấy workflow kém hơn ngưỡng 0.75, hoặc kiến trúc nhiều agent tăng đáng kể độ đúng ở claim mơ hồ mà vẫn giữ leak/bypass bằng 0 và crash an toàn.

Ablation R4 chỉ chứng minh trên setup này rằng bỏ draft không đổi ledger và giảm cost/success 3.594206%; nó không đo chất lượng lời giải thích cho khách hàng. Vì nhu cầu sản phẩm cần giải thích cả trường hợp failed, nhóm giữ draft trong workflow được chọn.

## 8. Tài liệu tham khảo

- Tài liệu nội bộ của lab: `README.md`, `docs/business_rules.md`, `docs/contracts.md`, `docs/architecture.md`, `docs/metrics.md`.
- Zhang et al. (2026), *Rethinking the Evaluation of Efficiency Methods for Multi-Agent Systems*, EMNLP 2026, benchmark thực nghiệm có kiểm soát: https://aclanthology.org/2026.emnlp-main.798/
