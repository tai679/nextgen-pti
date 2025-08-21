import sys
import json
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QMainWindow, QWidget, QMessageBox, QFileDialog
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi
from deta import DetailPage
import os

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