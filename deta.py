import sys
import json
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi
import os

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