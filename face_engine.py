"""
face_engine.py  —  OpenCV-only face recognition (LBPH + Haar cascade).
No dlib, no face_recognition library required.
"""
import cv2
import numpy as np
import json
import os
import shutil

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.path.join(BASE_DIR, "data")

# Haar cascade bundled with OpenCV
_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
_detector     = cv2.CascadeClassifier(_CASCADE_PATH)


# ── Path helpers ──────────────────────────────────────────────────────
def _safe(s):
    return str(s).replace(" ", "_").replace("/", "-")


def get_paths(year, class_name, section):
    base = os.path.join(DATA_ROOT, _safe(year), f"{_safe(class_name)}_{_safe(section)}")
    paths = {
        "dataset": os.path.join(base, "dataset"),
        "model":   os.path.join(base, "model"),
        "photos":  os.path.join(base, "photos"),
        "excel":   os.path.join(base, "excel"),
    }
    for p in paths.values():
        os.makedirs(p, exist_ok=True)
    return paths


def model_xml(year, class_name, section):
    return os.path.join(get_paths(year, class_name, section)["model"], "model.xml")

def model_map(year, class_name, section):
    return os.path.join(get_paths(year, class_name, section)["model"], "id_map.json")


def photos_dir(year, class_name, section):
    return get_paths(year, class_name, section)["photos"]


def excel_file(year, class_name, section):
    return os.path.join(
        get_paths(year, class_name, section)["excel"],
        f"{_safe(class_name)}_{_safe(section)}_{year}.xlsx"
    )


def cropped_dir():
    p = os.path.join(BASE_DIR, "Cropped_faces")
    os.makedirs(p, exist_ok=True)
    return p


# ── Internal helpers ──────────────────────────────────────────────────
def _read_gray(path):
    """Read image as grayscale, handling unicode paths on Windows."""
    arr = np.fromfile(path, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return None
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def _detect_faces(gray):
    """Return list of (x,y,w,h) face rects, trying two scale passes."""
    faces = _detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
    if len(faces) == 0:
        faces = _detector.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3, minSize=(40, 40))
    return faces if len(faces) > 0 else []


# ── Train ─────────────────────────────────────────────────────────────
def train_model(year, class_name, section):
    """
    Build an LBPH model from enrolled student images.
    Saves model.pkl containing the serialised LBPH recogniser + id map.
    Returns number of face samples trained.
    """
    ds = get_paths(year, class_name, section)["dataset"]
    faces, labels, id_map = [], [], {}   # id_map: int_label → student_id_str

    label_counter = 0
    for folder in sorted(os.listdir(ds)):
        fp = os.path.join(ds, folder)
        if not os.path.isdir(fp):
            continue
        sid = folder.replace("student_", "")
        int_label = label_counter
        id_map[int_label] = sid
        label_counter += 1

        for fn in os.listdir(fp):
            if not fn.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            gray = _read_gray(os.path.join(fp, fn))
            if gray is None:
                continue
            rects = _detect_faces(gray)
            for (x, y, w, h) in rects:
                roi = cv2.resize(gray[y:y+h, x:x+w], (100, 100))
                faces.append(roi)
                labels.append(int_label)

    if not faces:
        print("No face samples found — check dataset folder.")
        return 0

    recognizer = cv2.face.LBPHFaceRecognizer_create(
        radius=1, neighbors=8, grid_x=8, grid_y=8, threshold=80.0
    )
    recognizer.train(faces, np.array(labels))

    xml = model_xml(year, class_name, section)
    jmap = model_map(year, class_name, section)
    recognizer.save(xml)
    with open(jmap, "w") as f:
        json.dump(id_map, f)

    print(f"Trained {len(faces)} samples, {len(id_map)} students → {xml}")
    return len(faces)


# ── Save student images ───────────────────────────────────────────────
def save_student_images(student_id, year, class_name, section, file_list):
    folder = os.path.join(
        get_paths(year, class_name, section)["dataset"],
        f"student_{student_id}"
    )
    os.makedirs(folder, exist_ok=True)
    existing = len([f for f in os.listdir(folder) if f.endswith(".jpg")])
    saved = 0
    for i, fs in enumerate(file_list):
        if fs and getattr(fs, "filename", None):
            fs.save(os.path.join(folder, f"img_{existing+i+1}.jpg"))
            saved += 1
    return saved


def save_image_bytes(student_id, year, class_name, section, img_bytes, idx):
    folder = os.path.join(
        get_paths(year, class_name, section)["dataset"],
        f"student_{student_id}"
    )
    os.makedirs(folder, exist_ok=True)
    existing = len([f for f in os.listdir(folder) if f.endswith(".jpg")])
    path = os.path.join(folder, f"img_{existing+idx+1}.jpg")
    with open(path, "wb") as f:
        f.write(img_bytes)
    return path


# ── Save attendance photo ─────────────────────────────────────────────
def save_attendance_photo(image_path, year, class_name, section, date_str, session_type):
    pd = photos_dir(year, class_name, section)
    dest = os.path.join(pd, f"{date_str}_{session_type}.jpg")
    shutil.copy2(image_path, dest)
    return dest


# ── Detect & identify ─────────────────────────────────────────────────
def detect_and_identify(image_path, year, class_name, section):
    """
    Returns (present_ids, num_detected, error_str_or_None).
    present_ids — list of student_id strings recognised as present.
    """
    xml = model_xml(year, class_name, section)
    jmap = model_map(year, class_name, section)
    if not os.path.exists(xml) or not os.path.exists(jmap):
        return [], 0, "Model not trained yet."

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(xml)
    with open(jmap) as f:
        id_map = {int(k): v for k, v in json.load(f).items()}

    if not id_map:
        return [], 0, "No face data in model. Re-enroll students and retrain."

    # Read & upscale if small
    arr = np.fromfile(image_path, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return [], 0, "Cannot read image."

    h, w = img.shape[:2]
    if w < 800:
        img = cv2.resize(img, (800, int(h * 800 / w)))

    gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = _detect_faces(gray)

    # Clear cropped faces folder
    cd = cropped_dir()
    for fn in os.listdir(cd):
        os.remove(os.path.join(cd, fn))

    present_ids = set()
    for i, (x, y, w_r, h_r) in enumerate(rects):
        roi = cv2.resize(gray[y:y+h_r, x:x+w_r], (100, 100))
        cv2.imwrite(os.path.join(cd, f"face_{i+1}.jpg"), roi)
        try:
            label, confidence = recognizer.predict(roi)
            print(f"Face {i+1}: label={label} conf={confidence:.1f}")
            # Lower confidence = better match in LBPH
            if confidence < 80:
                sid = id_map.get(label)
                if sid:
                    present_ids.add(str(sid))
        except Exception as e:
            print(f"Face {i+1} predict error: {e}")

    return list(present_ids), len(rects), None
