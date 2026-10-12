# BÁO CÁO THỰC HÀNH LAB 4
## MÔN HỌC: CẤU TRÚC DỮ LIỆU VÀ GIẢI THUẬT (DATA STRUCTURES & ALGORITHMS)
**Học phần:** Thực hành Cấu trúc dữ liệu và Giải thuật  
**Dự án xuyên suốt:** Lõi Hệ Thống Thương Mại Điện Tử Mini (Mini E-commerce Core)  
**Chủ đề Lab 4:** Cây Nhị Phân Tìm Kiếm (Binary Search Tree - BST) & Cây Tự Cân Bằng (AVL Tree)  
**Ngôn ngữ hiện thực:** Python 3 (Tiêu chuẩn Kỹ nghệ Phần mềm, không sử dụng thư viện ngoài)

---

## 1. TỔNG QUAN & BỐI CẢNH KẾ THỪA HỆ THỐNG

### 1.1 Chuỗi kế thừa dự án Mini E-commerce Core
Dự án được xây dựng và phát triển liên tục qua 4 giai đoạn thực hành:
- **Lab 1 (Mảng tĩnh & Đo lường $O(n)$)**: `https://github.com/dtung1108ltt-glitch/Lab1_CTDL-GT.git`  
  *Kế thừa*: Thực thể dữ liệu `Product` (`product_id`, `name`, `price`, `category`, `stock`), bộ tạo dữ liệu giả lập có kiểm soát giống thực tế (Mock Data Generator với seed cố định), cơ chế đo thời gian vi mô chính xác cao (`time.perf_counter()`).
- **Lab 2 (Danh sách liên kết đơn / Singly Linked List)**: `https://github.com/dtung1108ltt-glitch/LAB2_CTDT-GT.git`  
  *Kế thừa*: Khái niệm liên kết nút bằng con trỏ tham chiếu (`Node`, `next`). Nhận diện điểm nghẽn cổ chai (bottleneck) của việc tra cứu tuyến tính $O(n)$ trên cấu trúc 1 chiều khi số lượng sản phẩm kho hàng tăng cao.
- **Lab 3 (Ngăn xếp & Hàng đợi - Stack & Queue)**: `https://github.com/dtung1108ltt-glitch/LAB3_CTDLGT.git`  
  *Kế thừa*: Cơ chế Call Stack điều phối các hàm đệ quy và cấu trúc Hàng đợi (Queue FIFO) phục vụ giải thuật duyệt cây theo từng tầng (Level-order Traversal / BFS).

### 1.2 Bối cảnh bài toán và Nhu cầu nâng cấp ở Lab 4
Ở các giai đoạn trước, Kho hàng được lưu trữ bằng cấu trúc tuyến tính (Mảng hoặc Danh sách liên kết đơn). Khi quy mô hệ thống mở rộng lên hàng trăm ngàn đến hàng triệu sản phẩm ($N \ge 100.000$):
- Mọi truy vấn tra cứu thông tin sản phẩm theo mã `product_id` (được gửi từ Web, Mobile App, hoặc thiết bị IoT tại kho) đều phải quét tuần tự từng phần tử từ đầu đến cuối danh sách ($O(n)$).
- Trong trường hợp xấu nhất (sản phẩm không tồn tại hoặc nằm ở đáy danh sách), hệ thống phải thực hiện tới $100.000$ phép so sánh.
- Hệ quả: CPU bị chiếm dụng cao, thời gian đáp ứng (Latency) tăng vọt, các kết nối mạng bị Timeout.

**Giải pháp Lab 4**: Nâng cấp cấu trúc lưu trữ kho hàng sang **Cây nhị phân tìm kiếm (Binary Search Tree - BST)** và mở rộng nâng cao với **Cây tự cân bằng (AVL Tree)** để đưa độ phức tạp tìm kiếm từ $O(n)$ xuống $O(\log n)$.

---

## 2. HIỆN THỰC KỸ THUẬT & PHÂN TÍCH THUẬT TOÁN

### 2.1 Cấu trúc Cây Nhị phân Tìm kiếm (BST)
Mỗi nút trên cây (`BSTNode`) lưu trữ một đối tượng `Product` và hai liên kết con trỏ `left` và `right`.

```
                  [Root Node: ID=50]
                     /          \
        (ID < 50)   /            \   (ID > 50)
            [Node: ID=30]     [Node: ID=70]
               /     \           /     \
             [20]    [40]      [60]    [80]
```

- **Quy tắc bất biến BST (Invariant)**:
  $$\forall u \in \text{LeftSubtree}(root): u.\text{product\_id} < root.\text{product\_id}$$
  $$\forall v \in \text{RightSubtree}(root): v.\text{product\_id} > root.\text{product\_id}$$
  Mỗi `product_id` là khóa duy nhất (Primary Key), các ID trùng lặp bị từ chối chèn để đảm bảo tính toàn vẹn dữ liệu.

- **Thao tác Chèn (`insert(product)`) - Độ phức tạp $O(h)$**:
  Vận dụng đệ quy so sánh khóa để rẽ nhánh trái hoặc phải cho đến khi gặp vị trí lá trống thì tạo `BSTNode` mới.
- **Thao tác Tìm kiếm (`search(target_id)`) - Độ phức tạp $O(h)$**:
  Tại mỗi nút, so sánh `target_id` với khóa hiện tại. Do tính chất phân nhánh, sau mỗi bước so sánh, thuật toán loại bỏ hoàn toàn một nửa không gian tìm kiếm còn lại (tương tự Tìm kiếm nhị phân).

### 2.2 Thuật toán Xóa nút (`delete(target_id)`) - Xử lý triệt để 3 trường hợp
Xóa một nút trên BST đòi hỏi phải bảo toàn tính chất thứ tự của cây. Thuật toán xử lý trọn vẹn 3 trường hợp:
1. **Trường hợp 1 (Nút lá - Leaf Node)**: Nút không có con nào (`left is None and right is None`). Ta ngắt kết nối trực tiếp bằng cách trả về `None` cho nút cha.
2. **Trường hợp 2 (Nút có đúng 1 cây con - Single Child)**: Nút chỉ có con trái hoặc con phải. Ta bắc cầu nối con duy nhất của nút bị xóa trực tiếp lên nút cha (`return current.left` hoặc `return current.right`).
3. **Trường hợp 3 (Nút có đủ 2 cây con - Two Children)**:
   - Tìm **In-order Successor** (Nút có khóa nhỏ nhất bên cây con phải - nút nằm tận cùng bên trái của cây con phải).
   - Sao chép toàn bộ dữ liệu của nút thế mạng vào vị trí của nút cần xóa.
   - Đệ quy xóa nút thế mạng khỏi cây con phải (lúc này nút thế mạng chắc chắn chỉ rơi vào Trường hợp 1 hoặc 2 vì nó không thể có con trái).

### 2.3 Phép duyệt cây & Cơ chế Giải phóng bộ nhớ (Post-order Destructor)
- **In-order Traversal (LNR - Duyệt Trung tự)**: Duyệt Cây con Trái $\to$ Nút hiện tại $\to$ Cây con Phải.  
  *Ý nghĩa*: Trích xuất dữ liệu danh mục kho hàng **tự động sắp xếp tăng dần theo ID** mà không cần tốn chi phí cho thuật toán sắp xếp bên ngoài ($O(n)$).
- **Pre-order Traversal (NLR - Duyệt Tiền tự)**: Nút $\to$ Trái $\to$ Phải. Phục vụ việc tuần tự hóa (Serialization) và sao chép cây.
- **Post-order Traversal (LRN - Duyệt Hậu tự)**: Trái $\to$ Phải $\to$ Nút.
- **Level-order Traversal (BFS)**: Duyệt theo tầng sử dụng cấu trúc Hàng đợi (Queue FIFO kế thừa từ Lab 3).
- **Cơ chế Destructor chống Memory Leak (`clear()` / `destroy_tree()`)**:
  Giải phóng cây từ dưới lên trên theo nguyên lý duyệt Hậu tự: Giải phóng triệt để 2 nhánh con trước khi ngắt nút cha (`node.left = None; node.right = None`). Điều này phá vỡ toàn bộ chuỗi liên kết tham chiếu hai chiều, hỗ trợ bộ thu gom rác (Garbage Collector) của Python thu hồi RAM an toàn và ngăn chặn hiện tượng rò rỉ bộ nhớ.

---

## 3. HIỆN TƯỢNG SUY BIẾN CÂY VÀ GIẢI PHÁP CÂY TỰ CÂN BẰNG AVL

### 3.1 Bản chất hiện tượng Cây suy biến (Degenerate / Skewed Tree)
Khi các sản phẩm được nhập vào kho theo thứ tự mã số tăng dần (ví dụ: $1, 2, 3, 4, \dots, N$):
- Tại mỗi nút, phần tử mới luôn lớn hơn nút hiện tại, dẫn đến việc luôn luôn rẽ nhánh PHẢI.
- Cây bị lệch hoàn toàn sang phải, cấu trúc phân nhánh 2 chiều suy biến thành một **Danh sách liên kết đơn** (Singly Linked List).
- Chiều cao cây đạt cực đại: $h = N$.
- Độ phức tạp tìm kiếm suy thoái từ $O(\log n)$ trở lại $O(n)$, làm mất hoàn toàn ưu thế vượt trội của BST.

```
       [1]
         \
         [2]
           \
           [3]    ==> Chiều cao h = N (Suy biến thành Linked List, tìm kiếm O(n))
             \
             ...
               \
               [N]
```

### 3.2 Giải pháp Cây AVL (Adelson-Velsky and Landis Tree)
Cây AVL bổ sung cơ chế tự cân bằng nghiêm ngặt:
- Mỗi nút lưu trữ thuộc tính `height`.
- **Hệ số cân bằng (Balance Factor)**:
  $$\text{Balance Factor}(u) = \text{Height}(u.\text{left}) - \text{Height}(u.\text{right}) \in \{-1, 0, 1\}$$
- Ngay khi một nút bị vi phạm cân bằng ($|\text{Balance Factor}| > 1$), cây lập tức kích hoạt 1 trong 4 phép xoay cục bộ với độ phức tạp $O(1)$:

#### 4 Phép xoay cân bằng trong AVL:
1. **Xoay Đơn Phải (Right Rotation - LL)**: Áp dụng khi cây lệch Trái - Trái.
```
       y                               x
      / \                             / \
     x   T3   -- right_rotate(y) --> T1   y
    / \                                  / \
   T1  T2                               T2  T3
```
2. **Xoay Đơn Trái (Left Rotation - RR)**: Áp dụng khi cây lệch Phải - Phải.
```
     x                                   y
    / \                                 / \
   T1  y      -- left_rotate(x) -->    x   T3
      / \                             / \
     T2  T3                          T1  T2
```
3. **Xoay Kép Trái - Phải (Left-Right Rotation - LR)**: Xoay Trái tại con trái, sau đó Xoay Phải tại nút hiện tại.
4. **Xoay Kép Phải - Trái (Right-Left Rotation - RL)**: Xoay Phải tại con phải, sau đó Xoay Trái tại nút hiện tại.

*Hệ quả*: Chiều cao cây AVL luôn được chặn trên bởi $h \le 1.44 \log_2(N + 2) \approx \lceil \log_2 N \rceil$. Mọi thao tác tìm kiếm, chèn, xóa luôn được bảo đảm ở mức $O(\log n)$ ngay cả khi dữ liệu đầu vào đã sắp xếp sẵn.

---

## 4. KẾT QUẢ THỰC NGHIỆM & ĐỐI CHIẾU HIỆU NĂNG (BENCHMARK)

Môi trường kiểm thử: Python 3.14 trên Windows 11, bộ đo thời gian vi mô `time.perf_counter()`.

### 4.1 Thí nghiệm 1: Kho hàng $100.000$ sản phẩm ngẫu nhiên (Linear Search vs BST Search)
- Số lượng nút nạp vào kho: $N = 100.000$ sản phẩm.
- Chiều cao cây BST tự nhiên: $h = 43$ (gần sát cận lý thuyết $\log_2(100.000) \approx 17$).
- Thời gian nạp toàn bộ $100.000$ nút: $0.4745$ giây ($0.0047$ ms/sản phẩm).

| Kịch bản thử nghiệm | Linear Search $O(n)$ (Lab 1 & 2) | BST Search $O(\log n)$ (Lab 4) | Tỉ lệ tăng tốc (Speedup) |
|---|:---:|:---:|:---:|
| **Worst Case** (Tìm ID không tồn tại: `999_999_999`) | $2.9216\text{ ms}$ | $0.002040\text{ ms}$ | **$1.432,1\times$ Nhanh hơn** |
| **Deep Existing Case** (Tìm ID nằm sâu trong kho: `21612`) | $3.1599\text{ ms}$ | $0.004245\text{ ms}$ | **$744,4\times$ Nhanh hơn** |

> **Nhận xét**: 
> - Ở Worst Case, Linear Search buộc phải duyệt qua toàn bộ $100.000$ sản phẩm mới có thể kết luận sản phẩm không tồn tại, mất gần $3\text{ ms}$.
> - Trong khi đó, Cây BST chỉ cần duyệt qua tối đa $43$ phép so sánh rẽ nhánh từ gốc đến lá, hoàn tất tìm kiếm trong $0.002\text{ ms}$.
> - BST mang lại tốc độ vượt trội gấp hơn **$1.400$ lần**, giải quyết triệt để vấn đề quá tải CPU.

---

### 4.2 Thí nghiệm 2: Hiện tượng Suy biến trên Dữ liệu đã Sắp xếp ($N = 10.000$)
Nạp $10.000$ sản phẩm có ID tăng dần $1, 2, 3, \dots, 10.000$ vào BST tiêu chuẩn và Cây AVL.

| Tiêu chí / Chỉ số kỹ thuật | Cây BST Tiêu Chuẩn (Bị suy biến) | Cây Tự Cân Bằng AVL | Đánh giá & So sánh |
|---|:---:|:---:|---|
| **Dữ liệu đầu vào** | Đã sắp xếp tăng dần $1..N$ | Đã sắp xếp tăng dần $1..N$ | Dữ liệu kiểm thử giống nhau |
| **Số lượng phần tử ($N$)** | $10.000$ | $10.000$ | |
| **Thời gian nạp dữ liệu** | $8.825,10\text{ ms}$ | $99,54\text{ ms}$ | Cây AVL nạp nhanh hơn **$88,6\times$** |
| **Chiều cao cây thực tế ($h$)** | **$h = 10.000$** | **$h = 14$** | Cây AVL giảm chiều cao **$714$ lần**! |
| **Độ phức tạp tìm kiếm** | $O(n)$ (suy thoái) | $O(\log n)$ (tối ưu) | $\lceil \log_2(10.000) \rceil = 14$ |
| **Thời gian tìm kiếm phần tử cuối ($N=10.000$)** | $1.5043\text{ ms}$ | $0.000869\text{ ms}$ | Cây AVL nhanh hơn **$1.731,1$ lần** |

> **Nhận xét cốt lõi**:
> 1. Trên BST thông thường, việc nạp dữ liệu có thứ tự đẩy chiều cao cây lên $10.000$, biến cây thành danh sách liên kết, thao tác tìm kiếm phải duyệt qua $10.000$ nút gây chậm trễ.
> 2. Cây AVL liên tục thực hiện các phép xoay đơn (RR) trong quá trình chèn, giữ cho cây cân bằng hoàn hảo với chiều cao chỉ bằng $14$. Nhờ đó, thao tác tìm kiếm chỉ tốn $0.000869\text{ ms}$, nhanh gấp **$1.731$ lần** so với cây suy biến!

---

## 5. BẢNG SO SÁNH TỔNG HỢP BIG-O XUYÊN SUỐT 4 BÀI LAB

| Cấu trúc dữ liệu | Đại diện Lab | Tìm kiếm (Search) | Chèn (Insert) | Xóa (Delete) | Duyệt (Traverse) | Nguy cơ suy biến / Điểm nghẽn |
|---|:---:|:---:|:---:|:---:|:---:|---|
| **Mảng tĩnh (Static Array)** | Lab 1 | $O(n)$ | $O(n)$ (chèn giữa) | $O(n)$ (dồn mảng) | $O(n)$ | Kích thước cố định, tràn bộ nhớ |
| **DS Liên kết (Linked List)** | Lab 2 | $O(n)$ | $O(1)$ (đầu/cuối) | $O(n)$ (tìm rồi xóa) | $O(n)$ | Tìm kiếm tuần tự chậm khi $N$ lớn |
| **Ngăn xếp / Hàng đợi (Stack/Queue)**| Lab 3 | $O(n)$ | $O(1)$ (Push/Enqueue)| $O(1)$ (Pop/Dequeue) | $O(n)$ | Bị giới hạn truy cập chỉ ở 2 đầu |
| **Cây BST (Trường hợp tốt/trung bình)**| Lab 4 | **$O(\log n)$** | **$O(\log n)$** | **$O(\log n)$** | $O(n)$ | Cần dữ liệu phân bố ngẫu nhiên |
| **Cây BST (Trường hợp suy biến)** | Lab 4 | $O(n)$ | $O(n)$ | $O(n)$ | $O(n)$ | Xảy ra khi dữ liệu đã sắp xếp sẵn |
| **Cây Tự Cân Bằng AVL** | Lab 4 (Nâng cao)| **$O(\log n)$** | **$O(\log n)$** | **$O(\log n)$** | $O(n)$ | Chi phí xoay cây nhỏ ($O(1)$), hiệu năng luôn đảm bảo |

---

## 6. KẾT LUẬN & BÀI HỌC KỸ NGHỆ PHẦN MỀM

1. **Hiệu quả của Cấu trúc Dữ liệu Phi Tuyến Tính**: Việc chuyển đổi lưu trữ kho hàng từ cấu trúc tuyến tính ($O(n)$) sang cấu trúc Cây nhị phân ($O(\log n)$) đem lại bước nhảy vọt về hiệu năng (tăng tốc từ $700\times$ đến $1.400\times$ khi $N=100.000$), giải quyết triệt để bài toán thắt nút cổ chai truy vấn.
2. **Giá trị thực tiễn của Thuật toán Tự Cân Bằng**: Trong các hệ thống sản xuất thực tế, dữ liệu nạp vào thường có xu hướng tăng dần theo thời gian (ví dụ: auto-increment ID, timestamp). Cây BST thuần túy rất dễ biến thành cây suy biến. Cây AVL là giải pháp triệt để giúp duy trì tính ổn định của hệ thống với thời gian truy xuất luôn được đảm bảo ở mức logarit.
3. **Kỹ thuật Đệ quy & An toàn Bộ nhớ**:
   - Tăng `sys.setrecursionlimit()` là giải pháp kỹ thuật cần thiết khi làm việc với cây sâu trong Python.
   - Cơ chế giải phóng theo cơ chế Hậu tự (Post-order Destructor) là minh chứng cho tư duy kỹ nghệ phần mềm an toàn, chủ động dọn dẹp liên kết tham chiếu và hỗ trợ Garbage Collector tối ưu tài nguyên hệ thống.
