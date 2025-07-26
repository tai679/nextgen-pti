import sys
import json
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QMainWindow, QWidget, QMessageBox
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
        self.load_movies()
        self.quanlybtn.clicked.connect(self.open_crud)
        self.thoatrabtn.clicked.connect(self.close)
        self.btnFavorites.clicked.connect(self.open_favorites)

    def load_movies(self):
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                movies = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            movies = []

        self.listWidget.clear()
        for movie in movies:
            item_widget = self.create_movies_item(movie)
            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, item_widget)

    def create_movies_item(self, movie):
        item_widget = QWidget()
        layout = QVBoxLayout()

        img_label = QLabel()
        pixmap = QPixmap(movie["img"])
        img_label.setPixmap(pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(img_label)

        layout.addWidget(QLabel(f"<b style='color:red;'>ID: {movie['id']}</b>"))
        layout.addWidget(QLabel(f"<b>{movie['name']}</b>"))
        layout.addWidget(QLabel(f"Release Date: {movie['release_date']}"))
        layout.addWidget(QLabel(f"<b style='color:orange;'>Rating: {movie['rating']}</b>"))

        btn_fav = QPushButton("thêm vào Yêu thích")
        btn_fav.clicked.connect(lambda _, movie_id=movie["id"]: self.add_to_favorites(movie_id))
        layout.addWidget(btn_fav)

        btn_detail = QPushButton("Chi tiết")
        btn_detail.clicked.connect(lambda _, movie_id=movie["id"]: self.open_detail(movie))
        layout.addWidget(btn_detail)

        item_widget.setLayout(layout)
        return item_widget
    
    def open_detail(self, movie):
        self.detail_page = DetailPage( movie)
        self.detail_page.show()
        
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

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    def open_crud(self):
        self.crud_page = CRUDApp(self)
        self.crud_page.show()
        self.close()

    def open_favorites(self):
        self.fav_page = FavoritePage(self.username)
        self.fav_page.show()

class FavoritePage(QMainWindow):
    def __init__(self, username):
        super().__init__()
        loadUi("ui/favorite.ui", self)
        self.data_file = "data/data.json"
        self.users_file = "data/users.json"
        self.username = username
        self.btnBack.clicked.connect(self.close)
        self.load_favorites()

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
        layout.addWidget(QLabel(f"<b>{movie['name']}</b>"))
        layout.addWidget(QLabel(f"Release Date: {movie['release_date']}"))
        layout.addWidget(QLabel(f"<b style='color:orange;'>Rating: {movie['rating']}</b>"))

        item_widget.setLayout(layout)
        return item_widget

class CRUDApp(QMainWindow):
    def __init__(self, home_page):
        super().__init__()
        loadUi("ui/edit.ui", self)
        self.home_page = home_page
        self.data_file = "data/data.json"
        self.data = []

        self.btnBack.clicked.connect(self.return_home)
        self.btnAdd.clicked.connect(self.add_item)
        self.btnUpdate.clicked.connect(self.update_item)
        self.btnDelete.clicked.connect(self.delete_item)

        self.load_data()

    def return_home(self):
        self.close()
        self.home_page.load_movies()
        self.home_page.show()

    def load_data(self):
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = []

        self.listWidget.clear()
        for item in self.data:
            self.listWidget.addItem(QListWidgetItem(f"{item['id']}: {item['name']} - {item['release_date']} - Rating: {item['rating']}"))

        QApplication.processEvents()

    def save_data(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu: {e}")

    def add_item(self):
        name = self.txtName.text().strip()
        release_date = self.txtReleaseDate.text().strip()
        rating = self.txtRating.text().strip()
        img = self.txtLabel.text().strip()

        if not name or not release_date or not rating or not img:
            return

        new_id = max([item["id"] for item in self.data], default=0) + 1
        self.data.append({"id": new_id, "name": name, "release_date": release_date, "rating": rating, "download_link": "", "img": img})

        self.save_data()
        self.load_data()

        self.txtName.clear()
        self.txtReleaseDate.clear()
        self.txtRating.clear()
        self.txtLabel.clear()

    def update_item(self):
        selected = self.listWidget.currentRow()
        if selected == -1:
            return

        self.data[selected]["name"] = self.txtName.text().strip()
        self.data[selected]["release_date"] = self.txtReleaseDate.text().strip()
        self.data[selected]["rating"] = self.txtRating.text().strip()
        self.data[selected]["img"] = self.txtLabel.text().strip()

        self.save_data()
        self.load_data()
        QApplication.processEvents()

    def delete_item(self):
        selected = self.listWidget.currentRow()
        if selected == -1:
            return

        self.data.pop(selected)
        self.save_data()
        self.load_data()
        QApplication.processEvents()
class DetailPage(QMainWindow):
    def __init__(self, movie):
        super().__init__()
        self.ui = loadUi("ui/detail.ui", self)
    
        self.tieude.setText(movie["name"])
        self.nam.setText(movie["nam"])
        self.gioi.setText(movie["gioi"])
        self.xem.setText(movie["xem"])
        self.thich.setText(movie["thich"])
        self.binhluan.setText(movie["binhluan"])
        self.img.setPixmap(QPixmap(movie["img"]))
        self.mota.setPlainText(movie["mota"])

        
   
if __name__ == "__main__":
    app = QApplication(sys.argv)
    loginPage = Login()
    loginPage.show()
    sys.exit(app.exec())