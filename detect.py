import cv2
import dlib
import os
import sys
from PyQt5.QtWidgets import QApplication, QFileDialog

detector = dlib.get_frontal_face_detector()

app = QApplication(sys.argv)
file, _ = QFileDialog.getOpenFileName(None, "Select Class Photo", "", "Images (*.jpg *.jpeg *.png)")
app.quit()

if not file:
    print("No image selected.")
    sys.exit()

if not os.path.exists('./pics'):
    os.makedirs('./pics')

img_src = cv2.imread(file)
cv2.imwrite('./pics/framee1.jpg', img_src)

img = cv2.imread('./pics/framee1.jpg')
dets = detector(img, 1)

if not os.path.exists('./Cropped_faces'):
    os.makedirs('./Cropped_faces')

# Clear previous cropped faces
for f in os.listdir('./Cropped_faces'):
    os.remove(os.path.join('./Cropped_faces', f))

print(f"Detected {len(dets)} faces")
for i, d in enumerate(dets):
    cv2.imwrite(f'./Cropped_faces/face{i+1}.jpg', img[d.top():d.bottom(), d.left():d.right()])
