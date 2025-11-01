import io
import zipfile
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image
import sys
import os

Image.MAX_IMAGE_PIXELS = None

TOTAL_FILES = 310

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

zip_path = os.path.join(base_path, "cookieclicker.zip")

def process_image(input_path, output_zip_path, progress_callback):
    base_img = Image.open(input_path).convert("RGBA")

    with open(zip_path, "rb") as f:
        original_zip = io.BytesIO(f.read())

    buffer = io.BytesIO()
    with zipfile.ZipFile(original_zip, "r") as zin, zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zout:
        current = 0

        for item in zin.infolist():
            data = zin.read(item.filename)
            if not item.filename.startswith("img/"):
                zout.writestr(item, data)
                current += 1
                progress_callback(min(current, TOTAL_FILES), TOTAL_FILES)
                continue

            filename = os.path.basename(item.filename)
            ext = filename.lower().split(".")[-1]
            if not ext in ("png", "jpg", "jpeg", "bmp", "webp"):
                zout.writestr(item, data)
                current += 1
                progress_callback(min(current, TOTAL_FILES), TOTAL_FILES)
                continue

            try:
                with Image.open(io.BytesIO(data)) as target_img:
                    w, h = target_img.size
            except Exception:
                zout.writestr(item, data)
                current += 1
                progress_callback(min(current, TOTAL_FILES), TOTAL_FILES)
                continue

            src = base_img.resize((w, h), Image.LANCZOS)
            if ext in ("jpg", "jpeg"):
                src = src.convert("RGB")

            img_bytes = io.BytesIO()
            src.save(img_bytes, format="PNG" if ext == "png" else "JPEG")
            zout.writestr(item.filename, img_bytes.getvalue())

            current += 1
            progress_callback(min(current, TOTAL_FILES), TOTAL_FILES)

        empty_img = base_img.resize((256, 256), Image.LANCZOS)
        save_to_zip(zout, "img/empty.png", empty_img, "PNG")

        icon_tile = base_img.resize((48, 48), Image.LANCZOS)
        icons = Image.new("RGBA", (48 * 36, 48 * 37))
        for y in range(37):
            for x in range(36):
                icons.paste(icon_tile, (x * 48, y * 48))
        save_to_zip(zout, "img/icons.png", icons, "PNG")

        storetile = Image.new("RGB", (300, 256))
        part_height = 256 // 4
        stretched = base_img.resize((300, part_height), Image.LANCZOS)
        for i in range(4):
            storetile.paste(stretched, (0, i * part_height))
        save_to_zip(zout, "img/storeTile.jpg", storetile, "JPEG")

        bld_tile = base_img.resize((64, 64), Image.LANCZOS)
        buildings = Image.new("RGBA", (64 * 4, 64 * 21))
        for y in range(21):
            for x in range(4):
                buildings.paste(bld_tile, (x * 64, y * 64))
        save_to_zip(zout, "img/buildings.png", buildings, "PNG")

    with open(output_zip_path, "wb") as f:
        f.write(buffer.getvalue())

def save_to_zip(zip_obj, path, img, fmt):
    img_bytes = io.BytesIO()
    img.save(img_bytes, format=fmt)
    zip_obj.writestr(path, img_bytes.getvalue())

def start_gui():
    root = tk.Tk()
    root.title("Cookifier 1.0.0")
    root.geometry("300x100")
    root.resizable(False, False)

    start_button = ttk.Button(root, text="Begin Cookification Process")
    progress_label = tk.Label(root, text="Progress: 0 / 310")
    progress_bar = ttk.Progressbar(root, length=260, mode='determinate', maximum=TOTAL_FILES)

    start_button.pack(expand=True)

    def update_progress(current, total):
        progress_bar["value"] = min(current, total)
        progress_label.config(text=f"Progress: {min(current, total)} / {total}")
        root.update_idletasks()

    def run_process():
        image_path = filedialog.askopenfilename(
            title="Select Image to Cookify..",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp")]
        )
        if not image_path:
            return

        output_zip = filedialog.asksaveasfilename(
            title="Save Cookified ZIP as...",
            defaultextension=".zip",
            filetypes=[("ZIP files", "*.zip")]
        )
        if not output_zip:
            return

        start_button.pack_forget()
        root.geometry("300x120")
        progress_label.pack(pady=5)
        progress_bar.pack(pady=5)
        root.update_idletasks()

        update_progress(0, TOTAL_FILES)
        try:
            process_image(image_path, output_zip, update_progress)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")
            progress_label.pack_forget()
            progress_bar.pack_forget()
            start_button.pack(expand=True)
            root.geometry("300x100")
            return

        progress_label.pack_forget()
        progress_bar.pack_forget()
        messagebox.showinfo("Successfully Cookified", "The input image has successfully been Cookified.")
        root.destroy()

    start_button.config(command=run_process)
    root.mainloop()


if __name__ == "__main__":
    start_gui()
