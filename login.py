from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.uic import loadUi
import json
from main import Home

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
        username = self.email2.text().strip()
        password = self.matkhau2.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"users": []}

        for user in data["users"]:
            if user["username"] == username:
                QMessageBox.warning(self, "Lỗi", "Tài khoản đã tồn tại!")
                return

        new_user = {
            "username": username,
            "password": password,
            "favorites": []
        }
        data["users"].append(new_user)

        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        QMessageBox.information(self, "Thành công", "Đăng ký thành công! Hãy đăng nhập.")
        self.email2.clear()
        self.matkhau2.clear()
        self.return_to_login()


    def return_to_login(self):
        self.login_page = Login()
        self.login_page.show()
        self.close()