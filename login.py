import sys
import os
import sqlite3
import hashlib

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QStackedWidget, QFrame
)
from PyQt5.QtGui import QFont, QPainter, QLinearGradient, QColor, QBrush, QIcon
from PyQt5.QtCore import Qt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "Face-DataBase")


def init_auth_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS Teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        class_name TEXT NOT NULL
    )""")
    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_login(username, password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        "SELECT id, full_name, class_name FROM Teachers WHERE username=? AND password=?",
        (username, hash_password(password))
    )
    row = cur.fetchone()
    conn.close()
    return row


def register_teacher(username, password, full_name, class_name):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO Teachers(username, password, full_name, class_name) VALUES(?,?,?,?)",
            (username, hash_password(password), full_name, class_name)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


class StyledInput(QLineEdit):
    def __init__(self, placeholder, echo=False):
        super().__init__()
        self.setPlaceholderText(placeholder)
        if echo:
            self.setEchoMode(QLineEdit.Password)
        self.setMinimumHeight(45)
        self.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.08);
                border: 1px solid #2c5364;
                border-radius: 8px;
                color: white;
                padding: 0 14px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #00d4ff;
                background: rgba(255,255,255,0.12);
            }
        """)


class StyledButton(QPushButton):
    def __init__(self, text, color="#1a73e8"):
        super().__init__(text)
        self.setMinimumHeight(45)
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                color: white;
                border-radius: 8px;
                border: none;
            }}
            QPushButton:hover {{
                background: white;
                color: {color};
                border: 2px solid {color};
            }}
        """)


class LoginPage(QWidget):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(14)

        title = QLabel("Welcome Back 👋")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #00d4ff;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("Sign in to your teacher account")
        sub.setStyleSheet("color: #aaaaaa; font-size: 12px;")
        sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub)
        layout.addSpacing(10)

        self.username = StyledInput("Username")
        self.password = StyledInput("Password", echo=True)
        layout.addWidget(QLabel("Username", styleSheet="color:#aaaaaa;"))
        layout.addWidget(self.username)
        layout.addWidget(QLabel("Password", styleSheet="color:#aaaaaa;"))
        layout.addWidget(self.password)
        layout.addSpacing(6)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #e53935; font-size: 11px;")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

        btn = StyledButton("Login")
        btn.clicked.connect(self.do_login)
        layout.addWidget(btn)
        layout.addStretch()

    def do_login(self):
        u = self.username.text().strip()
        p = self.password.text().strip()
        if not u or not p:
            self.error_label.setText("Please enter username and password.")
            return
        result = verify_login(u, p)
        if result:
            self.error_label.setText("")
            self.on_success(result[0], result[1], result[2])
        else:
            self.error_label.setText("❌ Invalid username or password.")


class RegisterPage(QWidget):
    def __init__(self, on_registered):
        super().__init__()
        self.on_registered = on_registered
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 30, 60, 30)
        layout.setSpacing(12)

        title = QLabel("Create Account 🎓")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #00d4ff;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("Register as a class teacher")
        sub.setStyleSheet("color: #aaaaaa; font-size: 12px;")
        sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub)
        layout.addSpacing(6)

        self.full_name = StyledInput("e.g. Mrs. Sharma")
        self.class_name = StyledInput("e.g. Class 10A")
        self.username = StyledInput("Choose a username")
        self.password = StyledInput("Choose a password", echo=True)
        self.confirm = StyledInput("Confirm password", echo=True)

        for label, widget in [
            ("Full Name", self.full_name),
            ("Class Name", self.class_name),
            ("Username", self.username),
            ("Password", self.password),
            ("Confirm Password", self.confirm),
        ]:
            layout.addWidget(QLabel(label, styleSheet="color:#aaaaaa;"))
            layout.addWidget(widget)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #e53935; font-size: 11px;")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

        btn = StyledButton("Register", color="#0f9d58")
        btn.clicked.connect(self.do_register)
        layout.addWidget(btn)
        layout.addStretch()

    def do_register(self):
        fn = self.full_name.text().strip()
        cn = self.class_name.text().strip()
        u = self.username.text().strip()
        p = self.password.text().strip()
        c = self.confirm.text().strip()

        if not all([fn, cn, u, p, c]):
            self.error_label.setText("All fields are required.")
            return
        if p != c:
            self.error_label.setText("Passwords do not match.")
            return
        if len(p) < 6:
            self.error_label.setText("Password must be at least 6 characters.")
            return

        if register_teacher(u, p, fn, cn):
            QMessageBox.information(self, "Success", f"✅ Account created for {fn}!\nYou can now login.")
            self.on_registered()
        else:
            self.error_label.setText("❌ Username already exists. Choose another.")


class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        init_auth_db()
        self.setWindowTitle("AttendEase - Login")
        self.setFixedSize(480, 620)
        self.setWindowIcon(QIcon(os.path.join(BASE_DIR, "home.png")))
        self._build_ui()

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor("#0f2027"))
        gradient.setColorAt(0.5, QColor("#203a43"))
        gradient.setColorAt(1.0, QColor("#2c5364"))
        painter.fillRect(self.rect(), QBrush(gradient))

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # App title
        header = QWidget()
        header.setStyleSheet("background: transparent;")
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(20, 20, 20, 10)

        app_title = QLabel("AttendEase")
        app_title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        app_title.setStyleSheet("color: #00d4ff; letter-spacing: 3px;")
        app_title.setAlignment(Qt.AlignCenter)
        h_layout.addWidget(app_title)

        tagline = QLabel("Smart Attendance Management System")
        tagline.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        tagline.setAlignment(Qt.AlignCenter)
        h_layout.addWidget(tagline)
        main_layout.addWidget(header)

        # Tab buttons
        tab_layout = QHBoxLayout()
        tab_layout.setContentsMargins(40, 10, 40, 0)
        tab_layout.setSpacing(0)

        self.login_tab = QPushButton("Login")
        self.register_tab = QPushButton("Register")
        for btn in [self.login_tab, self.register_tab]:
            btn.setMinimumHeight(38)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFont(QFont("Segoe UI", 11))
        self.login_tab.clicked.connect(lambda: self.switch_tab(0))
        self.register_tab.clicked.connect(lambda: self.switch_tab(1))
        tab_layout.addWidget(self.login_tab)
        tab_layout.addWidget(self.register_tab)
        main_layout.addLayout(tab_layout)

        # Stacked pages
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")
        self.login_page = LoginPage(self.on_login_success)
        self.register_page = RegisterPage(lambda: self.switch_tab(0))
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.register_page)
        main_layout.addWidget(self.stack)

        self.switch_tab(0)

    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        active = "background:#00d4ff; color:#0f2027; font-weight:bold; border:none; border-radius:0;"
        inactive = "background:rgba(255,255,255,0.05); color:#aaaaaa; border:none; border-radius:0;"
        self.login_tab.setStyleSheet(active if index == 0 else inactive)
        self.register_tab.setStyleSheet(active if index == 1 else inactive)

    def on_login_success(self, teacher_id, full_name, class_name):
        from layout_main import MainWindow
        self.main_window = MainWindow(teacher_id, full_name, class_name)
        self.main_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AuthWindow()
    window.show()
    sys.exit(app.exec())
