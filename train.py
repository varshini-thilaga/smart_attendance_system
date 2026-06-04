import face_recognition
import os
import pickle
import sqlite3
from datetime import datetime

DATASET_DIR = "dataset"
MODEL_FILE = "trained_model.pkl"

def train():
    known_encodings = []
    known_ids = []

    connect = sqlite3.connect("Face-DataBase")

    for folder in os.listdir(DATASET_DIR):
        folder_path = os.path.join(DATASET_DIR, folder)
        if not os.path.isdir(folder_path):
            continue

        student_id = folder.replace("user", "")

        for filename in os.listdir(folder_path):
            if not filename.endswith(".jpg"):
                continue
            img_path = os.path.join(folder_path, filename)
            image = face_recognition.load_image_file(img_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_encodings.append(encodings[0])
                known_ids.append(student_id)
                print(f"Encoded: {filename}")

    with open(MODEL_FILE, "wb") as f:
        pickle.dump({"encodings": known_encodings, "ids": known_ids}, f)

    # Save training timestamp
    connect.execute("CREATE TABLE IF NOT EXISTS TrainLog (trained_at TEXT)")
    connect.execute("DELETE FROM TrainLog")
    connect.execute("INSERT INTO TrainLog VALUES (?)", (datetime.now().isoformat(),))
    connect.commit()
    connect.close()

    print(f"Training complete. {len(known_encodings)} faces encoded.")

if __name__ == "__main__":
    train()
