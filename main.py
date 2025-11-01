import io
import zipfile
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image
import os

Image.MAX_IMAGE_PIXELS = None

TOTAL_FILES = 310

def process_image(input_path, output_zip_path, progress_callback):
    base_img = Image.open(input_path).convert("RGBA")

    with open("cookieclicker.zip", "rb") as f:
        original_zip = io.BytesIO(f.read())

    buffer = io.BytesIO()
    with zipfile.ZipFile(original_zip, "r") as zin, zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zout:
        current = 0

        for item in zin.infolist():
            if not item.filename.startswith("img/"):
                zout.writestr(item, zin.read(item.filename))
                current = min(current + 1, TOTAL_FILES)
                progress_callback(current, TOTAL_FILES)

        def save_to_zip(path, image, fmt):
            img_bytes = io.BytesIO()
            image.save(img_bytes, format=fmt)
            zout.writestr(path, img_bytes.getvalue())

        empty_img = base_img.resize((256, 256), Image.LANCZOS)
        save_to_zip("img/empty.png", empty_img, "PNG")
        current += 1
        progress_callback(current, TOTAL_FILES)

        icon_tile = base_img.resize((48, 48), Image.LANCZOS)
        icons = Image.new("RGBA", (48 * 36, 48 * 37))
        for y in range(37):
            for x in range(36):
                icons.paste(icon_tile, (x * 48, y * 48))
        save_to_zip("img/icons.png", icons, "PNG")
        current += 1
        progress_callback(current, TOTAL_FILES)

        part_height = 256 // 4
        stretched = base_img.resize((300, part_height), Image.LANCZOS)
        storetile = Image.new("RGB", (300, 256))
        for i in range(4):
            storetile.paste(stretched, (0, i * part_height))
        save_to_zip("img/storeTile.jpg", storetile, "JPEG")
        current += 1
        progress_callback(current, TOTAL_FILES)

        building_tile = base_img.resize((64, 64), Image.LANCZOS)
        buildings = Image.new("RGBA", (64 * 4, 64 * 21))
        for y in range(21):
            for x in range(4):
                buildings.paste(building_tile, (x * 64, y * 64))
        save_to_zip("img/buildings.png", buildings, "PNG")
        current += 1
        progress_callback(current, TOTAL_FILES)

    with open(output_zip_path, "wb") as f:
        f.write(buffer.getvalue())

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
