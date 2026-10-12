"""
lab4_ecommerce_tree.py
===============================================================================
BÀI THỰC HÀNH LAB 4 - LÕI HỆ THỐNG THƯƠNG MẠI ĐIỆN TỬ MINI (MINI E-COMMERCE CORE)
CHỦ ĐỀ: CÂY NHỊ PHÂN TÌM KIẾM (BST) & CÂY TỰ CÂN BẰNG (AVL TREE)
===============================================================================
Kế thừa kiến trúc từ chuỗi 3 bài Lab trước:
  - Lab 1: Thực thể Product (ID, Name, Price), Mock Data Generator, Benchmark O(n).
  - Lab 2: Liên kết nút (References), giải quyết vấn đề nút thắt cổ chai tìm kiếm
           tuyến tính O(n) trên Mảng / Danh sách liên kết khi dữ liệu đạt quy mô lớn.
  - Lab 3: Ngăn xếp (Call Stack) cho đệ quy, Hàng đợi (Queue) cho duyệt cây theo tầng (BFS).

Quy chuẩn kỹ nghệ phần mềm:
  - Toàn bộ hiện thực trong 1 file duy nhất, chỉ sử dụng Python Standard Library.
  - Đầy đủ docstring, type hints, chú thích thuật toán Big-O chi tiết tại mọi điểm chốt.
  - Tăng giới hạn đệ quy hệ thống: sys.setrecursionlimit(200000).
===============================================================================
"""

from __future__ import annotations

import sys
import time
import random
from collections import deque
from dataclasses import dataclass
from typing import Optional, List, Tuple, Callable

# =============================================================================
# CẤU HÌNH HỆ THỐNG: TĂNG GIỚI HẠN CALL STACK ĐỆ QUY
# =============================================================================
# Mặc định Python chỉ cho phép đệ quy sâu 1000 mức. Để xử lý cây dữ liệu quy mô
# lớn (100.000 sản phẩm) và kiểm chứng cây suy biến (chiều sâu lên tới 10.000),
# ta tăng recursion limit lên 200.000 nhằm tránh RecursionError.
sys.setrecursionlimit(200000)

# Cấu hình mã hóa UTF-8 cho console Windows để in tiếng Việt chuẩn không bị lỗi charmap
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass



# =============================================================================
# BƯỚC 1: LỚP THỰC THỂ DỮ LIỆU PRODUCT (KẾ THỪA TỪ LAB 1, 2, 3)
# =============================================================================
@dataclass
class Product:
    """
    Thực thể Sản phẩm (Product Entity) trong kho E-commerce.
    
    Thuộc tính:
        product_id (int): Khóa định danh duy nhất (Unique Key dùng cho BST/AVL).
        name (str): Tên thương mại của sản phẩm.
        price (float): Giá bán niêm yết (VND).
        category (str): Ngành hàng / Danh mục sản phẩm.
        stock (int): Số lượng tồn kho (kế thừa từ Lab 1-3).
    """
    product_id: int
    name: str
    price: float
    category: str
    stock: int = 100

    @property
    def id(self) -> int:
        """Thuộc tính tương thích ngược với mã nguồn Lab 1 & Lab 2."""
        return self.product_id

    def __str__(self) -> str:
        """
        Biểu diễn chuỗi trực quan dạng 'Chip / Card' thông tin sản phẩm.
        Độ phức tạp: O(1).
        """
        return (f"[ID: {self.product_id:06d}] "
                f"{self.name:<24} | "
                f"Giá: {self.price:>12,.0f} VND | "
                f"Ngành: {self.category:<12} | "
                f"Tồn kho: {self.stock:>4}")


# =============================================================================
# BƯỚC 1: LỚP NÚT CÂY NHỊ PHÂN TÌM KIẾM (BST NODE)
# =============================================================================
class BSTNode:
    """
    Nút trong Cây Nhị phân Tìm kiếm (Binary Search Tree Node).
    
    Mỗi nút lưu trữ một thực thể Product và hai con trỏ tham chiếu
    tới cây con trái (left) và cây con phải (right).
    Kế thừa triết lý liên kết nút từ Singly Linked List (Lab 2), nâng cấp
    từ liên kết 1 chiều sang phân nhánh 2 chiều.
    """
    def __init__(self, product: Product) -> None:
        self.data: Product = product
        self.left: Optional[BSTNode] = None   # Tham chiếu cây con trái: chứa các ID < data.product_id
        self.right: Optional[BSTNode] = None  # Tham chiếu cây con phải: chứa các ID > data.product_id

    def __repr__(self) -> str:
        return f"BSTNode(ID={self.data.product_id}, Name='{self.data.name}')"


# =============================================================================
# BƯỚC 1: CÂY NHỊ PHÂN TÌM KIẾM (BINARY SEARCH TREE - BST)
# =============================================================================
class BinarySearchTree:
    """
    Cấu trúc dữ liệu Cây Nhị phân Tìm kiếm (BST) lưu trữ Kho hàng E-commerce.
    
    Quy tắc cấu trúc (BST Invariant):
      - Mọi nút trên cây con TRÁI có `product_id` < `root.product_id`.
      - Mọi nút trên cây con PHẢI có `product_id` > `root.product_id`.
      - Cây con trái và cây con phải đều là các Cây Nhị phân Tìm kiếm.
      - Không chứa hai sản phẩm trùng `product_id` (Unique Identifier).

    Hiệu năng lý thuyết:
      - Cân bằng / Ngẫu nhiên: Độ cao h ≈ log2(n) => Tìm kiếm, Chèn, Xóa: O(log n).
      - Suy biến (Worst case): Độ cao h = n      => Tìm kiếm, Chèn, Xóa: O(n).
    """

    def __init__(self) -> None:
        """Khởi tạo cây BST rỗng."""
        self.root: Optional[BSTNode] = None
        self._size: int = 0

    # -------------------------------------------------------------------------
    # 1. THAO TÁC CHÈN (INSERT)
    # -------------------------------------------------------------------------
    def insert(self, product: Product) -> bool:
        """
        Thêm một sản phẩm mới vào cây BST theo quy tắc khóa `product_id`.
        
        Cơ chế: Vận dụng đệ quy để duyệt từ gốc xuống nút lá thích hợp.
          - ID nhỏ hơn: rẽ trái.
          - ID lớn hơn: rẽ phải.
          - ID trùng lặp: từ chối chèn (bảo vệ tính toàn vẹn của khóa định danh).
          
        Độ phức tạp thời gian:
          - Trung bình (Average): O(log n) khi cây phát triển cân đối.
          - Xấu nhất (Worst): O(n) khi cây bị suy biến thành danh sách liên kết.
        Độ phức tạp không gian:
          - O(h) trên Call Stack do đệ quy (h là chiều cao của cây).
          
        Returns:
            bool: True nếu chèn thành công, False nếu ID đã tồn tại.
        """
        inserted: bool = False

        def _insert_recursive(current: Optional[BSTNode]) -> BSTNode:
            nonlocal inserted
            # Neo đệ quy: Tìm thấy vị trí lá trống -> Tạo nút mới
            if current is None:
                inserted = True
                return BSTNode(product)

            # Rẽ trái nếu ID nhỏ hơn khóa hiện tại
            if product.product_id < current.data.product_id:
                current.left = _insert_recursive(current.left)
            # Rẽ phải nếu ID lớn hơn khóa hiện tại
            elif product.product_id > current.data.product_id:
                current.right = _insert_recursive(current.right)
            else:
                # Trùng khóa ID: từ chối thêm mới
                inserted = False

            return current

        self.root = _insert_recursive(self.root)
        if inserted:
            self._size += 1
        return inserted

    # -------------------------------------------------------------------------
    # 2. THAO TÁC TÌM KIẾM (SEARCH)
    # -------------------------------------------------------------------------
    def search(self, target_id: int) -> Optional[Product]:
        """
        Tìm kiếm thông tin sản phẩm theo `product_id` bằng giải thuật đệ quy.
        
        Cơ chế:
          Tại mỗi nút so sánh `target_id` với `current.data.product_id`:
          - Bằng nhau: Tìm thấy đích -> Trả về thực thể Product.
          - target_id < current: Loại bỏ toàn bộ cây con phải, chỉ đệ quy sang trái.
          - target_id > current: Loại bỏ toàn bộ cây con trái, chỉ đệ quy sang phải.
          => Loại bỏ 1/2 không gian tìm kiếm sau mỗi bước rẽ (tương tự Binary Search).
          
        Độ phức tạp thời gian:
          - Best Case: O(1) - Nằm ngay tại nút gốc.
          - Average Case: O(log n) - Chiều cao cây cân đối h ≈ 1.44 log2(n).
          - Worst Case: O(n) - Cây suy biến hoàn toàn lệch 1 bên.
          
        Returns:
            Optional[Product]: Đối tượng Product nếu tìm thấy, None nếu không tồn tại.
        """
        def _search_recursive(current: Optional[BSTNode]) -> Optional[Product]:
            # Neo đệ quy 1: Cây rỗng hoặc đã duyệt qua nút lá mà không thấy
            if current is None:
                return None
            
            # Neo đệ quy 2: Khóa trùng khớp
            if target_id == current.data.product_id:
                return current.data
            
            # Bước đệ quy: Rẽ nhánh
            if target_id < current.data.product_id:
                return _search_recursive(current.left)   # Rẽ trái
            else:
                return _search_recursive(current.right)  # Rẽ phải

        return _search_recursive(self.root)

    # -------------------------------------------------------------------------
    # 3. THAO TÁC XÓA (DELETE) - XỬ LÝ TRIỆT ĐỂ 3 TRƯỜNG HỢP
    # -------------------------------------------------------------------------
    def delete(self, target_id: int) -> bool:
        """
        Xóa sản phẩm có mã `target_id` khỏi cây BST, duy trì cấu trúc BST hợp lệ.
        
        Xử lý triệt để 3 trường hợp kinh điển:
          - Trường hợp 1: Nút cần xóa là Nút lá (Leaf Node)
              -> Trả về None cho nút cha ngắt kết nối trực tiếp.
          - Trường hợp 2: Nút cần xóa có đúng 1 cây con (Single Child)
              -> Nối trực tiếp cây con duy nhất (trái hoặc phải) lên nút cha.
          - Trường hợp 3: Nút cần xóa có đủ 2 cây con (Two Children)
              -> Tìm nút thế mạng: In-order Successor (nút có khóa nhỏ nhất bên
                 cây con phải).
              -> Sao chép dữ liệu của In-order Successor đè lên nút hiện tại.
              -> Đệ quy xóa In-order Successor khỏi cây con phải (vốn chỉ rơi
                 vào trường hợp 1 hoặc 2).
                 
        Độ phức tạp thời gian:
          - Trung bình: O(log n).
          - Xấu nhất: O(n).
        Độ phức tạp không gian:
          - O(h) trên Call Stack.
          
        Returns:
            bool: True nếu tìm thấy và xóa thành công, False nếu ID không tồn tại.
        """
        deleted: bool = False

        def _find_min(node: BSTNode) -> BSTNode:
            """Tìm nút có khóa nhỏ nhất trong cây con (nút nằm tận cùng bên trái)."""
            current = node
            while current.left is not None:
                current = current.left
            return current

        def _delete_recursive(current: Optional[BSTNode], key: int) -> Optional[BSTNode]:
            nonlocal deleted
            if current is None:
                return None  # Không tìm thấy nút có ID cần xóa

            if key < current.data.product_id:
                current.left = _delete_recursive(current.left, key)
            elif key > current.data.product_id:
                current.right = _delete_recursive(current.right, key)
            else:
                # ĐÃ TÌM THẤY NÚT CẦN XÓA!
                deleted = True

                # TRƯỜNG HỢP 1 & 2: Có 0 con (lá) hoặc có 1 con
                if current.left is None:
                    # Nếu không có con trái: trả về con phải (dù con phải là None hay có nút)
                    return current.right
                elif current.right is None:
                    # Nếu không có con phải: trả về con trái
                    return current.left

                # TRƯỜNG HỢP 3: Có đầy đủ 2 con
                # Bước 3.1: Tìm In-order Successor (nút nhỏ nhất của cây con phải)
                successor = _find_min(current.right)
                # Bước 3.2: Sao chép dữ liệu của nút thế mạng vào nút hiện tại
                current.data = successor.data
                # Bước 3.3: Xóa nút thế mạng khỏi cây con phải
                current.right = _delete_recursive(current.right, successor.data.product_id)

            return current

        self.root = _delete_recursive(self.root, target_id)
        if deleted:
            self._size -= 1
        return deleted

    # -------------------------------------------------------------------------
    # 4. CÁC PHÉP DUYỆT CÂY (TRAVERSALS)
    # -------------------------------------------------------------------------
    def inorder_traversal(self, limit: Optional[int] = None) -> List[Product]:
        """
        Duyệt Trung tự (In-order Traversal: Left -> Node -> Right).
        
        Ý nghĩa lý thuyết:
          Tính chất toán học cốt lõi của BST chứng minh rằng phép duyệt LNR
          luôn trích xuất các phần tử theo thứ tự TĂNG DẦN TUYỆT ĐỐI của khóa
          ID mà không cần chạy thêm bất kỳ thuật toán sắp xếp (Sorting) nào!
          
        Độ phức tạp thời gian: O(n) do ghé thăm mỗi nút đúng một lần.
        Độ phức tạp không gian: O(h) trên Call Stack.
        """
        result: List[Product] = []

        def _inorder(node: Optional[BSTNode]) -> None:
            if node is None:
                return
            if limit is not None and len(result) >= limit:
                return

            _inorder(node.left)

            if limit is None or len(result) < limit:
                result.append(node.data)

            if limit is None or len(result) < limit:
                _inorder(node.right)

        _inorder(self.root)
        return result

    def preorder_traversal(self, limit: Optional[int] = None) -> List[Product]:
        """
        Duyệt Tiền tự (Pre-order Traversal: Node -> Left -> Right).
        
        Ý nghĩa ứng dụng:
          Dùng để Serialize / Lưu vết cấu trúc cây xuống đĩa hoặc truyền qua
          mạng. Khi đọc lại dữ liệu theo thứ tự Pre-order và chèn lại vào BST,
          cấu trúc phân nhánh ban đầu của cây được tái tạo chính xác.
          
        Độ phức tạp: O(n).
        """
        result: List[Product] = []

        def _preorder(node: Optional[BSTNode]) -> None:
            if node is None:
                return
            if limit is not None and len(result) >= limit:
                return

            result.append(node.data)
            _preorder(node.left)
            _preorder(node.right)

        _preorder(self.root)
        return result

    def postorder_traversal(self, limit: Optional[int] = None) -> List[Product]:
        """
        Duyệt Hậu tự (Post-order Traversal: Left -> Right -> Node).
        
        Ý nghĩa ứng dụng:
          Xử lý từ đáy lên đỉnh. Rất quan trọng trong việc tính kích thước thư mục,
          đánh giá biểu thức toán học (Syntax Tree) và HỦY BỘ NHỚ CÂY (Destructor).
          
        Độ phức tạp: O(n).
        """
        result: List[Product] = []

        def _postorder(node: Optional[BSTNode]) -> None:
            if node is None:
                return
            if limit is not None and len(result) >= limit:
                return

            _postorder(node.left)
            _postorder(node.right)
            if limit is None or len(result) < limit:
                result.append(node.data)

        _postorder(self.root)
        return result

    def level_order_traversal(self, limit: Optional[int] = None) -> List[Product]:
        """
        Duyệt theo tầng (Level-order Traversal / Breadth-First Search - BFS).
        
        KẾ THỪA TỪ LAB 3:
          Sử dụng cấu trúc Hàng đợi (Queue - FIFO) đã nghiên cứu ở Lab 3
          để duyệt cây từ gốc xuống theo từng độ sâu tầng 0, 1, 2...
          
        Độ phức tạp thời gian: O(n).
        Độ phức tạp không gian: O(w) với w là độ rộng lớn nhất của cây.
        """
        if self.root is None:
            return []

        result: List[Product] = []
        queue: deque[BSTNode] = deque([self.root])  # Queue FIFO (kế thừa Lab 3)

        while queue and (limit is None or len(result) < limit):
            current = queue.popleft()
            result.append(current.data)

            if current.left is not None:
                queue.append(current.left)
            if current.right is not None:
                queue.append(current.right)

        return result

    # -------------------------------------------------------------------------
    # 5. GIẢI PHÓNG BỘ NHỚ AN TOÀN (POST-ORDER DESTRUCTOR / CLEAR)
    # -------------------------------------------------------------------------
    def clear(self) -> int:
        """
        Hủy toàn bộ cây theo cơ chế Duyệt Hậu tự (Post-order Destructor).
        
        Nguyên lý:
          Duyệt đệ quy tới các nút lá sâu nhất trước, ngắt đứt con trỏ `left`
          và `right` (gán None), sau đó mới ngắt nút cha. Quá trình ngắt liên kết
          từ lá lên gốc giúp bộ thu gom rác (Garbage Collector của Python)
          thu hồi bộ nhớ tức thì, ngăn chặn hiện tượng rò rỉ bộ nhớ (Memory Leak)
          và gỡ bỏ các liên kết tham chiếu chéo (Cyclic References).
          
        Độ phức tạp thời gian: O(n) - duyệt qua từng nút.
        Độ phức tạp không gian: O(h) trên Call Stack.
        
        Returns:
            int: Số lượng nút đã được giải phóng.
        """
        count = 0

        def _destroy_postorder(node: Optional[BSTNode]) -> None:
            nonlocal count
            if node is None:
                return

            # Đi xuống giải phóng 2 cây con trước (Left -> Right)
            _destroy_postorder(node.left)
            _destroy_postorder(node.right)

            # Xử lý nút hiện tại (Node): Ngắt liên kết con trỏ
            node.left = None
            node.right = None
            node.data = None  # type: ignore
            count += 1

        _destroy_postorder(self.root)
        self.root = None
        self._size = 0
        return count

    def destroy_tree(self) -> int:
        """Bí danh cho phương thức clear() theo đề bài."""
        return self.clear()

    # -------------------------------------------------------------------------
    # 6. CÁC TIỆN ÍCH TRUY VẤN CẤU TRÚC
    # -------------------------------------------------------------------------
    def height(self) -> int:
        """
        Tính chiều cao (Height/Depth) của cây BST.
        Định nghĩa: Chiều cao cây rỗng là 0, cây có 1 nút gốc là 1.
        Độ phức tạp: O(n).
        """
        def _get_height(node: Optional[BSTNode]) -> int:
            if node is None:
                return 0
            return 1 + max(_get_height(node.left), _get_height(node.right))

        return _get_height(self.root)

    def size(self) -> int:
        """Trả về số lượng sản phẩm đang có trong cây. Độ phức tạp: O(1)."""
        return self._size

    def is_empty(self) -> bool:
        """Kiểm tra cây có rỗng hay không. Độ phức tạp: O(1)."""
        return self.root is None


# =============================================================================
# BƯỚC 2: TẠO DỮ LIỆU KHO HÀNG GIẢ LẬP (MOCK DATA GENERATOR)
# =============================================================================
CATEGORIES = [
    "Dien thoai", "Laptop", "Phu kien", "Thoi trang",
    "Gia dung", "Thiet bi am thanh", "Dong ho", "The thao"
]

SAMPLE_NAMES = {
    "Dien thoai": ["iPhone 15 Pro", "Samsung S24 Ultra", "Xiaomi 14 Pro", "Oppo Find X7"],
    "Laptop": ["MacBook Pro M3", "Dell XPS 15", "ThinkPad X1 Carbon", "Asus ROG Zephyrus"],
    "Phu kien": ["Cap sac Type-C", "Cu sac nhanh 65W", "Chuot Bluetooth", "Ban phim co"],
    "Thoi trang": ["Ao khoac Gio", "Quan Jeans Slimfit", "Giay Sneaker", "Ao Polo DryEx"],
    "Gia dung": ["Noi chien khong dau", "May hut bui Robot", "May loc khong khi", "Am sieu toc"],
    "Thiet bi am thanh": ["Tai nghe Sony WH1000XM5", "Loa Marshall Stanmore", "AirPods Pro 2", "Loa JBL Charge 5"],
    "Dong ho": ["Apple Watch Ultra", "Garmin Fenix 7", "Casio G-Shock", "Galaxy Watch 6"],
    "The thao": ["Tham Yoga cao cap", "Bong da Tieuchuan", "Bo ta tay tap nha", "Binh nuoc giu nhiet"]
}


def generate_mock_products(count: int, seed: int = 42, shuffle: bool = True) -> List[Product]:
    """
    Sinh danh sách `count` sản phẩm với mã `product_id` DUY NHẤT.
    
    Kế thừa phương pháp sinh dữ liệu từ Lab 1 và Lab 2:
      - Sử dụng seed cố định để đảm bảo kết quả thực nghiệm có thể tái lập (Reproducible).
      - Nếu shuffle=True: Xáo trộn ngẫu nhiên thứ tự chèn. Đây là yếu tố quyết định
        giúp cây BST tự nhiên phân nhánh cân đối, đạt độ sâu trung bình O(log n).
      - Nếu shuffle=False: Giữ nguyên thứ tự tăng dần 1..count để kiểm chứng hiện tượng
        cây suy biến ở Bước 4.
        
    Độ phức tạp: O(n).
    """
    rng = random.Random(seed)
    
    # Tạo danh sách ID duy nhất 1..count
    ids = list(range(1, count + 1))
    if shuffle:
        rng.shuffle(ids)

    products: List[Product] = []
    for pid in ids:
        cat = rng.choice(CATEGORIES)
        base_name = rng.choice(SAMPLE_NAMES[cat])
        name = f"{base_name} #{pid % 1000:03d}"
        price = round(rng.uniform(50_000, 45_000_000), -3)  # Làm tròn đến nghìn
        stock = rng.randint(5, 500)

        p = Product(product_id=pid, name=name, price=price, category=cat, stock=stock)
        products.append(p)

    return products


# =============================================================================
# BƯỚC 3: THUẬT TOÁN TÌM KIẾM TUẦN TỰ O(n) ĐỂ ĐỐI CHỨNG (BASELINE LAB 1 & LAB 2)
# =============================================================================
def linear_search_by_id(product_list: List[Product], target_id: int) -> Optional[Product]:
    """
    Tìm kiếm tuần tự trên mảng/danh sách (Linear Search - O(n)).
    Đại diện cho mô hình kho lưu trữ ở Lab 1 (Mảng tĩnh) và Lab 2 (Linked List).
    
    Độ phức tạp:
      - Best Case: O(1) nếu phần tử nằm ở đầu mảng.
      - Worst Case: O(n) nếu phần tử nằm ở cuối mảng hoặc không tồn tại (phải quét qua n phần tử).
    """
    for p in product_list:
        if p.product_id == target_id:
            return p
    return None


# =============================================================================
# BƯỚC 4: HIỆN THỰC CÂY AVL (TỰ CÂN BẰNG - ADVANCED EXTENSION)
# =============================================================================
class AVLNode:
    """
    Nút trong Cây AVL (Adelson-Velsky and Landis Tree).
    
    Đặc điểm bổ sung so với BSTNode:
      - Có thêm thuộc tính `height` (chiều cao nút) được cập nhật liên tục
        sau mỗi thao tác chèn/xóa để phát hiện mất cân bằng cục bộ.
    """
    def __init__(self, product: Product) -> None:
        self.data: Product = product
        self.left: Optional[AVLNode] = None
        self.right: Optional[AVLNode] = None
        self.height: int = 1  # Chiều cao ban đầu của một nút lá mới tạo là 1


class AVLTree:
    """
    Cây Nhị phân Tìm kiếm Tự Cân bằng (AVL Tree).
    
    Định lý cân bằng AVL:
      Tại mọi nút u trong cây, độ lệch chiều cao giữa cây con trái và
      cây con phải (Balance Factor) KHÔNG ĐƯỢC VƯỢT QUÁ 1:
          |balance_factor(u)| = |height(left) - height(right)| <= 1.
          
    Nếu sau khi chèn một nút mới mà hệ số cân bằng vượt quá ngưỡng (-2 hoặc +2),
    cây lập tức thực hiện một trong 4 phép xoay cục bộ để tái lập cân bằng.
    
    Hệ quả:
      Chiều cao cây luôn được đảm bảo chặt chẽ: h <= 1.44 log2(n + 2).
      Mọi thao tác Tìm kiếm, Chèn, Xóa LUÔN ĐẠT HIỆU NĂNG O(log n)
      ngay cả khi dữ liệu nạp vào theo thứ tự ĐÃ SẮP XẾP TĂNG DẦN!
    """

    def __init__(self) -> None:
        self.root: Optional[AVLNode] = None
        self._size: int = 0

    # -------------------------------------------------------------------------
    # HÀM BỔ TRỢ ĐO CHIỀU CAO VÀ TÍNH HỆ SỐ CÂN BẰNG
    # -------------------------------------------------------------------------
    @staticmethod
    def _get_node_height(node: Optional[AVLNode]) -> int:
        """Lấy chiều cao của nút an toàn (trả về 0 nếu nút rỗng). Độ phức tạp: O(1)."""
        return node.height if node is not None else 0

    def _get_balance_factor(self, node: Optional[AVLNode]) -> int:
        """
        Tính hệ số cân bằng (Balance Factor) = height(left) - height(right).
        Độ phức tạp: O(1).
        """
        if node is None:
            return 0
        return self._get_node_height(node.left) - self._get_node_height(node.right)

    def _update_height(self, node: AVLNode) -> None:
        """Cập nhật lại chiều cao của một nút dựa vào chiều cao 2 con. Độ phức tạp: O(1)."""
        node.height = 1 + max(self._get_node_height(node.left), self._get_node_height(node.right))

    # -------------------------------------------------------------------------
    # 4 PHÉP XOAY CÂN BẰNG (ROTATIONS) - TẤT CẢ ĐỀU LÀ O(1)
    # -------------------------------------------------------------------------
    def _rotate_right(self, y: AVLNode) -> AVLNode:
        r"""
        Phép xoay Đơn sang Phải (Right Rotation - áp dụng khi lệch Trái - Trái / LL).
        
        Mô hình biến đổi:
               y                               x
              / \                             / \
             x   T3   -- right_rotate(y) --> T1   y
            / \                                  / \
           T1  T2                               T2  T3
           
        Độ phức tạp: O(1) (chỉ cập nhật vài con trỏ và tính lại chiều cao).
        """
        x = y.left
        assert x is not None
        t2 = x.right

        # Thực hiện phép xoay
        x.right = y
        y.left = t2

        # Cập nhật chiều cao (y trước vì y nay trở thành con của x)
        self._update_height(y)
        self._update_height(x)

        return x  # x trở thành nút gốc mới của cây con

    def _rotate_left(self, x: AVLNode) -> AVLNode:
        r"""
        Phép xoay Đơn sang Trái (Left Rotation - áp dụng khi lệch Phải - Phải / RR).
        
        Mô hình biến đổi:
             x                                   y
            / \                                 / \
           T1  y      -- left_rotate(x) -->    x   T3
              / \                             / \
             T2  T3                          T1  T2
             
        Độ phức tạp: O(1).
        """
        y = x.right
        assert y is not None
        t2 = y.left

        # Thực hiện phép xoay
        y.left = x
        x.right = t2

        # Cập nhật chiều cao (x trước vì x trở thành con của y)
        self._update_height(x)
        self._update_height(y)

        return y  # y trở thành nút gốc mới của cây con

    # -------------------------------------------------------------------------
    # THAO TÁC CHÈN VÀ TỰ CÂN BẰNG TRONG AVL (INSERT WITH SELF-BALANCING)
    # -------------------------------------------------------------------------
    def insert(self, product: Product) -> bool:
        """
        Thêm một sản phẩm vào cây AVL và tự động thực hiện phép xoay nếu mất cân bằng.
        
        Quy trình:
          1. Chèn đệ quy như BST thông thường.
          2. Cập nhật lại chiều cao của nút tổ tiên khi đệ quy quay lui (backtracking).
          3. Tính Balance Factor và xử lý 4 trường hợp mất cân bằng:
             - Trường hợp LL: Balance > 1 và Key < Left.Key
                 => Xoay Đơn sang Phải: `_rotate_right(node)`.
             - Trường hợp RR: Balance < -1 và Key > Right.Key
                 => Xoay Đơn sang Trái: `_rotate_left(node)`.
             - Trường hợp LR: Balance > 1 và Key > Left.Key
                 => Xoay Kép: Xoay Trái con trái, rồi Xoay Phải nút hiện tại.
             - Trường hợp RL: Balance < -1 và Key < Right.Key
                 => Xoay Kép: Xoay Phải con phải, rồi Xoay Trái nút hiện tại.
                 
        Độ phức tạp thời gian: O(log n) trong MỌI TRƯỜNG HỢP (kể cả dữ liệu đã sắp xếp).
        """
        inserted: bool = False

        def _insert_and_balance(node: Optional[AVLNode]) -> AVLNode:
            nonlocal inserted
            # Bước 1: Chèn như BST tiêu chuẩn
            if node is None:
                inserted = True
                return AVLNode(product)

            if product.product_id < node.data.product_id:
                node.left = _insert_and_balance(node.left)
            elif product.product_id > node.data.product_id:
                node.right = _insert_and_balance(node.right)
            else:
                inserted = False
                return node  # Trùng lặp ID -> bỏ qua

            # Bước 2: Cập nhật chiều cao của nút tổ tiên
            self._update_height(node)

            # Bước 3: Lấy hệ số cân bằng để kiểm tra vi phạm
            balance = self._get_balance_factor(node)

            # Bước 4: Tự động cân bằng khi xảy ra vi phạm (|balance| > 1)
            
            # TRƯỜNG HỢP 1: Lệch Trái - Trái (Left-Left / LL) -> Xoay Đơn Phải
            if balance > 1 and node.left is not None and product.product_id < node.left.data.product_id:
                return self._rotate_right(node)

            # TRƯỜNG HỢP 2: Lệch Phải - Phải (Right-Right / RR) -> Xoay Đơn Trái
            if balance < -1 and node.right is not None and product.product_id > node.right.data.product_id:
                return self._rotate_left(node)

            # TRƯỜNG HỢP 3: Lệch Trái - Phải (Left-Right / LR) -> Xoay Kép (Trái con trái, Phải nút hiện tại)
            if balance > 1 and node.left is not None and product.product_id > node.left.data.product_id:
                node.left = self._rotate_left(node.left)
                return self._rotate_right(node)

            # TRƯỜNG HỢP 4: Lệch Phải - Trái (Right-Left / RL) -> Xoay Kép (Phải con phải, Trái nút hiện tại)
            if balance < -1 and node.right is not None and product.product_id < node.right.data.product_id:
                node.right = self._rotate_right(node.right)
                return self._rotate_left(node)

            return node

        self.root = _insert_and_balance(self.root)
        if inserted:
            self._size += 1
        return inserted

    def search(self, target_id: int) -> Optional[Product]:
        """
        Tìm kiếm trên cây AVL.
        Bảo đảm chắc chắn thời gian truy xuất O(log n) nhờ chiều cao luôn tối ưu.
        """
        current = self.root
        while current is not None:
            if target_id == current.data.product_id:
                return current.data
            elif target_id < current.data.product_id:
                current = current.left
            else:
                current = current.right
        return None

    def height(self) -> int:
        """Lấy chiều cao gốc của cây AVL. Độ phức tạp: O(1)."""
        return self._get_node_height(self.root)

    def size(self) -> int:
        """Lấy số lượng phần tử trong cây AVL. Độ phức tạp: O(1)."""
        return self._size

    def clear(self) -> None:
        """Hủy cây AVL an toàn."""
        def _destroy(node: Optional[AVLNode]) -> None:
            if node is None:
                return
            _destroy(node.left)
            _destroy(node.right)
            node.left = None
            node.right = None
            node.data = None  # type: ignore

        _destroy(self.root)
        self.root = None
        self._size = 0


# =============================================================================
# CÁC KỊCH BẢN THỰC NGHIỆM VÀ ĐO LƯỜNG HIỆU NĂNG (BENCHMARK SUITE)
# =============================================================================

def print_separator(title: str = "") -> None:
    """In dải phân cách thẩm mỹ cho báo cáo console."""
    if title:
        print(f"\n{'=' * 78}")
        print(f" {title.upper()} ")
        print(f"{'=' * 78}")
    else:
        print(f"{'-' * 78}")


def demo_step1_bst_operations() -> None:
    """
    BƯỚC 1: Kiểm chứng toàn diện các thao tác cơ bản trên Cây BST:
      - Thêm phần tử (Insert).
      - Tìm kiếm (Search).
      - Xóa phần tử (Delete) kiểm tra đủ 3 trường hợp:
          + TH1: Xóa nút lá (Leaf).
          + TH2: Xóa nút có đúng 1 con (Single child).
          + TH3: Xóa nút có đủ 2 con (Two children - In-order Successor).
      - Duyệt cây theo 4 cách: In-order (LNR), Pre-order (NLR), Post-order (LRN), Level-order (BFS).
      - Giải phóng bộ nhớ (Post-order Destructor / Clear).
    """
    print_separator("BƯỚC 1: HIỆN THỰC & KIỂM CHỨNG CÁC THAO TÁC CƠ BẢN TRÊN CÂY BST")
    bst = BinarySearchTree()

    # Dữ liệu mẫu minh họa có cấu trúc cây đa dạng
    sample_items = [
        Product(50, "Ban Phim Co Custom", 1_800_000, "Phu kien", 20),
        Product(30, "Chuot Khong Day Ergonomic", 650_000, "Phu kien", 45),
        Product(70, "Man Hinh Gaming 27 inch", 6_200_000, "Dien tu", 15),
        Product(20, "Lot Chuot Size XL", 150_000, "Phu kien", 100),
        Product(40, "Gia Do Tai Nghe", 220_000, "Phu kien", 30),
        Product(60, "Webcam Full HD 1080p", 950_000, "Dien tu", 25),
        Product(80, "Ghe Ergonomic Lumbar", 4_500_000, "Gia dung", 10),
        Product(10, "Hub Chuyen Doi Type-C", 350_000, "Phu kien", 60),  # Lá sâu
    ]

    print("[1.1] Chèn lần lượt 8 sản phẩm vào cây BST:")
    for item in sample_items:
        bst.insert(item)
        print(f"   + Đã chèn ID={item.product_id:02d}: {item.name}")

    print(f"\n=> Tổng số nút trong cây: {bst.size()} | Chiều cao cây: {bst.height()}")

    # 1.2 Duyệt Trung tự (In-order) chứng minh tính chất tự động sắp xếp
    print("\n[1.2] Duyệt Trung tự (In-order Traversal - LNR):")
    print("      (Chứng minh: Danh sách tự động sắp xếp TĂNG DẦN theo ID)")
    inorder_list = bst.inorder_traversal()
    for p in inorder_list:
        print(f"      {p}")

    # 1.3 Duyệt Tiền tự & Hậu tự & Theo tầng (BFS - Kế thừa Lab 3)
    print("\n[1.3] Các phép duyệt khác:")
    print("      - Tiền tự (Pre-order / NLR):", [p.product_id for p in bst.preorder_traversal()])
    print("      - Hậu tự   (Post-order / LRN):", [p.product_id for p in bst.postorder_traversal()])
    print("      - Theo tầng (Level-order / BFS - Lab 3 Queue):", [p.product_id for p in bst.level_order_traversal()])

    # 1.4 Kiểm tra tìm kiếm
    print("\n[1.4] Kiểm chứng thao tác tìm kiếm (Search):")
    found_item = bst.search(40)
    print(f"      Tìm ID=40: {'THÀNH CÔNG -> ' + str(found_item) if found_item else 'THẤT BẠI'}")
    not_found = bst.search(99)
    print(f"      Tìm ID=99: {'THÀNH CÔNG' if not_found else 'KHÔNG TÌM THẤY (Chính xác)'}")

    # 1.5 Kiểm tra Xóa 3 trường hợp
    print("\n[1.5] Kiểm tra thao tác Xóa (Delete) xử lý triệt để 3 trường hợp:")

    # TH1: Xóa nút lá ID=10 (không có con nào)
    print("   * Trường hợp 1: Xóa nút lá ID=10...")
    bst.delete(10)
    print("     -> Kết quả sau khi xóa ID=10 (In-order):", [p.product_id for p in bst.inorder_traversal()])

    # TH2: Xóa nút có đúng 1 con (Nút 20 hiện chỉ còn con nào? Nút 20 ban đầu có con trái là 10, nay thành lá,
    # hãy tạo một nút có đúng 1 con bằng cách xét nút 30: có con trái 20 và con phải 40.
    # Nút 20 nay là lá. Xóa 20 thì là lá. Giờ ta xóa 30 (có 2 con: 20 và 40).
    # Để minh họa nút có 1 con: Ta chèn ID=25 (con phải của 20), sau đó xóa 20 (nút có 1 con trái/phải)!
    bst.insert(Product(25, "Bút Lau Màn Hình", 50_000, "Phu kien", 10))
    print("   * Trường hợp 2: Xóa nút có đúng 1 con (Nút ID=20 chỉ có con phải ID=25)...")
    bst.delete(20)
    print("     -> Kết quả sau khi xóa ID=20 (In-order):", [p.product_id for p in bst.inorder_traversal()])

    # TH3: Xóa nút gốc có đủ 2 con: Gốc ID=50 (có con trái 30 và con phải 70)
    print("   * Trường hợp 3: Xóa nút có đủ 2 con (Gốc ID=50, tìm In-order Successor là ID=60)...")
    bst.delete(50)
    print("     -> Kết quả sau khi xóa nút gốc ID=50 (In-order):", [p.product_id for p in bst.inorder_traversal()])
    print(f"     -> Nút gốc mới hiện tại là: {bst.root.data.product_id if bst.root else 'None'}")

    # 1.6 Kiểm tra Post-order Destructor
    print("\n[1.6] Kiểm tra giải phóng bộ nhớ an toàn (Post-order Destructor / Clear):")
    freed_nodes = bst.clear()
    print(f"      Đã giải phóng an toàn {freed_nodes} nút. Cây hiện rỗng: {bst.is_empty()} (size={bst.size()})")


def demo_step2_warehouse_integration(product_count: int = 100_000) -> Tuple[BinarySearchTree, List[Product]]:
    """
    BƯỚC 2: Tích hợp dữ liệu kho hàng quy mô lớn vào Cây BST.
      - Sinh ngẫu nhiên từ 100.000 sản phẩm với ID duy nhất.
      - Nạp toàn bộ vào cây BST bằng hàm `insert()`.
      - Đo đạc thời gian nạp.
      - Trích xuất 5 phần tử đầu tiên bằng `inorder_traversal()` để kiểm chứng
        dữ liệu tự động được sắp xếp tăng dần theo ID.
    """
    print_separator(f"BƯỚC 2: TÍCH HỢP KHO HÀNG {product_count:,} SẢN PHẨM VÀO CÂY BST")

    print(f"[*] Đang sinh ngẫu nhiên {product_count:,} sản phẩm với mã ID duy nhất (seed=42)...")
    t0_gen = time.perf_counter()
    products = generate_mock_products(count=product_count, seed=42, shuffle=True)
    t1_gen = time.perf_counter()
    print(f"    -> Đã sinh xong dữ liệu trong: {(t1_gen - t0_gen) * 1000:.2f} ms")

    print(f"\n[*] Đang nạp {product_count:,} sản phẩm vào Cây Nhị phân Tìm kiếm (BST)...")
    bst = BinarySearchTree()
    t0_load = time.perf_counter()
    for p in products:
        bst.insert(p)
    t1_load = time.perf_counter()
    print(f"    -> Đã nạp thành công {bst.size():,} nút vào cây BST.")
    print(f"    -> Thời gian nạp: {(t1_load - t0_load):.4f} giây "
          f"({(t1_load - t0_load) * 1000 / product_count:.4f} ms/sản phẩm)")
    print(f"    -> Chiều cao cây thực tế h: {bst.height()} "
          f"(So với lý thuyết tối ưu log2(N) ≈ 17, cho thấy cây phân nhánh rất tốt!)")

    # Kiểm chứng In-order Traversal
    print("\n[*] Kiểm chứng 5 sản phẩm đầu tiên từ phép duyệt In-order (Trung tự):")
    first_5 = bst.inorder_traversal(limit=5)
    for p in first_5:
        print(f"    {p}")

    # Kiểm tra tính đơn điệu tăng dần của In-order trên 1.000 phần tử đầu
    sample_check = bst.inorder_traversal(limit=1000)
    is_sorted = all(sample_check[i].product_id < sample_check[i + 1].product_id for i in range(len(sample_check) - 1))
    print(f"\n=> Kiểm chứng tính đơn điệu tăng dần của ID: {'CHÍNH XÁC 100%' if is_sorted else 'SAI LỆCH'}")

    return bst, products


def demo_step3_benchmark(bst: BinarySearchTree, products: List[Product]) -> None:
    """
    BƯỚC 3: Tra cứu nhanh và Đo lường hiệu năng (Benchmark).
      - Sử dụng `time.perf_counter()` đo thời gian với độ chính xác nano-giây.
      - Đối chiếu 2 cấu trúc:
          + Tuyến tính (Linear Search O(n) trên List - đại diện Lab 1 và Lab 2).
          + Phi tuyến tính (Binary Search Tree O(log n)).
      - Thực nghiệm trên 2 kịch bản trọng yếu:
          + Kịch bản 1: Worst Case - Tìm ID hoàn toàn KHÔNG TỒN TẠI (ID = 999_999_999).
          + Kịch bản 2: Deep Existing Case - Tìm ID có tồn tại ở độ sâu lớn.
      - Tính toán Speedup factor (Tỉ lệ tăng tốc = t_linear / t_bst).
    """
    print_separator("BƯỚC 3: ĐO LƯỜNG HIỆU NĂNG (BENCHMARK) LINEAR SEARCH O(n) VS BST O(log n)")

    N = len(products)
    REPEAT_TRIALS = 20  # Lặp lại nhiều lần để lấy thời gian trung bình ổn định

    # -------------------------------------------------------------------------
    # KỊCH BẢN 1: WORST CASE - TÌM ID KHÔNG TỒN TẠI
    # -------------------------------------------------------------------------
    non_existent_id = 999_999_999
    print(f"[KỊCH BẢN 1: WORST CASE] Tìm kiếm mã sản phẩm KHÔNG TỒN TẠI (ID = {non_existent_id})")
    print(f"              Quy mô kho hàng: N = {N:,} sản phẩm\n")

    # 1.1 Tuyến tính (Linear Search O(n))
    t0 = time.perf_counter()
    for _ in range(REPEAT_TRIALS):
        res_linear = linear_search_by_id(products, non_existent_id)
    t1 = time.perf_counter()
    avg_linear_time_ms = ((t1 - t0) / REPEAT_TRIALS) * 1000

    # 1.2 Cây BST (O(log n))
    t0 = time.perf_counter()
    for _ in range(REPEAT_TRIALS):
        res_bst = bst.search(non_existent_id)
    t1 = time.perf_counter()
    avg_bst_time_ms = ((t1 - t0) / REPEAT_TRIALS) * 1000

    speedup_1 = avg_linear_time_ms / avg_bst_time_ms if avg_bst_time_ms > 0 else float("inf")

    print(f"  * Linear Search O(n) [Lab 1/2] : {avg_linear_time_ms:>10.4f} ms | Kết quả: {res_linear}")
    print(f"  * BST Search O(log n) [Lab 4]  : {avg_bst_time_ms:>10.6f} ms | Kết quả: {res_bst}")
    print(f"  => TỈ LỆ TĂNG TỐC (SPEEDUP)    : {speedup_1:>10.1f} LẦN NHANH HƠN!")

    # -------------------------------------------------------------------------
    # KỊCH BẢN 2: DEEP EXISTING CASE - TÌM ID CÓ TỒN TẠI Ở ĐỘ SÂU LỚN
    # -------------------------------------------------------------------------
    # Lấy ID của sản phẩm nằm ở 1/10 cuối cùng của danh sách mảng để mô phỏng
    # việc tìm kiếm tuyến tính phải duyệt gần hết mảng.
    deep_product = products[int(N * 0.95)]
    target_id = deep_product.product_id

    print(f"\n[KỊCH BẢN 2: EXISTING CASE] Tìm kiếm sản phẩm CÓ TỒN TẠI (ID = {target_id})")
    print(f"              Tên sản phẩm: '{deep_product.name}' | Nằm ở vị trí sâu trong kho\n")

    # 2.1 Tuyến tính (Linear Search O(n))
    t0 = time.perf_counter()
    for _ in range(REPEAT_TRIALS):
        res_linear = linear_search_by_id(products, target_id)
    t1 = time.perf_counter()
    avg_linear_time_ms_2 = ((t1 - t0) / REPEAT_TRIALS) * 1000

    # 2.2 Cây BST (O(log n))
    t0 = time.perf_counter()
    for _ in range(REPEAT_TRIALS):
        res_bst = bst.search(target_id)
    t1 = time.perf_counter()
    avg_bst_time_ms_2 = ((t1 - t0) / REPEAT_TRIALS) * 1000

    speedup_2 = avg_linear_time_ms_2 / avg_bst_time_ms_2 if avg_bst_time_ms_2 > 0 else float("inf")

    print(f"  * Linear Search O(n) [Lab 1/2] : {avg_linear_time_ms_2:>10.4f} ms | Kết quả: Tìm thấy ID={res_linear.product_id if res_linear else None}")
    print(f"  * BST Search O(log n) [Lab 4]  : {avg_bst_time_ms_2:>10.6f} ms | Kết quả: Tìm thấy ID={res_bst.product_id if res_bst else None}")
    print(f"  => TỈ LỆ TĂNG TỐC (SPEEDUP)    : {speedup_2:>10.1f} LẦN NHANH HƠN!")

    # Bảng tổng hợp thực nghiệm
    print("\n" + "=" * 78)
    print(f"{'KỊCH BẢN THỬ NGHIỆM':<30} | {'LINEAR SEARCH O(n)':<18} | {'BST SEARCH O(log n)':<18} | {'TĂNG TỐC'}")
    print("-" * 78)
    print(f"{'Worst Case (ID không có)':<30} | {avg_linear_time_ms:>14.4f} ms | {avg_bst_time_ms:>14.6f} ms | {speedup_1:>8.1f}x")
    print(f"{'Deep Case (ID tồn tại sâu)':<30} | {avg_linear_time_ms_2:>14.4f} ms | {avg_bst_time_ms_2:>14.6f} ms | {speedup_2:>8.1f}x")
    print("=" * 78)


def demo_step4_avl_self_balancing(test_n: int = 10_000) -> None:
    """
    BƯỚC 4 (NÂNG CAO - ĐIỂM CỘNG): XỬ LÝ CÂY SUY BIẾN BẰNG CÂY TỰ CÂN BẰNG AVL.
    
    Vấn đề:
      Khi người dùng nạp dữ liệu đã được sắp xếp tăng dần sẵn (1, 2, 3, ..., N),
      cây BST thông thường rẽ phải liên tục, biến thành một Danh sách liên kết suy biến:
        - Chiều cao cây: h = N.
        - Độ phức tạp tìm kiếm: suy thoái từ O(log n) về O(n)!
        - Nguy cơ tràn Call Stack.
        
    Giải pháp:
      Cây AVL sử dụng 4 phép xoay (LL, RR, LR, RL) để tự cân bằng sau mỗi lần chèn.
      Đảm bảo chiều cao luôn duy trì ở mức h ≈ log2(N).
      
    Thực nghiệm:
      Nạp 10.000 phần tử có thứ tự tăng dần vào cả BST thông thường và Cây AVL.
      So sánh chiều cao và đo thời gian tìm kiếm.
    """
    print_separator(f"BƯỚC 4: XỬ LÝ CÂY SUY BIẾN VỚI CÂY TỰ CÂN BẰNG AVL (N = {test_n:,})")

    # Tạo 10.000 sản phẩm đã được SẮP XẾP TĂNG DẦN THEO ID (shuffle=False)
    print(f"[*] Tạo {test_n:,} sản phẩm với ID tăng dần từ 1 đến {test_n:,}...")
    sorted_products = generate_mock_products(count=test_n, seed=42, shuffle=False)

    # 4.1 Nạp vào Cây BST tiêu chuẩn (Gây suy biến)
    print("\n[4.1] Đang nạp vào Cây BST tiêu chuẩn (không tự cân bằng)...")
    degenerate_bst = BinarySearchTree()
    t0 = time.perf_counter()
    for p in sorted_products:
        degenerate_bst.insert(p)
    t1 = time.perf_counter()
    bst_insert_time = (t1 - t0) * 1000
    bst_height = degenerate_bst.height()
    print(f"      -> Thời gian chèn BST: {bst_insert_time:.2f} ms")
    print(f"      -> CHIỀU CAO CÂY BST : h = {bst_height:,} "
          f"(= N, CÂY ĐÃ BỊ SUY BIẾN HOÀN TOÀN THÀNH DANH SÁCH LIÊN KẾT!)")

    # 4.2 Nạp vào Cây AVL (Tự cân bằng qua phép xoay RR)
    print("\n[4.2] Đang nạp vào Cây AVL (tự cân bằng liên tục qua các phép xoay)...")
    avl_tree = AVLTree()
    t0 = time.perf_counter()
    for p in sorted_products:
        avl_tree.insert(p)
    t1 = time.perf_counter()
    avl_insert_time = (t1 - t0) * 1000
    avl_height = avl_tree.height()
    print(f"      -> Thời gian chèn AVL: {avl_insert_time:.2f} ms")
    print(f"      -> CHIỀU CAO CÂY AVL : h = {avl_height} "
          f"(Cực kỳ tối ưu! Gần sát cận lý thuyết ceil(log2({test_n:,})) = 14)")

    # 4.3 Đo lường hiệu năng tìm kiếm giữa Cây Suy Biến vs Cây AVL
    search_target = test_n  # Tìm phần tử cuối cùng (ID = 10,000)
    TRIALS = 100

    print(f"\n[4.3] Đo tốc độ tìm kiếm phần tử ID={search_target} trên 2 cây ({TRIALS} lần lặp):")

    # Tìm trên BST suy biến (Duyệt qua 10,000 nút)
    t0 = time.perf_counter()
    for _ in range(TRIALS):
        res_bst = degenerate_bst.search(search_target)
    t1 = time.perf_counter()
    t_bst_search_ms = ((t1 - t0) / TRIALS) * 1000

    # Tìm trên AVL Tree (Chỉ duyệt qua tối đa 14 nút!)
    t0 = time.perf_counter()
    for _ in range(TRIALS):
        res_avl = avl_tree.search(search_target)
    t1 = time.perf_counter()
    t_avl_search_ms = ((t1 - t0) / TRIALS) * 1000

    speedup_avl = t_bst_search_ms / t_avl_search_ms if t_avl_search_ms > 0 else float("inf")

    print(f"  * BST Suy Biến (h={bst_height}) : {t_bst_search_ms:>10.4f} ms (suy thoái về O(n))")
    print(f"  * AVL Tự Cân Bằng (h={avl_height}) : {t_avl_search_ms:>10.6f} ms (chuẩn O(log n))")
    print(f"  => CÂY AVL NHANH HƠN           : {speedup_avl:>10.1f} LẦN!")

    print("\n" + "=" * 78)
    print(f"{'THUỘC TÍNH / CHỈ SỐ':<30} | {'BST TIÊU CHUẨN (SUY BIẾN)':<24} | {'CÂY TỰ CÂN BẰNG AVL'}")
    print("-" * 78)
    print(f"{'Dữ liệu đầu vào':<30} | {'Đã sắp xếp tăng dần 1..N':<24} | {'Đã sắp xếp tăng dần 1..N'}")
    print(f"{'Số lượng phần tử':<30} | {test_n:<24,} | {test_n:,}")
    print(f"{'Chiều cao cây (Height)':<30} | {bst_height:<24,} | {avl_height} (Giảm {bst_height / avl_height:.0f} lần!)")
    print(f"{'Độ phức tạp tìm kiếm':<30} | {'O(n)':<24} | {'O(log n)'}")
    print(f"{'Thời gian tìm kiếm (ms)':<30} | {t_bst_search_ms:<24.4f} | {t_avl_search_ms:.6f}")
    print("=" * 78)


# =============================================================================
# MENU TƯƠNG TÁC CONSOLE (KẾ THỪA TỪ LAB 2 & LAB 3)
# =============================================================================
def interactive_menu(bst: BinarySearchTree) -> None:
    """
    Menu tương tác dành cho giảng viên và kỹ sư trực tiếp kiểm thử trên dòng lệnh.
    """
    while True:
        print("\n" + "=" * 55)
        print("   HỆ THỐNG QUẢN LÝ KHO HÀNG MINI E-COMMERCE (LAB 4 - BST)")
        print("=" * 55)
        print(" 1. Tra cứu sản phẩm theo ID (O(log n))")
        print(" 2. Thêm sản phẩm mới vào Kho (O(log n))")
        print(" 3. Xóa sản phẩm khỏi Kho (Xử lý 3 trường hợp)")
        print(" 4. Xem thống kê Cây (Số lượng, Chiều cao)")
        print(" 5. Duyệt Kho hàng (In-order - hiển thị mẫu)")
        print(" 6. Thoát")
        print("=" * 55)
        choice = input("Nhập lựa chọn của bạn (1-6): ").strip()

        if choice == "1":
            raw_id = input("Nhập mã sản phẩm (ID) cần tra cứu: ").strip()
            if not raw_id.isdigit():
                print("Lỗi: ID phải là số nguyên dương!")
                continue
            pid = int(raw_id)
            t0 = time.perf_counter()
            product = bst.search(pid)
            t1 = time.perf_counter()
            if product:
                print("\n[KẾT QUẢ TÌM THẤY]:")
                print(f"  {product}")
                print(f"  Thời gian truy xuất BST: {(t1 - t0) * 1000:.6f} ms")
            else:
                print(f"\nKhông tìm thấy sản phẩm với ID = {pid} trong kho!")

        elif choice == "2":
            try:
                pid = int(input("Nhập mã ID mới: ").strip())
                name = input("Nhập tên sản phẩm: ").strip()
                price = float(input("Nhập giá niêm yết (VND): ").strip())
                cat = input("Nhập danh mục: ").strip() or "Khac"
                stock = int(input("Nhập số lượng tồn: ").strip() or "50")

                new_p = Product(product_id=pid, name=name, price=price, category=cat, stock=stock)
                if bst.insert(new_p):
                    print(f"\nThêm thành công sản phẩm ID={pid} vào cây BST!")
                else:
                    print(f"\nLỗi: ID={pid} đã tồn tại trong kho (Quy tắc BST không trùng khóa)!")
            except ValueError:
                print("Lỗi định dạng dữ liệu đầu vào. Vui lòng thử lại!")

        elif choice == "3":
            raw_id = input("Nhập ID sản phẩm cần xóa: ").strip()
            if not raw_id.isdigit():
                print("Lỗi: ID phải là số nguyên dương!")
                continue
            pid = int(raw_id)
            if bst.delete(pid):
                print(f"\nĐã xóa thành công sản phẩm ID={pid} khỏi cây!")
            else:
                print(f"\nKhông tìm thấy sản phẩm ID={pid} để xóa!")

        elif choice == "4":
            print(f"\n[THỐNG KÊ CÂY KHO HÀNG BST]:")
            print(f"  - Tổng số sản phẩm hiện tại: {bst.size():,} nút")
            print(f"  - Chiều cao cây hiện tại    : {bst.height()}")
            print(f"  - Trạng thái cây            : {'Rỗng' if bst.is_empty() else 'Hoạt động bình thường'}")

        elif choice == "5":
            limit = 10
            print(f"\nDanh sách {limit} sản phẩm đầu tiên theo thứ tự tăng dần ID (In-order):")
            for p in bst.inorder_traversal(limit=limit):
                print(f"  {p}")

        elif choice == "6":
            print("\nCảm ơn bạn đã sử dụng hệ thống Lõi E-commerce Mini Lab 4. Tạm biệt!\n")
            break
        else:
            print("Lựa chọn không hợp lệ, vui lòng chọn từ 1 đến 6!")


# =============================================================================
# HÀM ĐIỀU PHỐI CHÍNH (MAIN ENTRY POINT)
# =============================================================================
def main() -> None:
    """
    Điểm khởi chạy chính của chương trình Lab 4.
    Hỗ trợ chế độ chạy toàn bộ demo và benchmark (`--demo`)
    hoặc chạy tương tác kết hợp menu dòng lệnh.
    """
    demo_only = "--demo" in sys.argv

    print("\n" + "#" * 78)
    print("#  BÀI THỰC HÀNH LAB 4: CÂY NHỊ PHÂN TÌM KIẾM (BST) & CÂY AVL               #")
    print("#  LÕI HỆ THỐNG THƯƠNG MẠI ĐIỆN TỬ MINI (MINI E-COMMERCE CORE)             #")
    print("#" * 78)

    # Chạy tuần tự các bước 1, 2, 3, 4 theo yêu cầu đề bài
    demo_step1_bst_operations()
    bst, products = demo_step2_warehouse_integration(product_count=100_000)
    demo_step3_benchmark(bst, products)
    demo_step4_avl_self_balancing(test_n=10_000)

    print("\n" + "=" * 78)
    print(" HOÀN THÀNH TOÀN BỘ 4 BƯỚC THỰC NGHIỆM LAB 4")
    print("=" * 78)

    if not demo_only:
        # Nếu chạy thông thường, mở menu tương tác để người dùng thử nghiệm
        print("\nChuyển sang chế độ Menu Tương tác để bạn trực tiếp thao tác kho hàng...")
        interactive_menu(bst)


if __name__ == "__main__":
    main()
