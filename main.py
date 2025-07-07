import fitz 
from PIL import Image, ImageTk
import io
import os
import face_recognition
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time

STD_SIZES = {
    "Passport (413x531)": (413, 531),
    "Stamp (100x100)": (100, 100),
    "Aadhaar (300x400)": (300, 400),
    "Custom": None
}

ss = (413, 531)  # Selected Size
pd = 50       # Padding
sf = "PNG"      # Save Format
pf = ""     # PDF File Path
od = ""     # Output Dir
pm = "full"     # Preview Mode
scf = False    # Skip Current Face
fps = False     # First Preview Shown

# Counters
tf = 0     # Total Faces
fs = 0    # Faces Saved
fsk = 0   # Faces Skipped

# GUI

def get_inputs():
    def browse():
        global pf
        f = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if f:
            pf = f
            flbl.config(text=f)

    def apply(md):
        global ss, pd, sf, pm, od

        if not pf:
            messagebox.showerror("Err", "Pick a PDF file")
            return

        od = filedialog.askdirectory(title="Output Folder")
        if not od:
            messagebox.showerror("Err", "Pick output folder")
            return

        sz = szv.get()

        if sz == "Custom":
            try:
                w = int(cw.get())
                h = int(ch.get())
                ss = (w, h)
            except:
                messagebox.showerror("Err", "Bad custom size")
                return
        else:
            ss = STD_SIZES[sz]

        try:
            pd = int(pad.get())
        except:
            messagebox.showerror("Err", "Bad padding")
            return

        sf = fmt.get()
        pm = md
        root.destroy()

    root = tk.Tk()
    root.title("Face Cropper")

    ttk.Button(root, text="PDF File", command=browse).grid(row=0, column=0, pady=5)
    flbl = ttk.Label(root, text="No file")
    flbl.grid(row=0, column=1)

    ttk.Label(root, text="Size:").grid(row=1, column=0, sticky="w")
    szv = tk.StringVar(value="Passport (413x531)")
    szm = ttk.Combobox(root, textvariable=szv, values=list(STD_SIZES.keys()), state="readonly")
    szm.grid(row=1, column=1)

    ttk.Label(root, text="Custom W:").grid(row=2, column=0, sticky="w")
    cw = tk.Entry(root)
    cw.grid(row=2, column=1)

    ttk.Label(root, text="Custom H:").grid(row=3, column=0, sticky="w")
    ch = tk.Entry(root)
    ch.grid(row=3, column=1)

    ttk.Label(root, text="Padding:").grid(row=4, column=0, sticky="w")
    pad = tk.Entry(root)
    pad.insert(0, "50")
    pad.grid(row=4, column=1)

    ttk.Label(root, text="Format:").grid(row=5, column=0, sticky="w")
    fmt = tk.StringVar(value="PNG")
    fmtm = ttk.Combobox(root, textvariable=fmt, values=["PNG", "JPEG"], state="readonly")
    fmtm.grid(row=5, column=1)

    ttk.Label(root, text="Mode:").grid(row=6, column=0, pady=(10, 0))

    ttk.Button(root, text="Preview All", command=lambda: apply("full")).grid(row=7, column=0)
    ttk.Button(root, text="Fast (No Preview)", command=lambda: apply("none")).grid(row=7, column=1)
    ttk.Button(root, text="1st Preview", command=lambda: apply("first")).grid(row=8, column=0, columnspan=2)

    root.mainloop()

# Preview

def show_preview(img):
    global scf
    scf = False

    win = tk.Toplevel()
    win.title("Preview")

    rimg = img.resize((200, 200))
    tkimg = ImageTk.PhotoImage(rimg)
    lbl = tk.Label(win, image=tkimg)
    lbl.image = tkimg
    lbl.pack()

    def save(): win.destroy()
    def skip():
        global scf
        scf = True
        win.destroy()

    btns = ttk.Frame(win)
    btns.pack(pady=5)

    ttk.Button(btns, text="Save", command=save).grid(row=0, column=0, padx=5)
    ttk.Button(btns, text="Skip", command=skip).grid(row=0, column=1, padx=5)

    win.wait_window()

# Summary

def summary():
    root = tk.Tk()
    root.withdraw()
    msg = f"Faces: {tf}\nSaved: {fs}\nSkipped: {fsk}\nOut: {od}"
    messagebox.showinfo("Done", msg)
    root.destroy()

# Main

global tf, fs, fsk, fps  # Declare globals at top
get_inputs()
pdf = fitz.open(pf)

print("[Info] Counting faces...")
totf = 0
for p in pdf:
    for img in p.get_images(full=True):
        arr = np.array(Image.open(io.BytesIO(pdf.extract_image(img[0])["image"])))
        totf += len(face_recognition.face_locations(arr))
print(f"[Info] Est. faces: {totf}")

proc = 0
st = time.time()

for pnum, p in enumerate(pdf):
    for idx, img in enumerate(p.get_images(full=True)):
        arr = np.array(Image.open(io.BytesIO(pdf.extract_image(img[0])["image"])))
        locs = face_recognition.face_locations(arr)

        for fidx, (t, r, b, l) in enumerate(locs):
            tf += 1
            proc += 1

            t, l = max(0, t - pd), max(0, l - pd)
            b, r = min(arr.shape[0], b + pd), min(arr.shape[1], r + pd)

            img_pil = Image.fromarray(arr)
            face = img_pil.crop((l, t, r, b)).resize(ss)

            show = pm == "full" or (pm == "first" and not fps)
            if show:
                show_preview(face)
                fps = True
                if scf:
                    fsk += 1
                    continue

            fn = f"page{pnum+1}_img{idx+1}_face{fidx+1}.{sf.lower()}"
            face.save(os.path.join(od, fn), format=sf)
            fs += 1

            et = time.time() - st
            rem = max(0, (et/proc) * totf - et)
            print(f"[Progress] {fs} saved, {fsk} skipped, ~{int(rem)}s left")

pdf.close()
summary()
