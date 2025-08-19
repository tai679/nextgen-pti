import sys
import json
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QMainWindow, QWidget, QMessageBox, QFileDialog
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi

class Login(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("ui/dangnhap.ui", self)
        self.data_file = "data/users.json"
        self.btnLogin.clicked.connect(self.login)
        self.btndangky.clicked.connect(self.open_dangky)

    def login(self):
        username = self.email2.text().strip()
        password = self.matkhau2.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                users = json.load(f)["users"]
        except (FileNotFoundError, json.JSONDecodeError):
            users = []

        for user in users:
            if user["username"] == username and user["password"] == password:
                self.open_home(username)
                return

        QMessageBox.warning(self, "Lỗi", "Sai tài khoản hoặc mật khẩu!")

    def open_home(self, username):
        self.home_page = Home(username)
        self.home_page.show()
        self.close()

    def open_dangky(self):
        self.dangky_page = dangky()
        self.dangky_page.show()
        self.close()

class dangky(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("ui/dangky.ui", self)
        self.data_file = "data/users.json"
        self.btndangky.clicked.connect(self.dangky_user)
        self.btnback.clicked.connect(self.return_to_login)

    def dangky_user(self):
        user = {
            "username": self.email2.text().strip(),
            "password": self.matkhau2.text().strip(),
            "favorites": []
        }

        if not user["username"] or not user["password"]:
            return

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"users": []}

        data["users"].append(user)

        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        self.email2.clear()
        self.matkhau2.clear()
        self.return_to_login()

    def return_to_login(self):
        self.login_page = Login()
        self.login_page.show()
        self.close()

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
        self.thoatrabtn.clicked.connect(self.close)  
        self.btnFavorites.clicked.connect(self.open_favorites)
        self.btnSearch.clicked.connect(self.search_movies)
        self.hoi.clicked.connect(self.open_hoi)

        self.comboGenreFilter.addItem("Tất cả")  # để chọn xem tất cả
        self.comboGenreFilter.addItems([
            "Hành động", "Kinh dị", "Tình cảm", 
            "Hoạt hình", "Khoa học viễn tưởng"
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

        filtered = [m for m in self.all_movies if keyword in m["tenphim"].lower()]
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
        layout.addWidget(QLabel(f"<b style='color:orange;'>Lượt xem: {movie.get('luotxem', 0)}</b>"))

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

            self.load_movies()  # Refresh để đổi nút

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    def open_detail(self, movie):
        self.detail_page = DetailPage(movie, self.all_movies, self.data_file)
        self.detail_page.show()

    def open_crud(self):
        self.crud_page = CRUDApp(self)
        self.crud_page.show()
        self.close()

    def open_favorites(self):
        self.fav_page = FavoritePage(self.username, self.users_file, self.data_file)
        self.fav_page.show()

    def open_hoi(self):
        self.hoi_page = hoiPage()
        self.hoi_page.show()

class hoiPage(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("ui/gioithieu.ui", self)
        self.btnBack.clicked.connect(self.close)

       
class FavoritePage(QMainWindow):
    def __init__(self, username, users_file, data_file):
        super().__init__()
        loadUi("ui/favorite.ui", self)
        self.data_file = "data/data.json"
        self.users_file = "data/users.json"
        self.username = username
        self.btnBack.clicked.connect(self.close)
        self.load_favorites()

    def open_detail(self, movie):
        with open("data/data.json", "r", encoding="utf-8") as f:
            all_movies = json.load(f)
        self.detail_page = DetailPage(movie, all_movies, "data.json")
        self.detail_page.show()


    def load_favorites(self):
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                all_movies = json.load(f)
            with open(self.users_file, "r", encoding="utf-8") as f:
                users = json.load(f)["users"]
        except:
            all_movies = []
            users = []

        user = next((u for u in users if u["username"] == self.username), None)
        if not user:
            return

        favorite_ids = user.get("favorites", [])
        favorite_movies = [m for m in all_movies if m["id"] in favorite_ids]

        self.listWidget.clear()
        for movie in favorite_movies:
            item_widget = self.create_fav_item(movie)
            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, item_widget)

    def create_fav_item(self, movie):
        item_widget = QWidget()
        layout = QVBoxLayout()

        img_label = QLabel()
        pixmap = QPixmap(movie["img"])
        img_label.setPixmap(pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(img_label)

        layout.addWidget(QLabel(f"<b style='color:red;'>ID: {movie['id']}</b>"))
        layout.addWidget(QLabel(f"<b>{movie['tenphim']}</b>"))
        layout.addWidget(QLabel(f"dao: {movie['dao']}"))
        layout.addWidget(QLabel(f"<b style='color:orange;'>luotxem: {movie['luotxem']}</b>"))

        btn_detail = QPushButton("Xem chi tiết")
        btn_detail.clicked.connect(lambda _, m=movie: self.open_detail(m))
        layout.addWidget(btn_detail)

        item_widget.setLayout(layout)
        return item_widget

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
            "Hoạt hình", "Khoa học viễn tưởng"
        ])

        self.load_data()

    def return_home(self):
        self.close()
        self.home_page.load_movies()
        self.home_page.show()

    def choose_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn ảnh poster", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.selected_image_path = file_path
            pixmap = QPixmap(file_path).scaled(150, 200)
            self.anhthu.setPixmap(pixmap)

    def load_data(self):
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = []

        self.listWidget.clear()
        for item in self.data:
            self.listWidget.addItem(QListWidgetItem(
                f"{item.get('id', '')}: {item.get('tenphim', '')} - {item.get('dao', '')} - {item.get('luotxem', '0')} views"
            ))

        QApplication.processEvents()

    def save_data(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu: {e}")

    def add_item(self):
        movie_data = {
            "id": max([item["id"] for item in self.data], default=0) + 1,
            "tenphim": self.tenphim.text().strip(),
            "dao": self.dao.text().strip(),
            "dienvien": self.dienvien.toPlainText().strip(),
            "giai": self.giai.toPlainText().strip(),
            "mota": self.mota.toPlainText().strip(),
            "luotxem": self.luotxem.text().strip(),
            "binhluan": self.binhluan.toPlainText().strip(),
            "thich": self.thich.text().strip(),
            "img": self.selected_image_path if self.selected_image_path else "",
            "theloai": self.comboGenre_2.currentText()  # << thêm thể loại
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

        self.data[selected]["tenphim"] = self.tenphim.text().strip()
        self.data[selected]["dao"] = self.dao.text().strip()
        self.data[selected]["dienvien"] = self.dienvien.toPlainText().strip()
        self.data[selected]["giai"] = self.giai.toPlainText().strip()
        self.data[selected]["mota"] = self.mota.toPlainText().strip()
        self.data[selected]["luotxem"] = self.luotxem.text().strip()
        self.data[selected]["binhluan"] = self.binhluan.toPlainText().strip()
        self.data[selected]["thich"] = self.thich.text().strip()
        if self.selected_image_path:
            self.data[selected]["img"] = self.selected_image_path

        # Cập nhật thể loại
        self.data[selected]["theloai"] = self.comboGenre_2.currentText()

        self.save_data()
        self.load_data()
        QApplication.processEvents()
        self.clear_inputs()

    def delete_item(self):
        selected = self.listWidget.currentRow()
        if selected == -1:
            return

        self.data.pop(selected)
        self.save_data()
        self.load_data()
        QApplication.processEvents()

    def clear_inputs(self):
        self.tenphim.clear()
        self.dao.clear()
        self.dienvien.clear()
        self.giai.clear()
        self.mota.clear()
        self.luotxem.clear()
        self.binhluan.clear()
        self.thich.clear()
        self.anhthu.clear()
        self.comboGenre_2.setCurrentIndex(0)  # reset về thể loại đầu
        self.selected_image_path = None


class DetailPage(QMainWindow):
    def __init__(self, movie, all_movies, data_file):
        super().__init__()
        loadUi("ui/detail.ui", self)

        self.movie = movie
        self.all_movies = all_movies
        self.data_file = data_file

        self.tenphim.setText(movie.get("tenphim", ""))
        self.dao.setText(movie.get("dao", ""))
        self.dienvien.setPlainText(movie.get("dienvien", ""))
        self.giai.setPlainText(movie.get("giai", ""))
        self.mota.setPlainText(movie.get("mota", ""))
        self.luotxem.setText(movie.get("luotxem", "0"))
        self.thich.setText(movie.get("thich", "0"))
        self.binhluan.setPlainText(movie.get("binhluan", ""))

        img_path = movie.get("img", "")
        if img_path:
            self.img.setPixmap(QPixmap(img_path))

        self.btnSave.clicked.connect(self.save_changes)

    def save_changes(self):
        self.movie["tenphim"] = self.tenphim.text().strip()
        self.movie["dao"] = self.dao.text().strip()
        self.movie["dienvien"] = self.dienvien.toPlainText().strip()
        self.movie["giai"] = self.giai.toPlainText().strip()
        self.movie["mota"] = self.mota.toPlainText().strip()
        self.movie["luotxem"] = self.luotxem.text().strip()
        self.movie["thich"] = self.thich.text().strip()
        self.movie["binhluan"] = self.binhluan.toPlainText().strip()

        for i, m in enumerate(self.all_movies):
            if m["id"] == self.movie["id"]:
                self.all_movies[i] = self.movie
                break

        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.all_movies, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "Thành công", "Đã lưu thông tin phim!")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Lỗi khi lưu dữ liệu: {e}")

   
if __name__ == "__main__":
    app = QApplication(sys.argv)
    loginPage = Login()
    loginPage.show()
    sys.exit(app.exec())