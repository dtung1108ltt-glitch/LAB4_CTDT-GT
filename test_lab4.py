"""
test_lab4.py
===============================================================================
BỘ KIỂM THỬ TỰ ĐỘNG (UNIT TESTS) CHO BÀI THỰC HÀNH LAB 4
Kiểm thử toàn diện:
  1. Cây Nhị phân Tìm kiếm (BST):
     - Chèn phần tử hợp lệ & Từ chối trùng khóa (Duplicate ID).
     - Tìm kiếm phần tử tồn tại & không tồn tại.
     - Xóa phần tử xử lý triệt để 3 trường hợp:
         + Case 1: Nút lá (Leaf node).
         + Case 2: Nút có 1 con (Single child).
         + Case 3: Nút có 2 con (Two children - In-order successor).
     - Các phép duyệt: In-order (tăng dần), Pre-order, Post-order, Level-order (BFS).
     - Hủy cây (Clear / Post-order Destructor).
  2. Cây Tự Cân Bằng (AVL Tree):
     - Tự cân bằng khi chèn dữ liệu tăng dần (RR rotation).
     - Tự cân bằng khi chèn dữ liệu giảm dần (LL rotation).
     - Tự cân bằng xoay kép (LR và RL rotations).
     - Chiều cao cây luôn bị chặn bởi O(log n).
===============================================================================
"""

import unittest
from lab4_ecommerce_tree import Product, BinarySearchTree, AVLTree, generate_mock_products


class TestBinarySearchTree(unittest.TestCase):
    """Kiểm thử tính đúng đắn của Cây Nhị phân Tìm kiếm (BST)."""

    def setUp(self) -> None:
        self.bst = BinarySearchTree()
        # Cấu trúc cây mẫu:
        #          50
        #        /    \
        #       30     70
        #      /  \   /  \
        #     20  40 60  80
        #    /
        #   10
        self.products = [
            Product(50, "P50", 500.0, "CatA"),
            Product(30, "P30", 300.0, "CatB"),
            Product(70, "P70", 700.0, "CatC"),
            Product(20, "P20", 200.0, "CatA"),
            Product(40, "P40", 400.0, "CatB"),
            Product(60, "P60", 600.0, "CatC"),
            Product(80, "P80", 800.0, "CatA"),
            Product(10, "P10", 100.0, "CatB"),
        ]
        for p in self.products:
            self.bst.insert(p)

    def test_insert_and_size(self) -> None:
        """Kiểm tra số lượng nút và chiều cao sau khi chèn."""
        self.assertEqual(self.bst.size(), 8)
        self.assertFalse(self.bst.is_empty())
        self.assertEqual(self.bst.height(), 4)

    def test_duplicate_insert_rejected(self) -> None:
        """Kiểm tra quy tắc không cho phép trùng ID trong BST."""
        dup = Product(50, "P50_Duplicate", 999.0, "CatA")
        inserted = self.bst.insert(dup)
        self.assertFalse(inserted)
        self.assertEqual(self.bst.size(), 8)

    def test_search_existing_and_non_existing(self) -> None:
        """Kiểm tra tìm kiếm ID có và không có."""
        found = self.bst.search(40)
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "P40")

        not_found = self.bst.search(999)
        self.assertIsNone(not_found)

    def test_inorder_is_strictly_sorted(self) -> None:
        """Kiểm tra In-order Traversal luôn trả về mảng tăng dần theo ID."""
        traversal = self.bst.inorder_traversal()
        ids = [p.product_id for p in traversal]
        self.assertEqual(ids, [10, 20, 30, 40, 50, 60, 70, 80])

    def test_preorder_and_postorder_traversals(self) -> None:
        """Kiểm tra đúng thứ tự duyệt Tiền tự và Hậu tự."""
        pre = [p.product_id for p in self.bst.preorder_traversal()]
        self.assertEqual(pre, [50, 30, 20, 10, 40, 70, 60, 80])

        post = [p.product_id for p in self.bst.postorder_traversal()]
        self.assertEqual(post, [10, 20, 40, 30, 60, 80, 70, 50])

    def test_level_order_traversal(self) -> None:
        """Kiểm tra duyệt theo tầng (BFS với Queue)."""
        level = [p.product_id for p in self.bst.level_order_traversal()]
        self.assertEqual(level, [50, 30, 70, 20, 40, 60, 80, 10])

    def test_delete_case_1_leaf_node(self) -> None:
        """Trường hợp 1: Xóa nút lá (ID = 10)."""
        deleted = self.bst.delete(10)
        self.assertTrue(deleted)
        self.assertEqual(self.bst.size(), 7)
        self.assertIsNone(self.bst.search(10))
        ids = [p.product_id for p in self.bst.inorder_traversal()]
        self.assertEqual(ids, [20, 30, 40, 50, 60, 70, 80])

    def test_delete_case_2_single_child(self) -> None:
        """Trường hợp 2: Xóa nút có đúng 1 con (Nút ID=20 chỉ có con trái là 10)."""
        deleted = self.bst.delete(20)
        self.assertTrue(deleted)
        self.assertEqual(self.bst.size(), 7)
        self.assertIsNone(self.bst.search(20))
        # Nút 10 phải được nối trực tiếp làm con trái của 30
        ids = [p.product_id for p in self.bst.inorder_traversal()]
        self.assertEqual(ids, [10, 30, 40, 50, 60, 70, 80])

    def test_delete_case_3_two_children(self) -> None:
        """Trường hợp 3: Xóa nút có đủ 2 con (Xóa nút gốc ID=50)."""
        deleted = self.bst.delete(50)
        self.assertTrue(deleted)
        self.assertEqual(self.bst.size(), 7)
        self.assertIsNone(self.bst.search(50))
        # Nút thế mạng In-order Successor là 60
        self.assertEqual(self.bst.root.data.product_id, 60)
        ids = [p.product_id for p in self.bst.inorder_traversal()]
        self.assertEqual(ids, [10, 20, 30, 40, 60, 70, 80])

    def test_clear_destructor(self) -> None:
        """Kiểm tra giải phóng cây hoàn toàn."""
        freed = self.bst.clear()
        self.assertEqual(freed, 8)
        self.assertTrue(self.bst.is_empty())
        self.assertEqual(self.bst.size(), 0)
        self.assertIsNone(self.bst.root)


class TestAVLTree(unittest.TestCase):
    """Kiểm thử tính đúng đắn và khả năng tự cân bằng của Cây AVL."""

    def test_avl_rotations_ll_and_rr(self) -> None:
        """Kiểm tra xoay đơn LL và RR."""
        # 1. Chèn tăng dần 1, 2, 3 -> Kích hoạt RR Rotation (xoay trái)
        avl_rr = AVLTree()
        for i in [1, 2, 3]:
            avl_rr.insert(Product(i, f"P{i}", 10.0, "Cat"))
        # Sau khi xoay trái, gốc phải là 2, chiều cao là 2
        self.assertEqual(avl_rr.root.data.product_id, 2)
        self.assertEqual(avl_rr.height(), 2)

        # 2. Chèn giảm dần 3, 2, 1 -> Kích hoạt LL Rotation (xoay phải)
        avl_ll = AVLTree()
        for i in [3, 2, 1]:
            avl_ll.insert(Product(i, f"P{i}", 10.0, "Cat"))
        # Sau khi xoay phải, gốc phải là 2, chiều cao là 2
        self.assertEqual(avl_ll.root.data.product_id, 2)
        self.assertEqual(avl_ll.height(), 2)

    def test_avl_rotations_lr_and_rl(self) -> None:
        """Kiểm tra xoay kép LR và RL."""
        # 1. LR Rotation: Chèn 30, 10, 20
        avl_lr = AVLTree()
        for i in [30, 10, 20]:
            avl_lr.insert(Product(i, f"P{i}", 10.0, "Cat"))
        self.assertEqual(avl_lr.root.data.product_id, 20)
        self.assertEqual(avl_lr.height(), 2)

        # 2. RL Rotation: Chèn 10, 30, 20
        avl_rl = AVLTree()
        for i in [10, 30, 20]:
            avl_rl.insert(Product(i, f"P{i}", 10.0, "Cat"))
        self.assertEqual(avl_rl.root.data.product_id, 20)
        self.assertEqual(avl_rl.height(), 2)

    def test_avl_height_with_sorted_input(self) -> None:
        """Kiểm tra cây AVL không bị suy biến khi nạp 1000 phần tử tăng dần."""
        avl = AVLTree()
        for i in range(1, 1001):
            avl.insert(Product(i, f"P{i}", 10.0, "Cat"))
        self.assertEqual(avl.size(), 1000)
        # log2(1000) ≈ 9.96; chiều cao AVL luôn <= 1.44 * log2(1000) ≈ 14
        self.assertLessEqual(avl.height(), 14)
        # Tìm kiếm phần tử cuối cùng
        found = avl.search(1000)
        self.assertIsNotNone(found)
        self.assertEqual(found.product_id, 1000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
