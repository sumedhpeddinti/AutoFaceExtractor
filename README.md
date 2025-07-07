# AutoFaceExtractor
A Python desktop tool to automatically extract faces from images inside PDF files. Ideal for generating passport, Aadhaar, or custom-sized ID photos.
---
## Features
Detects faces inside PDF images using AI (face_recognition library)
Auto-crops faces with adjustable padding
Supports standard sizes: Passport, Aadhaar, Stamp, or fully Custom sizes
Preview mode: Review each face, skip unwanted ones
Fast mode: Batch extract without preview for speed
Estimated time remaining display
Final summary of saved/skipped faces

---
## Requirements

- Python 3.8+
- Install dependencies:
(also remember you need dlib wheel for face_recognition)
```bash
pip install PyMuPDF pillow face_recognition numpy (also you need dlib wheel for face_recognition)
pip install cmake
pip install dlib
```

A GUI window will open where you:

1. Select a PDF file
2. Choose output folder
3. Pick standard size or enter custom dimensions
4. Set padding and image format
5. Choose preview mode (full, none, first-only)
6. Start extraction

---

## Output

Cropped face images will be saved in your chosen folder, named by page, image, and face number.

Example:
```
page1_img2_face1.png
page1_img2_face2.png
```

---

## Note

- Works only with PDFs containing embedded images
- GUI-based (requires graphical interface)
- Designed for **offline**, personal use
