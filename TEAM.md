# Team

## Thông tin nhóm

- Tên nhóm: `1THANHVIEN`
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-1THANHVIEN-FromWorkflowsToAgents`
- URL repo, nhánh nộp, commit chốt: `https://github.com/damlinh820/K5-L3A-DAY08-1THANHVIEN-FromWorkflowsToAgents`, `main`, `a551fd1`

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Đàm Tuấn Linh | 2A202603624 | 26ai.linhdt3@vinuni.edu.vn | damlinh820 | Implementation, safety, evaluation, report |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Đàm Tuấn Linh | Implementation, safety, evaluation, report | `b892e6b`, `b3eb64c`, `0e3287d`, `9523182`, `bb042dc`, `a551fd1` | `tests/test_shape_safety.py`; `tests/test_workflow_ablation.py` |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603624_DamTuanLinh

### Phần việc phụ trách

- Workflow, single ReAct, orchestrator/handoff; durability, approval, trace; benchmark, R4 ablation và báo cáo.

### Đóng góp cụ thể

- Triển khai ba shape; thêm 264 test safety và 73 test ablation; tạo benchmark/crash/safety reports bằng CLI.

### Bằng chứng

- Các commit và test trong bảng đóng góp; run ID `R-workflow-C-014-s11`; benchmark 280 trial và crash 20/20.
