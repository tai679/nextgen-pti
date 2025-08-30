import json
from PyQt6.QtWidgets import QApplication, QListWidgetItem, QMainWindow, QMessageBox, QFileDialog
from PyQt6.QtGui import QPixmap
from PyQt6.uic import loadUi
import os

class CRUDApp(QMainWindow):
    def __init__(self, home_page):
        super().__init__()
        loadUi("ui/edit.ui", self)
        self.home_page = home_page
        self.data_file = "data/data.json"
        self.data = []
        self.selected_image_path = None

        self.btnBack.clicked.connect(self.return_home)
        self.btnAdd.clicked.connect(self.add_item)
        self.btnUpdate.clicked.connect(self.update_item)
        self.btnDelete.clicked.connect(self.delete_item)
        self.chonhinh.clicked.connect(self.choose_image)

        # Thêm thể loại vào combo box
        self.comboGenre_2.addItems([
            "Hành động", "Kinh dị", "Tình cảm",
            "Hoạt hình", "Khoa học viễn tưởng", "Trinh Thám","hài","hài tâm linh",
            "lịch sử","tài liệu","chiến tranh"
        ])

        # Khi click chọn 1 item trong list hiển thị ra form ấn 2 lần xoá
        self.listWidget.itemClicked.connect(self.load_selected_item)
        self.listWidget.itemDoubleClicked.connect(self.clear_inputs)

        self.load_data()

    def return_home(self):
        self.close()
        self.home_page.load_movies()
        self.home_page.show()

    # Hàm chọn ảnh
    def choose_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn ảnh poster", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.selected_image_path = file_path
            pixmap = QPixmap(file_path).scaled(150, 200)
            self.anhthu.setPixmap(pixmap)
    # lưu mở file để đọc dữ liệu
    def load_data(self):
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = []

        # Hiển thị dữ liệu trong list 
        self.listWidget.clear()
        for item in self.data:
            self.listWidget.addItem(QListWidgetItem(
                f"{item.get('id', '')}: {item.get('tenphim', '')} - {item.get('dao', '')} - {item.get('luotxem', '0')} views" 
                f" - {item.get('thich', '0')} likes"
            ))

        QApplication.processEvents()

    # lưu dữ liệu
    def save_data(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu: {e}")

    def add_item(self):
        movie_data = {
            "id": max([item["id"] for item in self.data], default=0) + 1,
            "txtName": self.txtName.text().strip(),
            "txtReleaseDate": self.txtReleaseDate.text().strip(),
            "rating": self.ratingComboBox.currentIndex() + 1,
            "tenphim": self.tenphim.text().strip(),
            "dao": self.dao.text().strip(),
            "dienvien": self.dienvien.toPlainText().strip(),
            "giai": self.giai.toPlainText().strip(),
            "mota": self.mota.toPlainText().strip(),
            "luotxem": self.luotxem.text().strip(),
            "binhluan": self.binhluan.toPlainText().strip(),
            "thich": self.thich.text().strip(),
            "img": self.selected_image_path if self.selected_image_path else "",
            "theloai": self.comboGenre_2.currentText()
        }

        if not movie_data["tenphim"]:
            return

        self.data.append(movie_data)
        self.save_data()
        self.load_data()
        self.clear_inputs()


    def update_item(self):
        selected = self.listWidget.currentRow()
        if selected == -1:
            return

        inputs = {
            "txtName": self.txtName.text().strip(),
            "txtReleaseDate": self.txtReleaseDate.text().strip(),
            "rating": self.ratingComboBox.currentIndex() + 1,
            "tenphim": self.tenphim.text().strip(),
            "dao": self.dao.text().strip(),
            "dienvien": self.dienvien.toPlainText().strip(),
            "giai": self.giai.toPlainText().strip(),
            "mota": self.mota.toPlainText().strip(),
            "luotxem": self.luotxem.text().strip(),
                "binhluan": self.binhluan.toPlainText().strip(),
            "thich": self.thich.text().strip(),
            "theloai": self.comboGenre_2.currentText()
        }

        for key, value in inputs.items():
            if value or key == "rating": 
                self.data[selected][key] = value

        if self.selected_image_path:
            self.data[selected]["img"] = self.selected_image_path

        self.save_data()
        self.load_data()
        QApplication.processEvents()


    def delete_item(self):
        selected = self.listWidget.currentRow()
        if selected == -1:
            return

        reply = QMessageBox.question(
            self,
            "Xác nhận xoá",
            "Bạn có chắc chắn muốn xoá mục này không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.data.pop(selected)
            self.save_data()
            self.load_data()
            QApplication.processEvents()

    def clear_inputs(self):
        self.tenphim.clear()
        self.txtName.clear()
        self.txtReleaseDate.clear()
        self.txtRating.clear()
        self.dao.clear()
        self.dienvien.clear()
        self.giai.clear()
        self.mota.clear()
        self.luotxem.clear()
        self.binhluan.clear()
        self.thich.clear()
        self.anhthu.clear()
        self.comboGenre_2.setCurrentIndex(0)
        self.ratingComboBox.setCurrentIndex(0)
        self.selected_image_path = None

    def load_selected_item(self):
        """Hiển thị dữ liệu phim đã chọn ra form để chỉnh sửa"""
        selected = self.listWidget.currentRow()
        if selected == -1:
            return

        movie = self.data[selected]

        self.tenphim.setText(movie.get("tenphim", ""))
        self.txtName.setText(movie.get("txtName", ""))
        self.txtReleaseDate.setText(movie.get("txtReleaseDate", ""))
        self.txtRating.setText(movie.get("txtRating", ""))
        self.dao.setText(movie.get("dao", ""))
        self.dienvien.setPlainText(movie.get("dienvien", ""))
        self.giai.setPlainText(movie.get("giai", ""))
        self.mota.setPlainText(movie.get("mota", ""))
        self.luotxem.setText(movie.get("luotxem", ""))
        self.binhluan.setPlainText(movie.get("binhluan", ""))
        self.thich.setText(movie.get("thich", ""))
        self.comboGenre_2.setCurrentText(movie.get("theloai", "Hành động"))

        rating = movie.get("rating", 1)
        self.ratingComboBox.setCurrentIndex(rating - 1)

        # Load ảnh
        img_path = movie.get("img", "")
        if img_path and os.path.exists(img_path):
            pixmap = QPixmap(img_path).scaled(150, 200)
            self.anhthu.setPixmap(pixmap)
            self.selected_image_path = img_path
        else:
            self.anhthu.clear()
            self.selected_image_path = None