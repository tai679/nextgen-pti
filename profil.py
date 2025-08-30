import json
from PyQt6.QtWidgets import (
    QMainWindow, QListWidgetItem, QWidget, QVBoxLayout,
    QLabel, QPushButton, QMessageBox,QFileDialog
)
from PyQt6.uic import loadUi
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class UserProfilePage(QMainWindow):
    def __init__(self, username, users_file, data_file):
        super().__init__()
        loadUi("ui/profile.ui", self)
        self.username = username
        self.users_file = users_file
        self.data_file = data_file

        # Nút
        self.btnBack.clicked.connect(self.close)
        self.btnChangePassword.clicked.connect(self.change_password)
        self.btnChangeAvatar.clicked.connect(self.change_avatar)
        self.btnChangeEmail.clicked.connect(self.change_email)
        self.btnDeleteAccount.clicked.connect(self.delete_account)

        self.load_profile()

    def load_profile(self):
        """Load dữ liệu hồ sơ người dùng"""
        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                users_data = json.load(f)
            with open(self.data_file, "r", encoding="utf-8") as f:
                movies_data = json.load(f)
        except Exception as e:
            print("Lỗi:", e)
            return

        self.users_data = users_data
        self.movies_data = movies_data

        user = next((u for u in users_data["users"] if u["username"] == self.username), None)
        if not user:
            return

        # Hiển thị thông tin cơ bản
        self.lblUsername.setText(f"Tên đăng nhập: {self.username}")
        self.lblPassword.setText(f"Mật khẩu: {user.get('password', 'Không rõ')}")
        self.lblFavoriteCount.setText(f"Số phim yêu thích: {len(user.get('favorites', []))}")
        self.txtNewEmail.setText(user.get("email", ""))

        # Hiển thị avatar
        avatar_path = user.get("avatar", "")
        if avatar_path:
            pixmap = QPixmap(avatar_path)
            self.lblAvatar.setPixmap(
                pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )
        else:
            self.lblAvatar.setText("Chưa có avatar")

        # Hiển thị danh sách phim yêu thích
        self.listFavorites.clear()
        for movie_id in user.get("favorites", []):
            movie = next((m for m in movies_data if m["id"] == movie_id), None)
            if movie:
                item_widget = self.create_fav_item(movie)
                item = QListWidgetItem()
                item.setSizeHint(item_widget.sizeHint())
                self.listFavorites.addItem(item)
                self.listFavorites.setItemWidget(item, item_widget)

    def create_fav_item(self, movie):
        """Tạo widget hiển thị phim yêu thích"""
        widget = QWidget()
        layout = QVBoxLayout()

        img = QLabel()
        pixmap = QPixmap(movie.get("img", ""))
        img.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(img)

        layout.addWidget(QLabel(f"{movie.get('tenphim', 'Không rõ')}"))
        layout.addWidget(QLabel(f"Đạo diễn: {movie.get('dao', 'Không rõ')}"))
        rating = movie.get("rating", 0)
        stars = "⭐" * int(rating) if rating else "Chưa có đánh giá"
        layout.addWidget(QLabel(f"Đánh giá: {stars}"))

        btn_detail = QPushButton("Xem chi tiết")
        btn_detail.clicked.connect(lambda _, m=movie: self.open_detail(m))
        layout.addWidget(btn_detail)

        widget.setLayout(layout)
        return widget

    def open_detail(self, movie):
        from deta import DetailPage
        self.detail_page = DetailPage(movie, None, self.data_file)
        self.detail_page.show()

    def change_password(self):
        """Đổi mật khẩu"""
        new_pass = self.txtNewPassword.text().strip()
        if not new_pass:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu mới không được để trống!")
            return

        for user in self.users_data["users"]:
            if user["username"] == self.username:
                user["password"] = new_pass
                break

        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(self.users_data, f, indent=4, ensure_ascii=False)

        QMessageBox.information(self, "Thành công", "Đổi mật khẩu thành công!")
        self.txtNewPassword.clear()

    def change_email(self):
        """Đổi email"""
        new_username = self.txtNewEmail.text().strip()
        if not new_username:
            QMessageBox.warning(self, "Lỗi", "Email mới không được để trống!")
            return

        for user in self.users_data["users"]:
            if user["username"] == self.username:
                user["username"] = new_username
                break

        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(self.users_data, f, indent=4, ensure_ascii=False)

        QMessageBox.information(self, "Thành công", "Đổi email thành công!")
        self.txtNewEmail.clear()

    def change_avatar(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh đại diện", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_name:
        # Cập nhật hiển thị avatar
            pixmap = QPixmap(file_name)
            self.lblAvatar.setPixmap(pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio))

        # Cập nhật dữ liệu người dùng
            with open(self.users_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for user in data["users"]:
                if user["username"] == self.username:
                    user["avatar"] = file_name
                    break

            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
    def delete_account(self):
        """Xóa tài khoản"""
        confirm = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc chắn muốn xóa tài khoản này không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.No:
            return

        self.users_data["users"] = [
            u for u in self.users_data["users"] if u["username"] != self.username
        ]

        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(self.users_data, f, indent=4, ensure_ascii=False)

        QMessageBox.information(self, "Đã xóa", "Tài khoản đã bị xóa!")
        self.close()
