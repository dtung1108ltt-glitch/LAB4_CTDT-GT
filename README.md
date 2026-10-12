# Lab 4 - Mini E-commerce Core (Giai đoạn 4)
Lõi hệ thống kho hàng với **Cây Nhị Phân Tìm Kiếm (Binary Search Tree - BST)** & **Cây Tự Cân Bằng (AVL Tree)**.  
Ngôn ngữ: **Python 3.8+** (Tiêu chuẩn kỹ nghệ phần mềm, thuần Python Standard Library, không cần thư viện ngoài).

Kế thừa liên tục từ chuỗi 3 bài Lab trước:
- **Lab 1 (Mảng tĩnh & Đo lường $O(n)$)**: `https://github.com/dtung1108ltt-glitch/Lab1_CTDL-GT.git`
- **Lab 2 (Danh sách liên kết đơn / Singly Linked List)**: `https://github.com/dtung1108ltt-glitch/LAB2_CTDT-GT.git`
- **Lab 3 (Ngăn xếp & Hàng đợi - Stack & Queue)**: `https://github.com/dtung1108ltt-glitch/LAB3_CTDLGT.git`

---

## 1. Cách chạy chương trình

```bash
# 1. Chạy chương trình đầy đủ: Chạy toàn bộ 4 bước thực nghiệm + Mở Menu tương tác
python lab4_ecommerce_tree.py
# (hoặc qua file wrapper):
python main.py

# 2. Chế độ chỉ chạy Demo & Benchmark tự động (không hỏi menu):
python lab4_ecommerce_tree.py --demo
# (hoặc):
python main.py --demo

# 3. Chạy toàn bộ bộ kiểm thử tự động (Unit Tests - 13 tests toàn diện):
python test_lab4.py
```

---

## 2. Cấu trúc mã nguồn trong Lab 4

| Tên File | Nguồn gốc | Vai trò & Nội dung |
|---|---|---|
| `lab4_ecommerce_tree.py` | **Mới (Lab 4 - Lõi chính)** | Toàn bộ hiện thực `Product`, `BSTNode`, `BinarySearchTree`, `AVLNode`, `AVLTree`, Benchmark đo lường và Menu tương tác trong 1 file độc lập duy nhất. |
| `main.py` | **Mới (Wrapper)** | Điểm khởi chạy chuẩn theo phong cách Lab 1-3. |
| `test_lab4.py` | **Mới (Lab 4)** | Bộ 13 Unit Tests kiểm thử tự động (Insert, Search, Delete 3 TH, Traversals, Clear Destructor, AVL 4 xoay, Chặn độ cao). |
| `BAO_CAO_LAB4.md` | **Mới (Lab 4)** | Bản báo cáo thực hành khoa học chi tiết chuẩn Markdown để nộp LMS. |
| `README.md` | **Mới (Lab 4)** | Tài liệu hướng dẫn, bảng đối chiếu Big-O và phân tích kiến trúc dự án. |

---

## 3. Các hàm & Cấu trúc KẾ THỪA từ Lab 1, 2, 3

| Thực thể / Giải thuật | Nguồn | Khái niệm & Cơ chế | Vai trò trong Lab 4 |
|---|---|---|---|
| `Product` | Lab 1 $\to$ 3 | ADT mô tả sản phẩm (ID, Name, Price, Category, Stock). | Dữ liệu cốt lõi lưu tại mỗi nút cây. |
| `generate_mock_products` | Lab 1 & 2 | Sinh ngẫu nhiên dữ liệu có kiểm soát bằng `seed=42`. | Sinh $100.000$ sản phẩm nạp vào cây BST. |
| `time.perf_counter()` | Lab 1 $\to$ 3 | Đồng hồ nano-giây đo lường hiệu năng thực nghiệm. | Đo đạc thời gian truy xuất và tính tỉ lệ tăng tốc (Speedup). |
| Con trỏ tham chiếu (References) | Lab 2 | Nối các nút dữ liệu trong bộ nhớ động. | Nâng cấp từ liên kết 1 chiều (`next`) lên 2 chiều (`left`, `right`). |
| `linear_search_by_id` | Lab 1 & 2 | Quét tuần tự $O(n)$ trên mảng / danh sách liên kết. | Làm mốc đối chứng (Baseline) đánh giá sự vượt trội của BST. |
| Hàng đợi (`Queue` / FIFO) | Lab 3 | Cơ chế hàng đợi vào trước ra trước. | Hiện thực duyệt cây theo từng tầng (`level_order_traversal` / BFS). |
| Call Stack & Đệ quy | Lab 3 | Ngăn xếp hệ thống lưu vết các hàm gọi lồng nhau. | Hiện thực các hàm duyệt cây, chèn, tìm kiếm, xóa nút. |

---

## 4. Các cấu trúc & Giải thuật MỚI ở Lab 4

| Hàm / Lớp | Thao tác / Thuật toán | Độ phức tạp lý thuyết | Ghi chú kỹ thuật |
|---|---|:---:|---|
| `BSTNode` | Nút cây nhị phân gồm `data`, `left`, `right` | $O(1)$ | Cấu trúc phân nhánh 2 chiều. |
| `BinarySearchTree.insert` | Chèn đệ quy theo quy tắc BST (khóa nhỏ sang trái, lớn sang phải) | $O(\log n)$ TB / $O(n)$ xấu | Loại bỏ trùng khóa `product_id`. |
| `BinarySearchTree.search` | Tìm kiếm đệ quy, loại bỏ 1/2 không gian tại mỗi bước | $O(\log n)$ TB / $O(n)$ xấu | Nhanh hơn tuần tự từ $700\times - 1.400\times$. |
| `BinarySearchTree.delete` | Xóa nút xử lý triệt để 3 trường hợp: Lá, 1 con, 2 con | $O(\log n)$ TB / $O(n)$ xấu | TH3 sử dụng In-order Successor (min cây con phải). |
| `inorder_traversal` | Duyệt Trung tự (Left $\to$ Node $\to$ Right) | $O(n)$ | Dữ liệu tự động tăng dần theo ID không cần sort. |
| `preorder_traversal` | Duyệt Tiền tự (Node $\to$ Left $\to$ Right) | $O(n)$ | Phục vụ Serialize / Nhân bản cây. |
| `postorder_traversal` | Duyệt Hậu tự (Left $\to$ Right $\to$ Node) | $O(n)$ | Phục vụ tính toán từ đáy lên đỉnh. |
| `level_order_traversal` | Duyệt theo tầng (BFS với Queue) | $O(n)$ | Kế thừa Queue FIFO từ Lab 3. |
| `clear()` / `destroy_tree()` | Post-order Destructor ngắt liên kết từ lá lên gốc | $O(n)$ | An toàn bộ nhớ, chống Memory Leak, hỗ trợ Python GC. |
| `AVLNode` | Nút AVL bổ sung thuộc tính `height` | $O(1)$ | Giám sát độ cao cục bộ. |
| `AVLTree.insert` | Chèn kết hợp tự cân bằng qua 4 phép xoay | $O(\log n)$ Luôn luôn | Giải quyết triệt để cây suy biến. |
| `_rotate_right` / `_rotate_left` | 2 phép xoay đơn (LL, RR) | $O(1)$ | Hoán đổi vài con trỏ và cập nhật chiều cao. |
| Xoay kép (LR, RL) | Kết hợp 2 lần xoay đơn | $O(1)$ | Tái lập cân bằng cho trường hợp gấp khúc. |

---

## 5. Kết quả Benchmark Thực nghiệm

### Thử nghiệm 1: Kho hàng $100.000$ sản phẩm ngẫu nhiên
- Chiều cao cây BST thực tế: $h = 43$.
- Thời gian nạp: $0.4745$ giây.

| Kịch bản | Linear Search $O(n)$ | BST Search $O(\log n)$ | Tỉ lệ tăng tốc (Speedup) |
|---|:---:|:---:|:---:|
| **Worst Case** (Không có ID) | $2.9216\text{ ms}$ | $0.002040\text{ ms}$ | **$1.432,1\times$ Nhanh hơn** |
| **Deep Existing Case** | $3.1599\text{ ms}$ | $0.004245\text{ ms}$ | **$744,4\times$ Nhanh hơn** |

### Thử nghiệm 2: Cây Suy Biến vs Cây AVL trên $10.000$ phần tử sắp xếp sẵn
| Tiêu chí | BST Tiêu Chuẩn (Suy biến) | Cây Tự Cân Bằng AVL | Hiệu quả tối ưu |
|---|:---:|:---:|---|
| **Chiều cao cây** | $h = 10.000$ (thành Linked List) | $h = 14$ ($\lceil \log_2 N \rceil$) | **Giảm chiều cao $714$ lần** |
| **Thời gian nạp** | $8.825,10\text{ ms}$ | $99,54\text{ ms}$ | AVL nạp nhanh hơn $88,6\times$ |
| **Tìm kiếm phần tử cuối** | $1.5043\text{ ms}$ ($O(n)$) | $0.000869\text{ ms}$ ($O(\log n)$) | **AVL nhanh hơn $1.731,1\times$** |

---

## 6. Quyết định thiết kế & Chuẩn Kỹ nghệ Phần mềm
1. **Thiết kế All-In-One nhưng tách bạch Module**: Mã nguồn chính được đặt trọn vẹn trong `lab4_ecommerce_tree.py` giúp nộp bài và chạy ở bất kỳ môi trường nào mà không sợ thiếu file phụ, đồng thời có `main.py` và `test_lab4.py` hỗ trợ quy trình CI/CD.
2. **Khắc phục giới hạn Call Stack**: Gọi `sys.setrecursionlimit(200000)` chủ động phòng tránh `RecursionError` trên các tập dữ liệu cực lớn.
3. **Mã hóa UTF-8 Console Windows**: Tự động reconfigure stdout/stderr sang UTF-8 tránh lỗi `charmap UnicodeEncodeError` trên môi trường terminal Windows tiếng Việt.
4. **Kiểm thử tự động 100%**: File `test_lab4.py` bao phủ tất cả các trường hợp biên, từ chối trùng ID, xóa đủ 3 trường hợp, và kiểm chứng toán học các phép xoay AVL.
