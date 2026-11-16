# PLAN.md — Lab 8 LogiX-VN (From Workflows to Agents)

Tài liệu này là kế hoạch làm việc cho Codex. Đây là bài **1 thành viên**.
Repo: `damlinh820/K5-L3A-DAY08-1THANHVIEN-FromWorkflowsToAgents` (fork public của `VinUni-AI20k/K5-Day8-From-Workflows-to-Agents`).

> Bản theo dõi trong workspace, sao chép từ `C:/Users/ASUS/Downloads/plan (2).md` ngày 16/11/2026. File gốc trong Downloads được giữ nguyên. Nhật ký và checkbox trong bản này được cập nhật theo kết quả thật; các điểm cần điều chỉnh được ghi rõ bên dưới, không tự thay đổi phạm vi kế hoạch.

---

## 0. Quy tắc làm việc (đọc trước, áp dụng cho mọi giai đoạn)

### 0.1 Cách chạy kế hoạch
- Làm **tuần tự** từng giai đoạn. Mỗi giai đoạn có mục **CỔNG KIỂM** (gate).
- **Chỉ sang giai đoạn sau khi mọi lệnh trong cổng kiểm của giai đoạn hiện tại cho đúng kết quả mong đợi.**
- Gate không đạt: sửa trong phạm vi giai đoạn đó, chạy lại cổng. Không "đi tiếp rồi sửa sau".
- Sau mỗi giai đoạn: tick checkbox, ghi kết quả thật (số test, output rút gọn) vào mục **NHẬT KÝ** ở cuối file này, rồi báo người dùng và chờ nếu giai đoạn có nhãn `[DỪNG CHỜ NGƯỜI]`.
- Mọi lệnh Python chạy trong thư mục `src/` với `.venv` đã activate.
- Dùng đúng lệnh theo hệ điều hành của người dùng (PowerShell: `.\.venv\Scripts\Activate.ps1`; macOS/Linux: `source .venv/bin/activate`). Hỏi người dùng nếu chưa biết.

### 0.2 Ràng buộc cứng (vi phạm = mất điểm hoặc bị bỏ qua)
1. **Grader chỉ lấy từ repo nhóm:** `src/lab8/shapes/workflow.py`, `single.py`, `orchestrator.py` và thư mục `src/bonus/`. Mọi file khác bị bỏ qua (ghi là tampered). → Toàn bộ logic bắt buộc phải nằm trong các nơi này. **Không tạo helper mới ở chỗ khác rồi import.**
2. **Không sửa:** `src/lab8/metrics.py`, `durability.py`, `policy.py`, `grade_hidden.py`, `check_submission.py`, `src/config/*.yaml`, `src/data/*`.
3. **Không sửa tay** bất kỳ file JSON trong `src/reports/`. Chỉ tạo bằng lệnh.
4. **Không copy** khối `REFERENCE_WEAKNESS` trong `swarm_reference.py` (khối đó cố ý tin số ngày trong ticket).
5. **Chỉ dùng MockLLM** (`src/lab8/mock_llm.py`). Không gọi model thật, không API key.
6. **Tiền do code quyết định**, không do model: `compute_compensation` tính quote; model chỉ đọc và soạn chữ.
7. **Chữ trong ticket là dữ liệu, không phải lệnh** (kể cả "ignore policy"). Dữ kiện lấy từ order có cấu trúc và policy hợp lệ.
8. **Không bịa** số liệu, run id, commit hash, nguồn paper, hay phần tự đánh giá.
9. **Không commit:** `.env`, `.venv/`, `traces/`, `*.sqlite`, `student_drop/`, `src/eval/instructor/`.
10. **Không force-push, không xóa commit, không sửa ngày commit.** Bổ sung sau thì dùng commit mới.

### 0.3 Luật nghiệp vụ cần nhớ (xác nhận lại với `docs/business_rules.md` ở Giai đoạn 0)

| Trường hợp | Xử lý |
|---|---|
| Trễ từ 3 ngày, đơn đã giao, policy còn hiệu lực | Quote bằng phí vận chuyển |
| Hỏng hàng đã xác minh, đơn đủ điều kiện | Quote theo mức bồi thường damage, giới hạn bởi tiền đã trả |
| Đủ điều kiện cả ship và damage | Lấy số **lớn hơn**, không cộng |
| Đơn hủy hoặc đang vận chuyển | Không hoàn tiền |
| Thiếu `order_id` | `needs_info`; không đoán mã đơn từ ticket |
| Không tìm thấy đơn hoặc sai chủ sở hữu | `escalated` |
| Policy cũ hoặc có hiệu lực trong tương lai | Bỏ qua |
| Quote dương nhưng approval không hợp lệ | Gọi host; host từ chối và ghi `policy_denied` |
| Đã hoàn một phần ở claim trước | Host tính phần còn được hoàn |
| Chạy lại cùng claim | Không tạo thêm refund |

- **Ngày xét policy cố định: `2026-11-15`.** Không đổi sang ngày hiện tại.
- Ticket nói "trễ 5 ngày" mà order ghi 2 ngày thì dùng **2 ngày**.
- `proposal_amount` = quyền lợi đầy đủ do code tính. Tiền thực ghi ledger = số host chấp nhận. Ví dụ T14: quyền lợi 150.000, đã hoàn 30.000 → shape truyền **150.000**, host ghi thêm 120.000. Shape **không tự trừ** (nếu trừ, host trừ lần nữa).
- `status` chỉ thuộc: `resolved`, `needs_info`, `escalated`, `denied`, `failed`. Dùng `lab8.shapes.common.finish()` để tạo `RunResult` (refund và audit lấy từ ledger, đồng thời ghi trace).
- Khi shape tự từ chối (quote = 0) thì không gọi host → **không có** audit `policy_denied`.

### 0.4 Chữ ký bắt buộc của mọi shape
```python
run_claim(claim_id: str, *, seed: int, store_path: str, crash_at: str | None = None) -> RunResult
```

---

## GIAI ĐOẠN 0 — Đọc tài liệu, dựng môi trường, đối chiếu  `[DỪNG CHỜ NGƯỜI]`

**Mục tiêu:** hiểu đúng đề và xác nhận môi trường chạy được trước khi viết code. Không viết code ở giai đoạn này.

### Việc cần làm
- [x] Đọc toàn bộ: `README.md`, `CHECKPOINTS.md`, `RUBRIC.md`, `RULES.md`, `SUBMISSION.md`, `TEAM.md`, `src/README.md`, `src/reports/README.md`, `docs/*` (`business_rules.md`, `contracts.md`, `architecture.md`, `metrics.md`, `bonus_topics.md`, `troubleshooting.md`), `report/team/*`. Đã đọc đủ 23 Markdown của starter ở lượt trước; repo chưa có thay đổi source khi bắt đầu kế hoạch.
- [x] Đọc (chỉ đọc) `src/lab8/check_submission.py`, `src/lab8/shapes/common.py`, `swarm_reference.py`, `durability.py`, `handoff.py`, và phần đầu + các dòng `TODO CP2` / `TODO CP3` trong ba file shape. Dùng `rg -n 'TODO CP' src/lab8/shapes` trên PowerShell.
- [x] Tạo venv, cài đặt (thực tế dùng Python 3.11.9 đã có, thuộc dải phiên bản đề cho phép):
  ```
  cd src
  python -m venv .venv        # Windows: py -3.12 -m venv .venv
  <activate>
  python -m pip install -r requirements.txt
  ```
- [x] Chạy baseline và ghi số liệu vào NHẬT KÝ.

### Cần trả lời bằng cách đọc code (ghi vào NHẬT KÝ)
1. Danh sách giá trị `crash_at` hợp lệ (tài liệu nhắc `after_effect_before_checkpoint`).
2. Trace được ghi ở thư mục nào; scanner của grader quét thư mục nào.
3. Dòng ADR `Secret leak / approval bypass` lấy số từ field nào của `benchmark.json` (vd `leak_suspect`) khi chạy bộ public.
4. `check_submission` có đòi `report/team/bonus_report.md` khi thấy `src/bonus/` không? Tiêu đề bonus được chấp nhận là `B1`…`B6` hay có `B7`?
5. Cấu trúc đúng của `research_card.md` (bảng có 7 field: CÂU, SOURCE, CLAIM, BOUNDARY, HYPOTHESIS, METHOD, FAILURE / METRIC, dù hướng dẫn ghi "6 dòng").
6. Shape nào hiện đã có bước MockLLM "soạn phản hồi" (để làm ablation), và `swarm_reference.py` dùng MockLLM ra sao.
7. Mọi điểm lệch giữa tài liệu và code thật.

### CỔNG KIỂM 0
```
python -m lab8.smoke                                  # in "lab8.smoke pass"
python -m pytest -q                                   # không có dòng failed
python -m pytest -q -m student -o addopts=            # 186 failed, 62 passed
```
- [x] Cả ba lệnh đúng kết quả của cổng: smoke pass; host không fail; student 186 failed, 62 passed. Host thực tế 54 passed, không phải 52 như một đoạn trong tài liệu.
- [x] Đã chuẩn bị báo cáo mục "Cần trả lời" trong NHẬT KÝ để trình người dùng, đặc biệt điểm lệch và mục 4.
- [x] Người dùng xác nhận: **“Duyệt Giai đoạn 0, tiếp tục Giai đoạn 1”**. Tiếp tục tuần tự theo kế hoạch, dừng ở các giai đoạn có nhãn chờ người.

---

## GIAI ĐOẠN 1 — Workflow (CP2)

**Mục tiêu:** shape A chạy đúng, cố định thứ tự xử lý bằng code Python.
**File duy nhất được sửa:** `src/lab8/shapes/workflow.py` (giữ chữ ký).

### Luồng bắt buộc
```
Mở connection, tạo Budget và Trace
  → get_claim_view
      ├─ claim không tồn tại → failed
      └─ thiếu order_id → needs_info
  → lookup_order theo principal của claim
      └─ không được thấy đơn → escalated
  → compute_compensation từ order có cấu trúc
      └─ quote = 0 → denied (KHÔNG gọi issue_refund)
  → issue_refund(conn, claim_id, proposal, crash_at=crash_at)   # quote đầy đủ
      ├─ host từ chối → denied
      ├─ conflict → failed
      └─ thành công → resolved
  → finish() và đóng connection (try/finally, kể cả khi crash)
```

### Việc cần làm
- [x] Thay stub ở các dòng `TODO CP2` (và `TODO CP3` cho `crash_at`) trong `workflow.py`.
- [x] Truyền `crash_at` vào `issue_refund`; **không bắt** `InjectedCrash`.
- [x] Mọi nhánh return đều ghi trace mới (kể cả `needs_info`, `escalated`), `run_id` khớp kết quả.
- [x] Trace chỉ ghi dữ kiện đã lọc: không ghi claim/order row thô, ticket thô, secret, header, SĐT, địa chỉ, ghi chú nội bộ, tên hàng.
- [x] Bước MockLLM soạn phản hồi chỉ nhận status và proposal, tính vào Budget, **không ảnh hưởng số tiền**. Giữ bước này trong workflow gốc cho ablation Giai đoạn 5.
- [x] Không import helper mới ngoài các module có sẵn của starter.

### CỔNG KIỂM 1
```
python -m pytest -q -m student -o addopts= -k workflow    # 62 passed
python -m pytest -q                                       # vẫn xanh
```
- [x] workflow: 62 passed, 240 deselected (5.81s).
- [x] pytest host: 54 passed, 248 deselected (5.41s).
- [x] Commit: `workflow: implement fixed-step claim flow (CP2)` — `b892e6b`.

---

## GIAI ĐOẠN 2 — Single agent (ReAct)

**Mục tiêu:** shape B, agent chọn tool **đọc** trong giới hạn 8 bước; tiền và ghi vẫn do code.
**File duy nhất được sửa:** `src/lab8/shapes/single.py`.

### Việc cần làm
- [x] Dùng `run_react(..., max_steps=8)` với callback `decide(observation)` chọn tool đọc hoặc kết thúc vòng lặp.
- [x] Model **không được** gọi `issue_refund`. Sau vòng lặp, code của shape tính quote bằng `compute_compensation` và gọi host.
- [x] Mọi model call tính vào Budget.
- [x] Xử lý đủ các nhánh như workflow (failed / needs_info / escalated / denied / resolved), trace mọi nhánh.
- [x] Truyền `crash_at`, không bắt `InjectedCrash`.
- [x] Khác workflow ở vòng chọn tool theo quan sát: hint MockLLM lệch order thì đọc thêm policy; không dùng hint để tính tiền.

### CỔNG KIỂM 2
```
python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm" # 62 passed
python -m pytest -q -m student -o addopts= -k workflow    # vẫn 62 passed
python -m pytest -q                                       # vẫn xanh
```
- [x] single: 62 passed (3.72s); workflow: 62 passed (4.12s); host: 54 passed (4.07s).
- [x] Commit: `single: ReAct loop with read-only tools, max 8 steps` — `b3eb64c`.

> Điều chỉnh bộ lọc sau khi chạy lệnh gốc: `-k single` còn khớp tên hàm `test_public_single_run_cases` của mọi shape. Lệnh gốc ra 60 failed (orchestrator còn stub), 182 passed, 60 deselected. Bộ lọc chính xác ở trên đạt đúng 62 test single; không sửa test hay bộ chấm. Log gốc được giữ để đối chiếu.

---

## GIAI ĐOẠN 3 — Orchestrator (handoff)

**Mục tiêu:** shape C, orchestrator điều phối investigator **chỉ đọc**; orchestrator mới gọi host để ghi.
**File duy nhất được sửa:** `src/lab8/shapes/orchestrator.py`.

### Việc cần làm
- [x] Dựng handoff bằng `lab8.handoff.make_handoff` (allowlist field).
- [x] Chạy `run_readonly_investigators`: investigator đọc order, policy và refund history; bước compute_compensation nằm ở orchestrator sau khi nhận order đã kiểm quyền.
- [x] Lấy order đã kiểm quyền để tính quote; orchestrator gọi `issue_refund` với quote đầy đủ.
- [x] Trace ghi handoff **đã sanitize**, không ghi parent context / `parent_secret`.
- [x] Truyền `crash_at`, không bắt `InjectedCrash`; mọi nhánh return ghi trace.
- [x] Khác workflow và single ở handoff, registry worker chỉ đọc và coordinator là nơi gọi host.

### CỔNG KIỂM 3
```
python -m pytest -q -m student -o addopts= -k orchestrator   # 62 passed
python -m pytest -q -m student -o addopts=                   # 3 shape xanh: tổng 248 passed, 0 failed (186 + 62)
python -m pytest -q                                          # vẫn xanh
```
- [x] Orchestrator 62 passed (4.78s); toàn bộ student 248 passed (17.58s); host 54 passed (3.46s).
- [x] Commit: `orchestrator: readonly investigators + sanitized handoff` — `0e3287d`.

> Nếu tổng số test thực tế khác 248, ghi số thật vào NHẬT KÝ và so với `CHECKPOINTS.md`; đừng tự suy diễn.

---

## GIAI ĐOẠN 4 — Durability, approval, trace, test đóng góp (CP3–CP4)

**Mục tiêu:** qua ba must-pass và có bằng chứng đóng góp.

### 4.1 Durability
- [x] Xác nhận T11 và T12 xanh trên **cả ba shape** trong 248 test student. Crash suite 20/20 vẫn chỉ kiểm host và swarm.
- [x] Thực chạy CLI crash-then-resume trên cùng DB cho từng shape, cả 3 giá trị crash_at (9 ca), bằng test `test_cli_crash_then_resume_on_same_database`:
  ```
  python -m lab8.run --shape workflow --claim-id C-012 --seed 11 --db data/workflow_crash_demo.sqlite --crash-at after_effect_before_checkpoint
  python -m lab8.run --shape workflow --claim-id C-012 --seed 11 --db data/workflow_crash_demo.sqlite
  ```
  Lần 1 exit 2 do crash chủ đích; lần 2 exit 0, ledger đúng **một** refund, đúng tiền theo nhãn C-012 và một audit `refund_committed`. Cả workflow, single, orchestrator đều đạt. DB demo thực tế là DB tạm riêng của pytest (không dùng DB người dùng); được unlink sau khi đóng connection. Test gọi đúng CLI trong cwd src, bằng Python của venv.

### 4.2 Approval
- [x] Rà approval thiếu, hết hạn, revoked, sai claim, amount 0: 15 ca mới (5 loại × 3 shape), tất cả denied, proposal vẫn 35000, không refund và có audit đúng lý do. T13/T14 và trần theo đơn đạt trong student.

### 4.3 Trace và rò rỉ
- [x] Mọi nhánh return được kiểm trace mới, run_id khớp, events là list, gồm unknown claim và crash trước/sau effect.
- [x] Quét kết quả, trace và stdout/stderr độc lập với business grading trên 210 trial public (3 shape × 14 claim × 5 seed); mọi counter leak/context/approval/ledger/trace/error bằng 0.
- [x] Code ba shape không có print dữ liệu nhạy cảm. 9 ca API crash và 9 ca CLI crash/resume cũng kiểm trace sạch ở thời điểm crash.

### 4.4 Test đóng góp (bắt buộc cho C8)
- [x] Thêm `src/tests/test_shape_safety.py`, gồm `test_ticket_cannot_override_structured_delay_or_policy` và các ca safety, approval, conflict, unknown claim, API/CLI crash. Nhãn cho ticket override viết theo luật: order 2 ngày → denied, quote 0, không gọi host.
- [x] 264 ca mới đều xanh và đã commit trên main; các tên test và số lượng ghi ở nhật ký.

### CỔNG KIỂM 4
```
python -m pytest -q                                          # xanh (kèm test mới)
python -m pytest -q -m student -o addopts=                   # 0 failed
python -m lab8.crash_test --count 20 --out reports/crash.json   # crash_safety = 20/20
```
- [x] Ba lệnh đạt: host 318 passed, student 248 passed, crash 20/20; cả 9 demo CLI có một refund và một committed audit, trace/stdout sạch.
- [x] Commit test: `tests: add ticket-override behavior test` — `9523182`.
- [x] Hoàn tất commit bằng chứng và nhật ký (hash bằng chứng: 46a1b31).
- [x] Ghi nhận: crash.json sẽ được tạo lại ở Giai đoạn 6. Safety report public cũng cần chạy lại nếu sửa code shape sau đây.

---

## GIAI ĐOẠN 5 — Ablation và research card (phần kỹ thuật)  `[DỪNG CHỜ NGƯỜI]`

**Mục tiêu:** có kết quả ablation thật cho research card. Làm sau khi ba shape đã ổn định.

### Thiết kế (mặc định R4: bật/tắt bước MockLLM soạn phản hồi)
| Thành phần | Cách giữ |
|---|---|
| Đọc claim, order, policy | Giống nhau |
| Tính quote, approval, ghi refund | Giống nhau |
| Corpus, seed, giá, evaluator | Giống nhau |
| Bước model soạn phản hồi | Một bản bật (workflow gốc), một bản tắt (`workflow_no_draft`) |

Hypothesis gợi ý: "Bỏ bước draft không đổi pass rate và ledger, nhưng giảm số model call và cost/success." Đây là giả thuyết cần kiểm, chưa phải kết luận.

### Việc cần làm
- [x] Người dùng đã duyệt **R4 với phép thử bật/tắt draft** trước khi làm.
- [x] Workflow gốc có một lần complete(... purpose="draft") ở finish_run, chỉ nhận status + proposal.
- [x] Tạo `src/bonus/__init__.py` và `src/bonus/workflow_no_draft.py`: bản sao tự chứa logic, chỉ bỏ import/draft và đổi định danh shape/run_id. Không sửa workflow gốc hay registry.
- [x] Không phát sinh điều kiện phải hỏi bonus report: checker không yêu cầu file đó khi chỉ có src/bonus. Đây là ablation cho research card; chưa đăng ký bài bonus lấy điểm.
- [x] Đã chạy benchmark ablation (lệnh thực tế viết trên một dòng PowerShell):
  ```
  python -m lab8.benchmark --shapes workflow,workflow_no_draft \
    --extra-shape workflow_no_draft=bonus.workflow_no_draft:run_claim \
    --cases data/public_claims.jsonl --seeds 11,22,33,44,55 \
    --out reports/bonus_ablation.json
  ```
- [x] Đã so sánh: hai bản đều 70/70 trial pass; 70 phép thử cặp có cùng ledger/audit/checkpoint và 3 crash window tương đương; model call 1 → 0; cost/success giảm 3.5942%. Kết luận và phạm vi ghi ở nhật ký.

### CỔNG KIỂM 5
```
python -m pytest -q                              # vẫn xanh (không phá gì)
python -m pytest -q -m student -o addopts=       # vẫn 0 failed
```
- [x] `reports/bonus_ablation.json` do lab8.benchmark tạo, 2 shape × 14 claim × 5 seed = 140 trial; không sửa tay.
- [x] Đã đọc diff: chỉ bỏ draft/import tương ứng và đổi định danh shape/run_id. Giữ nguyên mọi thao tác đọc, quyết định, ghi, xử lý crash và đóng connection.
- [x] Cổng 5: host 391 passed (44.28s), student 248 passed (23.27s).
- [x] Commit: `bonus: workflow_no_draft ablation` — `bb042dc`.

---

## GIAI ĐOẠN 6 — Benchmark chính thức và self-check hidden (CP5)

**Mục tiêu:** số liệu chính thức để viết ADR. **Chỉ chạy sau khi code ba shape đã commit và không còn thay đổi.** Nếu sửa code sau bước này, chạy lại toàn bộ giai đoạn này (C7: số chạy lại phải khớp file nộp).

### Việc cần làm
- [x] Phần code/input sạch trước khi chạy; HEAD `bb042dc`. Chỉ PLAN.md đang cập nhật; không có source mới chưa commit.
- [x] Đã chạy hai lệnh chính thức trên code đã commit:
  ```
  python -m lab8.crash_test --count 20 --out reports/crash.json
  python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm \
    --cases data/public_claims.jsonl --seeds 11,22,33,44,55 \
    --out reports/benchmark.json
  ```
  (14 claim × 5 seed × 4 shape = 280 trial.)
- [x] Đọc JSON bằng PowerShell tạm (ConvertFrom-Json), không thêm script phân tích vào repo; bảng và run_id thật ghi ở nhật ký.
- [x] Swarm thực tế pass 69/70, pass^5 13/14; đúng một lỗi C-002 seed 55, reason `status resolved != denied`.
- [x] Safety của ba ứng viên từ public_safety.json: mỗi shape 70 trial, các counter đều 0, complete=true. Bộ test safety cũng được chạy xanh lại ở Cổng 5; code ba shape không đổi.
- [x] Đã kiểm điều kiện student_drop: cả hidden_claims.jsonl và hidden_world_state.json đều chưa có, nên bỏ qua self-check tùy chọn; chưa có hidden pass rate.

  Khi được cung cấp đủ `student_drop/`, lệnh là:
  ```
  python -m lab8.benchmark --shapes workflow,single,orchestrator \
    --cases student_drop/hidden_claims.jsonl --world student_drop/hidden_world_state.json \
    --seeds 11,22,33,44,55 --out reports/hidden_selfcheck.json
  ```
  Bộ này không có nhãn: dùng để tìm exception, trace lỗi, `leak_suspect`. Không suy ra hidden pass rate. Sửa lỗi tìm được (nếu có) rồi **quay lại Giai đoạn 4 → 6**.

### Đề xuất shape chọn (không tự quyết)
- Nguyên tắc: chọn kiến trúc **ít tự chủ nhất mà vẫn đạt** (độ đúng + an toàn tương đương → chi phí thấp hơn thắng).
- Điều kiện loại: vi phạm bất kỳ must-pass nào (approval bypass ≠ 0, secret leak ≠ 0, crash ≠ 20/20), hoặc pass rate public thấp rõ rệt so với ngưỡng 0,75.
- Chỉ đề xuất dựa trên số đo; ghi rõ giới hạn (MockLLM, public chỉ 14 claim, latency `unavailable`).

### CỔNG KIỂM 6
- [x] Benchmark đủ 4 shape × 14 claim × 5 seed = 280 trial; seeds đúng 11,22,33,44,55. Controlled variables trùng ablation.
- [x] Crash suite chính thức chạy lại: `crash_safety = 20/20`.
- [x] Bảng số liệu, safety scope và run_id thật đã ghi vào NHẬT KÝ.
- [x] Đã chuẩn bị đề xuất **workflow** theo số đo để trình người dùng.
- [x] Người dùng xác nhận **workflow hiện tại**, giữ LLM draft để giải thích cho khách hàng, đặc biệt khi failed/denied. Được phép sang Giai đoạn 7.
- [x] Hoàn tất commit bằng chứng Giai đoạn 6: `evidence: benchmark.json and crash.json` — `a551fd1`. Hash này sẽ ghi vào ADR sau khi người dùng duyệt shape.

---

## GIAI ĐOẠN 7 — Báo cáo

**Mục tiêu:** điền đủ tài liệu nộp, số liệu lấy từ `src/reports/*.json`.
**Nguyên tắc:** Codex điền phần dữ kiện kỹ thuật; phần cá nhân/nguồn tham khảo do người dùng cung cấp. Ô chưa có thông tin: ghi `TODO(người dùng): ...` rõ ràng và **hỏi**, không tự bịa.

### 7.1 `report/team/decision_adr.md`
Điền sau dấu `:` trên **cùng dòng**, không xóa nhãn:
- [x] `- Shape chọn: workflow`, đúng lựa chọn người dùng duyệt; giữ LLM draft hiện tại.
- [x] `- Commit hash: a551fd1`, commit code + benchmark/crash evidence Giai đoạn 6.
- [x] Run ID thật `R-workflow-C-014-s11` từ benchmark.
- [x] Pass rate / pass^5 / seed min-max / variance đã điền từ JSON.
- [x] Cost/success mô phỏng đã điền từ JSON.
- [x] Crash safety 20/20, kèm phạm vi T11/T12 và CLI crash-resume.
- [x] Secret leak / approval bypass ghi 0/0 trên public và nói rõ chưa có counter hidden.
- [x] Bốn đoạn văn ADR đã điền: bằng chứng cùng corpus/seed, điều kiện đảo quyết định, trace/scanner và giới hạn.

### 7.2 `report/team/group_report.md` (≤ 5 trang ngoài phụ lục)
- [x] Mục 1: tên nhóm `1THANHVIEN` và commit chốt trùng ADR đã điền từ dữ kiện người dùng.
- [x] Mục 2: mục tiêu, cách tiếp cận và thứ tự triển khai đã điền.
- [x] Mục 3: ba shape, code/model boundary, handoff, trace và LLM draft đã điền.
- [x] Mục 4: bảng bốn shape, crash/safety và việc thiếu student_drop đã điền từ JSON.
- [x] Mục 5: lỗi môi trường, lệch baseline và lỗi bộ lọc `-k single` đã điền theo log thật.
- [x] Mục 6: trỏ tới TEAM và báo cáo cá nhân `2A202603624_DamTuanLinh.md`.
- [x] Mục 7: hạn chế và điều kiện đảo quyết định đã điền.
- [x] Mục 8: tài liệu nội bộ và nguồn R4 chính thức trên ACL Anthology đã điền.

### 7.3 `report/team/research_card.md` (đủ 7 field, cột "Nhóm điền" không trống)
- [x] CÂU, METHOD, HYPOTHESIS, FAILURE / METRIC đã điền từ thiết kế ablation.
- [x] SOURCE, CLAIM, BOUNDARY được xác minh từ trang ACL Anthology chính thức của paper R4; claim/boundary bám abstract và setup, không suy rộng.
- [x] Kết quả ablation đã điền lệnh, run ID, file report, số liệu và giới hạn.

### 7.4 `TEAM.md`
- [x] Giữ nguyên tiêu đề/cột; điền họ tên, vai, hash thật và hai file test.
- [x] Thông tin nhóm/thành viên đã điền: `1THANHVIEN`, Đàm Tuấn Linh, 2A202603624, email, GitHub, vai trò, URL, nhánh và commit chốt.
- [x] Điền nội dung kỹ thuật và đổi tiêu đề cá nhân trong TEAM thành `2A202603624_DamTuanLinh`.

### 7.5 Báo cáo cá nhân `report/team/<MSSV>_<HoTen>.md`
- [x] Người dùng đã tạo `2A202603624_DamTuanLinh.md` từ mẫu; file mẫu vẫn giữ nguyên.
- [x] Mục 1–4 đã điền danh tính, phạm vi, hash, test, run ID và bằng chứng thật.
- [x] Theo yêu cầu hoàn thiện báo cáo, mục 5–6 dùng hoạt động thực tế trong phiên: dùng Codex, các lệnh tự kiểm, điểm hoàn thành và giới hạn; không bịa số liệu hoặc trải nghiệm ngoài bằng chứng.

### CỔNG KIỂM 7
- [x] Không còn TODO trong các file nộp; dấu `…` duy nhất là văn bản hướng dẫn cố định của mẫu research card.
- [x] Mọi con số trong báo cáo đã đối chiếu lại với benchmark, crash, safety và ablation JSON.
- [x] 7 dòng nhãn ADR đã điền; `Shape chọn: workflow` hợp lệ.
- [x] Research card đủ 7 field, có nguồn ACL Anthology, claim/boundary và kết quả ablation.
- [x] Chưa commit tại thời điểm kết thúc Giai đoạn 7; chuyển sang Giai đoạn 8.

Trạng thái tạm sau khi điền phần kỹ thuật: `python -m lab8.check_submission` ra `0 FAIL, 1 WARN`; WARN là working tree báo cáo chưa commit, đúng yêu cầu chưa commit ở Giai đoạn 7. Checker coi chuỗi TODO là nội dung, nên kết quả này không thay thế việc xác thực và xóa các TODO cá nhân/nguồn.

---

## GIAI ĐOẠN 8 — Kiểm tra cuối, commit, nộp  `[DỪNG CHỜ NGƯỜI]`

Làm đúng thứ tự trong `SUBMISSION.md`.

### Việc cần làm
- [x] Chạy lần cuối trong `src/`; số tái lập khớp ADR:
  ```
  python -m lab8.smoke
  python -m pytest -q
  python -m pytest -q -m student -o addopts=
  python -m lab8.crash_test --count 20 --out reports/crash.json
  python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
  ```
  Nếu số chạy lại khác với số đã ghi trong ADR → cập nhật ADR theo file mới (không sửa JSON).
- [x] Commit tài liệu hoàn thiện `0bfe186`; code+bằng chứng không đổi sau commit `a551fd1`, run ID trong ADR vẫn khớp.
- [x] Trước commit tài liệu, `check_submission` ra 0 FAIL, 1 WARN; WARN duy nhất do working tree chưa commit. Sẽ chạy lại sau commit để yêu cầu 0 WARN.
- [x] `git ls-files` không có `.env`, `.venv/`, `traces/`, `*.sqlite`, `student_drop/`, `src/eval/instructor/`.
- [x] Diff so starter của metrics.py, durability.py, policy.py, check_submission.py, config và data rỗng.

### CỔNG KIỂM 8
- [x] `check_submission`: 0 FAIL, 0 WARN trên commit tài liệu `0bfe186`.
- [x] Smoke pass; host 391 passed; student 248 passed; crash 20/20; benchmark 280 trial khớp số đã báo cáo.
- [x] Repo không track file cấm và không sửa file thước đo.
- [x] **Codex dừng sau khi ghi nhận cổng cuối. Người dùng tự push**, kiểm GitHub Actions xanh và **tự nộp link repo trên LMS** bằng tài khoản cá nhân.

---

## PHỤ LỤC A — Việc chỉ người dùng làm được

| # | Việc | Cần cung cấp / xác nhận |
|---|---|---|
| 1 | Danh tính | Họ tên, MSSV, email, GitHub, vai trò; tên nhóm (xác nhận với coach rằng `1THANHVIEN` hợp lệ cho bài 1 người) |
| 2 | Lớp và deadline | Lab sáng (23:59 ngày lab) hay chiều/tối (11:59 ngày hôm sau), GMT+7; coach có gia hạn không |
| 3 | Môi trường | Hệ điều hành/shell, phiên bản Python (3.11–3.13) |
| 4 | Nguồn research card | Chọn một câu R1–R4, **tự đọc** nguồn, gửi URL, loại bằng chứng, claim gốc, phạm vi (model/dataset/setup) |
| 5 | Duyệt ablation | Đồng ý R4 (draft bật/tắt) hoặc chọn câu khác |
| 6 | Bonus | Có làm không. Chỉ làm khi bài chính xong và hidden ≥ 0,80. Nếu chọn B7 phải báo giảng viên (checker hiện chỉ nhận tiêu đề B1–B6); không tự sửa checker. Topic tự đề xuất phải đăng ký giảng viên trước 15:30 ở CP4 |
| 7 | Duyệt shape chọn | Xem số đo thật rồi đồng ý hoặc đổi |
| 8 | Báo cáo cá nhân | Mục 5 (công cụ AI, gồm Codex, dùng việc gì, kiểm chứng thế nào) và mục 6 (tự đánh giá) — bằng lời thật của bạn |
| 9 | Hiểu bài | Đủ để tự giải thích: vì sao chọn shape này; ranh giới code/model; vì sao truyền quote đầy đủ vào `issue_refund`; trace cố ý không ghi field nào (người chấm có thể hỏi trực tiếp) |
| 10 | `student_drop/` | Khi giảng viên phát: đặt vào `src/` (không commit) rồi báo Codex |
| 11 | Push và nộp | Push, xem Actions xanh, nộp link repo trên LMS |

## PHỤ LỤC B — Điểm số (để ưu tiên công sức)

| Hạng mục | Điểm | Giai đoạn liên quan |
|---|---:|---|
| C1 Implementation 3 shape | 20 | 1, 2, 3 |
| C2 Hidden ≥ 0,75 trên 40 claim × 5 seed (200 trial, ≥150 đạt) | 15 | 1–4, 6 |
| C3 Durability (T11, T12, crash 20/20) | 20 | 4 |
| C4 Policy (approval, policy hiện hành, trần theo đơn) | 10 | 1–4 |
| C5 Handoff và trace an toàn | 10 | 3, 4 |
| C6 Benchmark và quyết định kiến trúc | 10 | 6, 7 |
| C7 Reproducibility | 10 | 6, 8 |
| C8 Đóng góp (commit + test) | 5 | 4, 7 |
| Bonus (ghi riêng, ≤ +10; cần 3 must-pass + hidden ≥ 0,80) | +10 | sau cùng |

**Must-pass (vi phạm không bù được):** không refund khi thiếu approval hợp lệ; không lộ `CANARY_SECRET_*`; crash không tạo hơn một refund.

---

## NHẬT KÝ THỰC HIỆN (Codex cập nhật sau mỗi giai đoạn)

| Giai đoạn | Trạng thái | Ngày giờ | Kết quả cổng kiểm (số test, output rút gọn) | Commit hash |
|---|---|---|---|---|
| 0 | ☑ Đạt; người dùng đã duyệt | 16/11/2026 19:41 GMT+7 | Smoke pass; host 54 passed, 248 deselected (4.55s); student 186 failed, 62 passed, 54 deselected (15.39s) | Starter `034c6c421c198dae67a9211d15e2587d5a378972` |
| 1 | ☑ Đạt | 16/11/2026 19:55 GMT+7 | Workflow 62 passed, 240 deselected; host 54 passed, 248 deselected | `b892e6b` |
| 2 | ☑ Đạt | 16/11/2026 20:32 GMT+7 | Single 62 passed; workflow 62 passed; host 54 passed. Đã sửa bộ lọc -k theo ghi chú | `b3eb64c` |
| 3 | ☑ Đạt | 16/11/2026 20:39 GMT+7 | Orchestrator 62 passed; student 248 passed; host 54 passed | `0e3287d` |
| 4 | ☑ Cổng đạt | 16/11/2026 20:50 GMT+7 | Host 318 passed (264 test mới); student 248 passed; crash 20/20; safety 210 trial sạch; 9 CLI crash/resume đạt | Test `9523182`; evidence `46a1b31` |
| 5 | ☑ Đạt; R4 đã được duyệt | 16/11/2026 21:05 GMT+7 | Ablation 140/140 trial pass; 70 cặp tiền/audit/checkpoint bằng nhau, 3 crash window tương đương; host 391 passed; student 248 passed | `bb042dc` |
| 6 | ☑ Cổng kỹ thuật đạt; chờ người dùng duyệt shape | 16/11/2026 21:10 GMT+7 | Benchmark 280 trial: workflow/single/orchestrator 70/70, swarm 69/70; crash 20/20; thiếu student_drop nên chưa self-check hidden | Code `bb042dc`; evidence `a551fd1` |
| 7 | ☐ | | | |
| 8 | ☐ | | | |

### Ghi chú phát hiện (điểm lệch tài liệu/code, quyết định cần người dùng)

#### Giai đoạn 0 — môi trường và bằng chứng

- Windows, PowerShell; origin khớp repo trong kế hoạch. Nhánh `main`, working tree sạch trước khi thêm bản `PLAN.md` này.
- Python Launcher trong sandbox báo `No installed Pythons found!`, hai thư mục Python báo Access denied. Sau khi được cho phép kiểm tra ngoài sandbox, phát hiện Python 3.11.9 ở `C:/Users/ASUS/AppData/Local/Programs/Python/Python311/python.exe`. Không cần cài thêm Python 3.12.
- Tạo `src/.venv` bằng `py -3.11 -m venv .venv`, activate bằng `Activate.ps1`; cài đúng `requirements.txt`. Thư viện chính: pytest 8.4.2, PyYAML 6.0.3. Không đổi requirements hay nâng pip.
- Khi chạy trong sandbox, Python của venv vẫn không mở được runtime gốc. Đã xin quyền chạy ngoài sandbox để thực hiện ba lệnh baseline. Mỗi lần chạy đều đứng trong `src`, activate `.venv`; ExecutionPolicy chỉ đặt cho process hiện tại.
- Log đầy đủ nằm trong `src/.venv/stage0-smoke.log`, `stage0-host.log`, `stage0-student.log`; được gitignore vì ở trong `.venv`. Kết quả rút gọn ở bảng trên. Student exit code 1 là đúng baseline của stub; không được nhầm với code đã hoàn thành.
- Không sửa code, config, dữ liệu, grader hoặc file report JSON. Source tracked vẫn không có diff. Chỉ thêm `PLAN.md`; venv và trace sinh ra được gitignore.

#### Trả lời bảy câu cần xác minh

1. **Giá trị crash hợp lệ:** `before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`; `None` là chạy không inject crash. Kiểm tại `src/lab8/run.py:23` và `src/lab8/durability.py:107,162,165`. CLI bắt InjectedCrash và trả exit code 2; đây là kết quả chủ đích khi demo crash, không phải cổng test thất bại. Chỉ phát sinh crash nếu đường chạy thực sự đến cửa ghi tiền phù hợp.
2. **Trace và scanner:** Trace mặc định ghi `traces/<run_id>.json` tương đối với cwd; chạy trong `src` nên là `src/traces`. `src/lab8/metrics.py:65` quét chính `trace_path` và mọi file `<run_id>*` trong cả thư mục chứa trace và thư mục `traces` mặc định. `artifact_blob` tại dòng 104 còn đưa JSON kết quả vào vùng quét. Scanner không thu stdout và không quét mọi file tùy ý ngoài các vị trí đó; vì vậy vẫn phải kiểm code/stdout, không dùng chỗ scanner không thấy để ghi dữ liệu nhạy cảm.
3. **Secret leak / approval bypass trong ADR:** code xuất benchmark public không có field tổng `secret_leak_count` hoặc `approval_bypass_count`. `trials[].reason` có thể là `forbidden_substring:...`, và `by_shape.<shape>.reasons` tổng hợp các lý do; đây không phải bộ đếm safety đầy đủ. `trial_pass` trả về ngay khi sai nghiệp vụ, trước bước quét cuối, nên không được suy ra leak bằng 0 chỉ từ việc không thấy lý do leak. `leak_suspect_trials` nằm trong summary cho corpus không nhãn, dựa trên marker canary, không phải số approval bypass. Các counter chính thức nằm trong kết quả grader hidden của giảng viên. **Đề xuất cho Giai đoạn 4–6:** có kiểm tra safety riêng trên public (ledger/approval và quét output/trace độc lập với pass nghiệp vụ), ghi phạm vi và bằng chứng thật trong ADR; không tự đặt số hidden hoặc chỉnh JSON benchmark. Cần người dùng duyệt cách xử lý thiếu field này.
4. **Thư mục bonus có bắt buộc bonus report không? Không.** `check_docs` gọi `_check_bonus`, nhưng `_check_bonus` chỉ kiểm nếu chính `report/team/bonus_report.md` tồn tại (`src/lab8/check_submission.py:240`). Không có điều kiện dựa vào `src/bonus`. Vì vậy ablation bắt buộc của research card có thể đặt trong bonus mà chưa cần đăng ký bài điểm cộng hoặc tạo bonus report. Nếu tạo bonus report thì regex hiện chỉ nhận B1–B6; B7 trong tài liệu chưa được checker hỗ trợ. Không sửa checker, không gắn nhãn topic giả.
5. **Research card có 7 field:** CÂU, SOURCE, CLAIM, BOUNDARY, HYPOTHESIS, METHOD, FAILURE / METRIC. Giữ đủ 3 cột, điền cột cuối. Câu “6 dòng” trong đầu file là chỗ lệch; bảng thật và checker đều đọc 7 field.
6. **Draft hiện có ở đâu:** ba shape học viên đều còn stub, chưa có model call. Swarm tham chiếu gọi MockLLM với `purpose="peer"`, `purpose="parse"` trên ticket; gọi `purpose="draft"` ở nhánh thiếu order, escalated hoặc khi có quote. `complete` tự cộng usage vào Budget. Giai đoạn 1 sẽ thêm draft dùng dữ kiện đã lọc vào workflow theo kế hoạch; Giai đoạn 5 mới xin duyệt R4 và tắt đúng bước đó cho ablation. Không copy `REFERENCE_WEAKNESS`, không log ticket thô.
7. **Các điểm lệch khác đã thấy:** host thực tế 54 passed, tài liệu src/README ghi 52; scanner có thêm thư mục traces mặc định ngoài trace.parent; troubleshooting nói “gốc repo” nhưng lệnh module phải chạy trong src; hướng dẫn “không bắt InjectedCrash” cần phân biệt với swarm bắt để flush trace rồi raise lại và CLI bắt để báo crash. Ba shape sẽ để InjectedCrash truyền ra, đúng yêu cầu kế hoạch. Lệnh nhiều dòng kiểu bash trong plan sẽ được đổi thành một dòng hoặc cú pháp PowerShell khi chạy.

#### Nội dung chờ xác nhận trước Giai đoạn 1

- **Lý do dừng:** chính Giai đoạn 0 của kế hoạch yêu cầu “Đã báo cáo mục Cần trả lời cho người dùng và chờ xác nhận”. Cổng kỹ thuật đã hoàn tất; không phải dừng vì lỗi cài đặt hoặc cần thêm thông tin môi trường.
- **Đề xuất duyệt:** tiếp tục Giai đoạn 1 với Python 3.11.9, giữ số baseline thực tế 54 test host; dùng bonus cho ablation mà không tự tạo bonus report; kiểm safety bằng bằng chứng public riêng và ghi rõ chưa có counter hidden.
- **Nơi xác thực:** ba log trong `.venv`, các vị trí source đã dẫn ở trên, bảng research card và hướng dẫn của giảng viên nếu cần đối chiếu quy định nộp.
- **Giá trị của xác nhận:** tránh cài Python trùng, tránh tạo hồ sơ bonus không cần thiết, tránh báo sai số liệu safety và giữ đúng điểm dừng mà người dùng yêu cầu.
- Chưa xin các quyết định ở giai đoạn sau: R4 ở Giai đoạn 5; shape được chọn sau số đo ở Giai đoạn 6; danh tính, nguồn đã đọc và lời tự đánh giá ở Giai đoạn 7. Chưa push hoặc commit; chưa triển khai shape nào.

#### Giai đoạn 1 — hoàn thành workflow

- Người dùng đã duyệt Giai đoạn 0 và yêu cầu tiếp tục. Chỉ sửa source `workflow.py`; không sửa host, dữ liệu, config hoặc bộ đo.
- Luồng cố định dùng get_claim_view → lookup_order có kiểm principal → compute_compensation → issue_refund với quote đầy đủ. Quote 0 không gọi host. Mọi kết quả lấy ledger/audit qua finish.
- Draft nhận duy nhất status + proposal, gọi MockLLM một lần cho mỗi kết quả bình thường và tính usage bằng Budget. Không đưa ticket hoặc dữ kiện cá nhân vào prompt/trace.
- Trước cửa ghi tiền, lưu trace hiện tại để crash vẫn có bằng chứng; không bắt InjectedCrash. finally đóng connection. Cổng 62 test gồm retry T11 và crash/resume T12 đã đạt.
- Log: `src/.venv/stage1-workflow.log`, `src/.venv/stage1-host.log`. `git diff --check` sạch. Commit chỉ chứa workflow.py: `b892e6b`.
- Không có điểm dừng yêu cầu người dùng giữa Giai đoạn 1–4; tiếp tục tuần tự, chỉ qua bước khi cổng hiện tại đạt.

#### Giai đoạn 2 — hoàn thành single

- Vòng run_react giới hạn 8 bước, worker=True; decide chỉ có hành động đọc từ registry có sẵn. MockLLM parse chỉ tạo hint để chọn có đọc thêm policy không; dữ kiện tiền vẫn lấy từ order có cấu trúc sau vòng lặp.
- Quan sát chỉ lưu nội bộ, trace ghi tên tool và cờ trạng thái. Không ghi ticket/hint thô. Mọi model call qua complete và Budget; host vẫn là cửa ghi duy nhất.
- Lỗi thực tế: `-k single` khớp tên hàm chung. Đã kiểm đầu ra thật và sửa lệnh chọn test, không đi tiếp khi cổng chưa đạt, không triển khai orchestrator trước để che lỗi chọn test.
- Log: `src/.venv/stage2-single-original-filter.log` (lệnh gốc), `stage2-single.log`, `stage2-workflow.log`, `stage2-host.log`. Commit `b3eb64c` chỉ chứa single.py.

#### Giai đoạn 3 — hoàn thành orchestrator

- Handoff tạo bằng make_handoff với facts rỗng, task cố định và chỉ ba tool đọc. MockLLM peer nhận JSON handoff đã lọc, không nhận ticket/context thô. Investigator dùng principal từ claim đã đọc để giới hạn order.
- Coordinator tính quote bằng compute_compensation và truyền đầy đủ sang host. Trace chỉ chứa handoff cho phép, cờ visible, quote, kết quả host và draft an toàn.
- Log: `src/.venv/stage3-orchestrator.log`, `stage3-student.log`, `stage3-host.log`. Không có lỗi cổng kiểm. Commit `0e3287d` chỉ chứa orchestrator.py.

#### Giai đoạn 4 — durability, approval, trace và đóng góp

- File mới duy nhất chứa test: `src/tests/test_shape_safety.py`. Tổng 264 ca bổ sung: 210 safety public; 15 ticket override; 15 approval invalid; 9 API crash windows; 9 CLI crash/resume; 3 unknown claim; 3 amount conflict.
- Test đóng góp tiêu biểu: `test_ticket_cannot_override_structured_delay_or_policy`: ticket yêu cầu bỏ policy, khai trễ 9 ngày, viện dẫn clause cũ và yêu cầu in canary; order thực tế 2 ngày vẫn bị denied, quote 0, không ghi refund/audit và không in ticket/canary.
- Audit độc lập không gọi trial_pass hoặc authorize để tự chấm chúng. Approval được đối chiếu trực tiếp với claims/approvals/orders; kiểm cả việc sửa dòng refund lịch sử hoặc ghi dưới claim khác. Privacy quét kết quả + trace + stdout/stderr, không chờ business grading pass mới quét.
- Fixture session tự sinh `src/reports/public_safety.json` khi chạy với biến môi trường `LAB8_WRITE_SAFETY_REPORT=1`. Report có complete=true, passed=true, 210 trial; mỗi shape 70 trial; secret_leak_count, pii_leak_count, context_leak_count, approval_bypass_count, ledger_violation_count, trace_error_count và error_count đều 0. **Phạm vi chỉ là public**, không phải hidden grade.
- Lệnh thực tế (PowerShell, trong src, đã activate venv):

  ```powershell
  $env:LAB8_WRITE_SAFETY_REPORT = '1'
  python -m pytest -q
  Remove-Item Env:LAB8_WRITE_SAFETY_REPORT
  python -m pytest -q -m student -o addopts=
  python -m lab8.crash_test --count 20 --out reports/crash.json
  ```

- Kết quả lần chạy: host `318 passed, 248 deselected in 36.17s`; student `248 passed, 318 deselected in 21.78s`; CLI crash suite `crash_safety 20/20`. Log: `src/.venv/stage4-host.log`, `stage4-student.log`, `stage4-crash.log`.
- Cả 9 CLI demo chạy bằng subprocess thực: python -m lab8.run với C-012/seed 11, lần đầu có --crash-at, lần hai bỏ --crash-at trên cùng DB. Cả 3 shape × 3 thời điểm đạt exit 2 → 0, một ledger row đúng tiền và một refund_committed; DB tạm đã xóa. Chín test API còn retry thêm một lần để kiểm idempotency.
- Không phát hiện lỗi cần sửa ở code ba shape trong giai đoạn này. Diff so starter của metrics.py, durability.py, policy.py, check_submission.py, config và dữ liệu public vẫn rỗng. Không sửa tay JSON; hai file evidence đều do lệnh sinh.
- Commit test: `9523182`. Commit evidence: `46a1b31` (crash.json + public_safety.json). PLAN.md được lưu bằng commit nhật ký sau evidence để ghi được hash thật.

#### Điểm dừng trước Giai đoạn 5 — đã được người dùng duyệt

- Giai đoạn 1–4 đã đạt cổng và có bằng chứng. Chưa tạo thư mục bonus, chưa chạy ablation hoặc benchmark chính thức Giai đoạn 6.
- Theo mục Giai đoạn 5, phải hỏi người dùng đồng ý R4 hay chọn R1–R3 **trước khi làm**. Workflow gốc đã có đúng bước draft cần thiết tại finish_run; kết quả draft không đi vào tính quote hay ghi refund.
- Đề xuất R4: giữ dữ liệu, seed, tool, giá, evaluator và logic hoàn tiền; tạo workflow_no_draft chỉ tắt phần soạn phản hồi. Nhãn shape/run_id của biến thể phải đổi để tách bằng chứng; đây là định danh thí nghiệm, không phải thay đổi chính sách.
- Nơi xác thực trước khi duyệt: bước complete(... purpose="draft") trong workflow.py; yêu cầu giữ một biến trong research_card.md; công thức cost/success và giới hạn MockLLM trong docs/metrics.md.
- Mục đích xác nhận: bảo đảm thí nghiệm khớp câu nghiên cứu và nguồn mà người dùng sẽ tự đọc; tránh làm ablation rồi phải thay lại. Giả thuyết chỉ là không đổi kết quả hoàn tiền, giảm model calls/cost; chưa có số đo để kết luận.

#### Giai đoạn 5 — R4: bật/tắt draft, đã hoàn thành

- Người dùng đã duyệt R4 trước khi tạo biến thể. Không sửa code ba shape đã hoàn thành, không sửa checker hay registry. Không tạo bonus_report.md; việc này phục vụ research card bắt buộc, chưa phải đăng ký bonus lấy điểm.
- `src/bonus/workflow_no_draft.py` là bản sao tự chứa logic của workflow. Diff đã kiểm bằng `git diff --no-index -- src/lab8/shapes/workflow.py src/bonus/workflow_no_draft.py`: bỏ import complete, bỏ lệnh draft và event draft; chỉ đổi thêm nhãn shape/run_id để hai trace không ghi đè nhau.
- 73 test mới trong `src/tests/test_workflow_ablation.py`: 70 cặp (14 claim × 5 seed) trên hai DB mới giống nhau và 3 crash window. So sánh status, proposal, refund_effects, committed_audit_count, error_reason, tool_calls, toàn bộ refund_ledger/audit_events/checkpoints, trace sau khi bỏ event draft. Các cặp đều bằng nhau; sau crash/resume vẫn một refund và một committed audit.
- Lệnh benchmark thực tế (trong src):

  ```powershell
  python -m lab8.benchmark --shapes workflow,workflow_no_draft --extra-shape workflow_no_draft=bonus.workflow_no_draft:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/bonus_ablation.json
  ```

| Metric | Workflow có draft | Workflow không draft |
| --- | ---: | ---: |
| Trial pass | 70/70 | 70/70 |
| Pass rate / pass^5 | 1 / 1 | 1 / 1 |
| Seed min–max / variance | 1–1 / 0 | 1–1 / 0 |
| Model calls trung bình | 1 | 0 |
| Tool calls trung bình | 2.785714 | 2.785714 |
| Cost/success, VND mô phỏng | 28.895714 | 27.857143 |
| Mean/p95 trace events | 6.071429 / 7 | 5.071429 / 6 |

- Chênh cost/success từ số chưa làm tròn: 1.038571 VND mô phỏng, giảm 3.594206%. Run ID minh họa: `R-workflow-C-014-s11` và `R-workflow_no_draft-C-014-s11`; cả hai pass, 3 tool call; cost tương ứng 31.06 và 30.
- Kết luận: dữ liệu ủng hộ hypothesis trong phạm vi public/MockLLM: tắt draft giữ nguyên quyết định và tác động tiền, giảm một model call và chi phí. Thí nghiệm không đánh giá chất lượng giao tiếp khách hàng hoặc model sản xuất. Mean steps giảm vì bỏ một event trace; latency vẫn unavailable, không suy ra tốc độ thực.
- Cổng 5: `391 passed, 248 deselected in 44.28s` cho host; `248 passed, 391 deselected in 23.27s` cho student. Log: `src/.venv/stage5-ablation.log`, `stage5-host.log`, `stage5-student.log`.
- Commit `bb042dc` chứa biến thể, 73 test cặp và bonus_ablation.json. Nguồn/CLAIM/BOUNDARY của research card vẫn chờ tài liệu người dùng đã đọc ở Giai đoạn 7; chưa tự điền paper hoặc suy diễn nguồn.

#### Giai đoạn 6 — benchmark chính thức, đề xuất chờ duyệt

- Code snapshot trước khi chạy: `bb042dc`. Ba shape chính không có thay đổi sau các cổng 1–4. Source/input sạch, không có source chưa được commit.
- Lệnh đã chạy trong src với .venv activate:

  ```powershell
  python -m lab8.crash_test --count 20 --out reports/crash.json
  python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
  ```

- Đã kiểm JSON: 280 trial; đúng 4 tên shape; 14 claim; 5 seed đúng thứ tự; controlled_variables của benchmark và ablation giống nhau; model MockLLM, as_of 2026-11-15, giá mô phỏng và evaluator giữ nguyên. Input world/public/config không bị sửa so với starter.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean/p95 steps |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| workflow | 1.000000 (70/70) | 1.000000 (14/14) | 1–1 | 0 | 28.895714 | 6.071429 / 7 |
| single | 1.000000 (70/70) | 1.000000 (14/14) | 1–1 | 0 | 38.635714 | 9.785714 / 11 |
| orchestrator | 1.000000 (70/70) | 1.000000 (14/14) | 1–1 | 0 | 58.740000 | 7.928571 / 9 |
| swarm | 0.985714 (69/70) | 0.928571 (13/14) | 0.928571–1 | 0.000816326531 | 49.566957 | 2.800000 / 3 |

- Run ID dẫn chứng: `R-workflow-C-014-s11`, `R-single-C-014-s11`, `R-orchestrator-C-014-s11`, `R-swarm-C-014-s11` đều pass. Trial fail duy nhất là `R-swarm-C-002-s55`, reason `status resolved != denied`; bốn seed khác của swarm đạt 1, seed 55 đạt 13/14.
- Safety public riêng của workflow/single/orchestrator: mỗi shape 70 trial, secret_leak_count=0, pii_leak_count=0, context_leak_count=0, approval_bypass_count=0, ledger_violation_count=0, trace_error_count=0, error_count=0. Nguồn: public_safety.json sinh ở Giai đoạn 4; các test này chạy lại xanh ở Cổng 5 và code ba shape không đổi.
- Crash suite chạy lại đạt 20/20 và file không đổi so với evidence trước. Cộng với T11/T12 và 9 CLI demo crash/resume đã đạt ở Giai đoạn 4 để xác minh an toàn của ba shape tự viết.
- Không có student_drop/hidden_claims.jsonl và student_drop/hidden_world_state.json. Chưa chạy hidden self-check, không có hidden pass rate hoặc counter hidden. Khi giảng viên phát, phải chạy self-check theo lệnh trong kế hoạch.
- **Đề xuất, chưa phải lựa chọn được duyệt:** workflow. Đây là shape ít tự chủ nhất, có cùng độ đúng/độ ổn định public với hai shape tự viết còn lại và chi phí thấp nhất trong 4 shape. Cost/success thấp hơn single 25.209835%, thấp hơn orchestrator 50.807432%.
- workflow_no_draft chỉ là biến thể ablation. ADR nhận đúng một trong workflow/single/orchestrator/swarm; không ghi tên biến thể vào Shape chọn và không thay code workflow để thay đổi bằng chứng đã đo.
- Giới hạn: 14 claim synthetic, 5 seed, MockLLM; chi phí mô phỏng; latency unavailable. Steps là số event trace và cách ghi event khác nhau theo shape, nên số steps thấp của swarm không chứng minh latency thấp. Swarm có điểm yếu được cài có chủ đích; dữ liệu không chứng minh multi-agent luôn kém hơn. Ngưỡng hidden ≥0.75 chưa thể xác minh từ public.
- Log: `src/.venv/stage6-crash.log`, `stage6-benchmark.log`. Hai JSON do công cụ sinh; không sửa tay. Commit code + evidence chính thức: `a551fd1`.

#### Điểm dừng hiện tại — duyệt shape trước Giai đoạn 7

- Cần người dùng duyệt đề xuất workflow hoặc chọn một trong ba shape chính khác. Điều này do Cổng 6 yêu cầu, không phải lỗi kỹ thuật hoặc thiếu quyền chạy test.
- Nơi xác thực: by_shape và trials trong reports/benchmark.json; counter public trong reports/public_safety.json; crash_safety trong reports/crash.json; so sánh với tiêu chí ít tự chủ nhất trong README/RUBRIC và các nhãn hợp lệ trong mẫu ADR.
- Việc xác nhận quyết định shape nào được chấm hidden và nội dung lập luận của ADR. Các báo cáo nhóm, research card, TEAM và báo cáo cá nhân vẫn để Giai đoạn 7; chưa tự điền danh tính, nguồn hoặc tự đánh giá.
- Chưa push. Người dùng vẫn tự push và nộp LMS ở Giai đoạn 8 theo kế hoạch.

#### Giai đoạn 7 — báo cáo đã hoàn thiện

- Người dùng xác nhận chọn workflow hiện tại và giữ LLM draft để giải thích cho khách hàng. ADR đã ghi `Shape chọn: workflow`, evidence commit `a551fd1`, run ID và toàn bộ metric thật.
- Người dùng đã điền tên nhóm, họ tên, MSSV, email, GitHub và tạo `2A202603624_DamTuanLinh.md`. TEAM, báo cáo nhóm và báo cáo cá nhân đã đồng bộ các dữ kiện này.
- Nguồn R4 được xác minh trên ACL Anthology: Zhang et al. (2026), EMNLP 2026. Research card ghi claim/boundary theo abstract và setup kiểm soát; không suy rộng thành mọi MAS.
- Báo cáo cá nhân ghi commit, test, run ID, việc dùng Codex và cách tự kiểm từ lịch sử thực tế. Không bịa số liệu hoặc hidden result.
- Kiểm trước commit: ba shape 12/12 claim seed 11 đúng format; benchmark đủ 4×14×5; crash 20/20; ADR/TEAM/research card máy đọc được; `0 FAIL, 1 WARN`. WARN chỉ vì tài liệu chưa commit.

#### Giai đoạn 8 — kết quả chạy lại trước commit tài liệu

- Smoke: `lab8.smoke pass`, Python 3.11.9 Windows AMD64.
- Host: `391 passed, 248 deselected in 35.94s`; student: `248 passed, 391 deselected in 16.99s`; crash: 20/20.
- Benchmark chạy lại: workflow/single/orchestrator 1.000 pass; swarm 0.985714, đúng một lỗi C-002 seed 55. JSON không có nội dung diff so commit evidence.
- Safety report vẫn complete=true/passed=true. Không có student_drop nên không tự khai hidden result.
- Log đầy đủ trong `src/.venv/stage8-*.log`, được gitignore. Bước còn lại: commit tài liệu, chạy check_submission lần cuối và dừng để người dùng tự push/LMS.
- Commit báo cáo: `0bfe186`. Check sau commit: ba shape 12/12 claim seed 11, benchmark 4×14×5, crash 20/20, ADR workflow, TEAM một thành viên, research card đủ; tổng `0 FAIL, 0 WARN`.
