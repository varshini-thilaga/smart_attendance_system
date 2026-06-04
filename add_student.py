import cv2
import numpy as np
import sqlite3
import os
import shutil
from PyQt5.QtWidgets import QApplication, QFileDialog
import sys

def insertOrUpdate(Id, Name, roll):
    connect = sqlite3.connect("Face-DataBase")
    cmd = "SELECT * FROM Students WHERE ID = " + str(Id)
    cursor = connect.execute(cmd)
    isRecordExist = False
    for row in cursor:
        isRecordExist = True

    if isRecordExist:
        connect.execute("UPDATE Students SET Name = ? WHERE ID = ?", (Name, Id))
        connect.execute("UPDATE Students SET Roll = ? WHERE ID = ?", (roll, Id))
    else:
        params = (Id, Name, roll)
        connect.execute("INSERT INTO Students(ID, Name, Roll) VALUES(?, ?, ?)", params)
    connect.commit()
    connect.close()


def init_db():
    connect = sqlite3.connect("Face-DataBase")
    connect.execute("""CREATE TABLE IF NOT EXISTS Students (
        ID INTEGER PRIMARY KEY,
        Name TEXT,
        Roll TEXT,
        personID TEXT
    )""")
    connect.commit()
    connect.close()


if __name__ == "__main__":
    init_db()

    name = sys.argv[1] if len(sys.argv) > 1 else input("Enter student's name: ")
    roll = sys.argv[2] if len(sys.argv) > 2 else input("Enter student's Roll Number: ")
    Id = roll[-3:]

    insertOrUpdate(Id, name, roll)

    folderPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dataset", "user" + Id)
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)

    # Use file dialog to select images instead of webcam
    app = QApplication(sys.argv)
    files, _ = QFileDialog.getOpenFileNames(None, "Select Student Face Images (select multiple)", "", "Images (*.jpg *.jpeg *.png)")
    app.quit()

    if not files:
        print("No images selected.")
        sys.exit()

    for i, f in enumerate(files[:20]):
        dest = os.path.join(folderPath, f"User.{Id}.{i+1}.jpg")
        img = cv2.imread(f)
        cv2.imwrite(dest, img)
        print(f"Saved image {i+1}")

    print(f"Enrolled {min(len(files), 20)} images for {name}")
