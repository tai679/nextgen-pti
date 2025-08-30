import json
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QListWidgetItem, QMainWindow, QWidget, QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi

class Home(QMainWindow):
    def __init__(self, username):
        super().__init__()
        loadUi("ui/home.ui", self)
        self.data_file = "data/data.json"
        self.users_file = "data/users.json"
        self.username = username

        self.all_movies = []
        self.load_movies()

        self.quanlybtn.clicked.connect(self.open_crud)
        self.thoatrabtn.clicked.connect(self.return_to_login)  
        self.btnFavorites.clicked.connect(self.open_favorites)
        self.btnProfile.clicked.connect(self.open_profil)
        self.btnSearch.clicked.connect(self.search_movies)
        self.hoi.clicked.connect(self.open_hoi)

        self.comboGenreFilter.addItem("Tất cả")
        self.comboGenreFilter.addItems([
            "Hành động", "Kinh dị", "Tình cảm", 
            "Hoạt hình", "Khoa học viễn tưởng","trinh thám","hài","hài tâm linh",
            "lịch sử","tài liệu","chiến tranh"
        ])
        self.comboGenreFilter.currentIndexChanged.connect(self.filter_by_category)

    def filter_by_category(self):
        selected = self.comboGenreFilter.currentText()
        if selected == "Tất cả":
            self.display_movies(self.all_movies)
        else:
            filtered = [m for m in self.all_movies if m.get("theloai") == selected]
            self.display_movies(filtered)

    def load_movies(self):
        """Load toàn bộ phim từ file JSON và hiển thị"""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.all_movies = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.all_movies = []

        self.display_movies(self.all_movies)

    def display_movies(self, movies):
        """Hiển thị danh sách phim ra listWidget"""
        self.listWidget.clear()
        for movie in movies:
            item_widget = self.create_movies_item(movie)
            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, item_widget)

    def search_movies(self):
        """Lọc phim theo tên"""
        keyword = self.txtSearch.text().strip().lower()
        if not keyword:
            self.display_movies(self.all_movies)
            return

        filtered = [
            m for m in self.all_movies 
            if keyword in m["tenphim"].lower()
            or keyword in m["dao"].lower()
            or keyword in m["txtReleaseDate"].lower()
        ]
        self.display_movies(filtered)

    def create_movies_item(self, movie):
        """Tạo widget hiển thị 1 phim với nút Thêm/Xóa yêu thích"""
        item_widget = QWidget()
        layout = QVBoxLayout()

        img_label = QLabel()
        pixmap = QPixmap(movie.get("img", ""))
        img_label.setPixmap(pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(img_label)

        layout.addWidget(QLabel(f"<b style='color:red;'>ID: {movie.get('id', '')}</b>"))
        layout.addWidget(QLabel(f"<b>{movie.get('tenphim', 'Không rõ')}</b>"))
        layout.addWidget(QLabel(f"Đạo diễn: {movie.get('dao', 'Không rõ')}"))
        layout.addWidget(QLabel(f"Ngày phát hành: {movie.get('txtReleaseDate', 'Không rõ')}"))
        layout.addWidget(QLabel(f"<b style='color:orange;'>Lượt xem: {movie.get('luotxem', 0)}</b>"))
        rating = movie.get("rating", 0)
        stars = "⭐" * int(rating) if rating else "Chưa có đánh giá"
        layout.addWidget(QLabel(f"Đánh giá: {stars}"))

        # Kiểm tra phim đã trong favorites chưa
        in_favorites = False
        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for user in data["users"]:
                if user["username"] == self.username:
                    if movie.get("id") in user.get("favorites", []):
                        in_favorites = True
                    break
        except:
            pass

        if in_favorites:
            btn_fav = QPushButton("Xóa khỏi Yêu thích")
            btn_fav.clicked.connect(lambda _, movie_id=movie.get("id", None): self.remove_from_favorites(movie_id))
        else:
            btn_fav = QPushButton("Thêm vào Yêu thích")
            btn_fav.clicked.connect(lambda _, movie_id=movie.get("id", None): self.add_to_favorites(movie_id))

        layout.addWidget(btn_fav)

        btn_detail = QPushButton("Chi tiết")
        btn_detail.clicked.connect(lambda _, movie_data=movie: self.open_detail(movie_data))
        layout.addWidget(btn_detail)

        item_widget.setLayout(layout)
        return item_widget


    def add_to_favorites(self, movie_id):
        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for user in data["users"]:
                if user["username"] == self.username:
                    if "favorites" not in user:
                        user["favorites"] = []
                    if movie_id not in user["favorites"]:
                        user["favorites"].append(movie_id)
                        QMessageBox.information(self, "Thông báo", "Đã thêm vào yêu thích!")
                    else:
                        QMessageBox.information(self, "Thông báo", "Phim đã có trong yêu thích!")
                    break

            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            self.load_movies()  # Refresh để đổi nút

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    def remove_from_favorites(self, movie_id):
        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for user in data["users"]:
                if user["username"] == self.username:
                    if movie_id in user.get("favorites", []):
                        user["favorites"].remove(movie_id)
                        QMessageBox.information(self, "Thông báo", "Đã xóa khỏi yêu thích!")
                    else:
                        QMessageBox.information(self, "Thông báo", "Phim không có trong yêu thích!")
                    break

            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            self.load_movies()

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    def return_to_login(self):
        from login import Login
        self.login_page = Login()
        self.login_page.show()
        self.close()

    def open_profil(self):
        from profil import UserProfilePage
        self.profil_page = UserProfilePage(self.username, self.users_file, self.data_file)
        self.profil_page.show()


    def open_hoi(self):
        self.hoi_page = hoiPage()
        self.hoi_page.show()

    def open_detail(self, movie):
        from deta import DetailPage   # import ngay khi cần
        self.detail_page = DetailPage(movie, self.all_movies, self.data_file)
        self.detail_page.show()

    def open_crud(self):
        from edit import CRUDApp
        self.crud_page = CRUDApp(self)
        self.crud_page.show()
        self.close()

    def open_favorites(self):
        from fav import FavoritePage
        self.fav_page = FavoritePage(self.username, self.users_file, self.data_file, self)
        self.fav_page.show()
        self.close()


class hoiPage(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("ui/gioithieu.ui", self)
        self.btnBack.clicked.connect(self.close)