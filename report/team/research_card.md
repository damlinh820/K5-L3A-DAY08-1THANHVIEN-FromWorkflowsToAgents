# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R4 · Evaluation confounders |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Zhang et al., 2026, *Rethinking the Evaluation of Efficiency Methods for Multi-Agent Systems*, EMNLP 2026; paper thực nghiệm/benchmark có kiểm soát; https://aclanthology.org/2026.emnlp-main.798/ |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Nhiều mức tăng hiệu quả MAS được báo cáo phụ thuộc setup; khi prompt, topology ban đầu và runtime không được kiểm soát, cải thiện có thể đến từ structural collapse, tool pathway bị vô hiệu hóa hoặc baseline mà random pruning vẫn giữ accuracy, thay vì phương pháp cấu trúc thực sự tốt hơn. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Kết luận thuộc các phương pháp tối ưu hiệu quả LLM-based MAS được paper khảo sát trên diagnostic benchmark của họ, với shared backbone model, agent registry và runtime; các biến topology, scale, depth và tool use được kiểm soát. Không suy rộng thành mọi multi-agent system hoặc mọi task sản xuất. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Bỏ đúng bước MockLLM draft khỏi workflow sẽ giữ nguyên pass rate, ledger và safety; model calls giảm 1 mỗi trial và cost/success giảm, chưa giả định mức giảm trước khi đo. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ MockLLM, tool, 14 claim, seed 11/22/33/44/55, pricing, evaluator, policy và logic tiền; biến duy nhất là bật/tắt một lần `complete(... purpose="draft")`. Chạy hai DB mới cho từng cặp và so toàn bộ ledger/audit/checkpoint. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Rủi ro: bỏ draft vô tình đổi quyết định hoặc crash path. Đo pass rate, pass^5, seed variance, model/tool calls, cost/success, trace steps; test theo cặp status/proposal/refund/ledger/audit/checkpoint và ba crash window. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,workflow_no_draft --extra-shape workflow_no_draft=bonus.workflow_no_draft:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/bonus_ablation.json`
- Run id / file report: `R-workflow-C-014-s11`, `R-workflow_no_draft-C-014-s11`; `src/reports/bonus_ablation.json`
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: Ủng hộ trên public. Hai bản đều pass 70/70, pass^5 14/14, variance 0; 70 cặp có ledger/audit/checkpoint giống nhau và ba crash window tương đương. Model calls trung bình 1→0; cost/success 28.895714→27.857143 VND mô phỏng, giảm 3.594206%; mean/p95 trace events 6.071429/7→5.071429/6.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`; chỉ 14 claim synthetic × 5 seed. Thí nghiệm không đo chất lượng lời giải thích cho khách hàng, nên kết quả không đủ để khuyến nghị bỏ draft trong sản phẩm.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
