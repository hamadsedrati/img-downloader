import os
import sys
import requests
import colorama as cl
import argparse
import logging
from tqdm import tqdm
from PIL import Image
import pyperclip
import threading
from urllib.parse import urlparse
from datetime import datetime
import customtkinter as ctk

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except ImportError:
    tk = None  # GUI will be optional

cl.init()

red = cl.Fore.RED
green = cl.Fore.GREEN
yellow = cl.Fore.YELLOW
light_yellow = cl.Fore.LIGHTYELLOW_EX
reset = cl.Style.RESET_ALL

ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "bmp", "webp"]

# Setup logging
logging.basicConfig(filename="img-downloader.log", level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def print_banner():
    banner = """
 █████ ██████   ██████   █████████     ██████████   █████      
░░███ ░░██████ ██████   ███░░░░░███   ░░███░░░░███ ░░███       
 ░███  ░███░█████░███  ███     ░░░     ░███   ░░███ ░███       
 ░███  ░███░░███ ░███ ░███             ░███    ░███ ░███       
 ░███  ░███ ░░░  ░███ ░███    █████    ░███    ░███ ░███       
 ░███  ░███      ░███ ░░███  ░░███     ░███    ███  ░███      █
 █████ █████     █████ ░░█████████     ██████████   ███████████
░░░░░ ░░░░░     ░░░░░   ░░░░░░░░░     ░░░░░░░░░░   ░░░░░░░░░░░ 
                                                               
"""
    print(f"{yellow}{banner}{reset}")

def ensure_folder(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            logging.info(f"Created directory: {path}")
        except Exception as e:
            print(f"{red}[ERROR]{reset} Could not create directory: {path}")
            logging.error(f"Failed to create directory {path}: {e}")
            sys.exit(1)
    elif not os.path.isdir(path):
        print(f"{red}[ERROR]{reset} Path exists but is not a directory: {path}")
        logging.error(f"Path exists but is not a directory: {path}")
        sys.exit(1)

def get_filename_from_url(url, extension=None):
    parsed = urlparse(url)
    base = os.path.basename(parsed.path)
    if not base or '.' not in base:
        # fallback to timestamp
        base = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    name, ext = os.path.splitext(base)
    ext = ext.lstrip('.')
    if extension:
        ext = extension
    if ext.lower() not in ALLOWED_EXTENSIONS:
        ext = 'jpg'
    return f"{name}.{ext}"

def validate_image(path):
    try:
        with Image.open(path) as img:
            img.verify()  # Will raise if not a valid image
        logging.info(f"Validated image: {path}")
        return True
    except Exception as e:
        print(f"{red}[ERROR]{reset} File is not a valid image: {path}")
        logging.error(f"Invalid image file {path}: {e}")
        return False

def convert_image_format(path, target_format):
    try:
        with Image.open(path) as img:
            base, _ = os.path.splitext(path)
            new_path = f"{base}.{target_format.lower()}"
            img = img.convert("RGB") if target_format.lower() in ["jpg", "jpeg"] else img
            # Map jpg/jpeg to 'JPEG' for Pillow
            format_for_pillow = target_format.upper()
            if format_for_pillow == "JPG":
                format_for_pillow = "JPEG"
            img.save(new_path, format_for_pillow)
        logging.info(f"Converted {path} to {new_path}")
        print(f"{green}[CONVERTED]{reset} Saved as {new_path}")
        return new_path
    except Exception as e:
        print(f"{red}[ERROR]{reset} Could not convert {path} to {target_format}: {e}")
        logging.error(f"Failed to convert {path} to {target_format}: {e}")
        return None

def preview_image(path):
    try:
        with Image.open(path) as img:
            img.show()
        logging.info(f"Previewed image: {path}")
    except Exception as e:
        print(f"{red}[ERROR]{reset} Could not preview image: {path}")
        logging.error(f"Failed to preview image {path}: {e}")

def download_image(url, save_path, filename=None, retries=3, user_agent=None, proxy=None, progress=True, target_format=None, preview=False):
    headers = {"User-Agent": user_agent} if user_agent else {}
    proxies = {"http": proxy, "https": proxy} if proxy else None
    attempt = 0
    while attempt < retries:
        try:
            with requests.get(url, headers=headers, proxies=proxies, stream=True, timeout=15) as r:
                r.raise_for_status()
                total = int(r.headers.get('content-length', 0))
                if not filename:
                    extension = url.split(".")[-1].split("?")[0].lower()
                    filename = get_filename_from_url(url, extension)
                full_path = os.path.join(save_path, filename)
                with open(full_path, 'wb') as f:
                    if progress and total > 0:
                        for data in tqdm(r.iter_content(1024), total=total // 1024, unit='KB', desc=filename):
                            f.write(data)
                    else:
                        for data in r.iter_content(1024):
                            f.write(data)
                logging.info(f"Downloaded: {url} -> {full_path}")
                print(f"{green}[SUCCESS]{reset} Downloaded: {filename}")
                # Validate image
                if not validate_image(full_path):
                    return None
                # Convert format if requested
                if target_format:
                    converted = convert_image_format(full_path, target_format)
                    if converted and preview:
                        preview_image(converted)
                elif preview:
                    preview_image(full_path)
                return full_path
        except Exception as e:
            attempt += 1
            print(f"{yellow}[RETRY]{reset} Attempt {attempt}/{retries} failed for {url}: {e}")
            logging.warning(f"Attempt {attempt}/{retries} failed for {url}: {e}")
    print(f"{red}[FAILED]{reset} Could not download: {url}")
    logging.error(f"Failed to download: {url}")
    return None

def batch_download(urls, save_path, retries=3, user_agent=None, proxy=None, threads=4, target_format=None, preview=False):
    ensure_folder(save_path)
    def worker(url):
        download_image(url, save_path, retries=retries, user_agent=user_agent, proxy=proxy, target_format=target_format, preview=preview)
    threads_list = []
    for url in urls:
        t = threading.Thread(target=worker, args=(url,))
        threads_list.append(t)
        t.start()
        if len(threads_list) >= threads:
            for t in threads_list:
                t.join()
            threads_list = []
    for t in threads_list:
        t.join()

def launch_gui():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.title("Image Downloader")
    root.geometry("700x500")
    root.configure(bg="#232323")
    root.resizable(True, True)

    # Font
    try:
        FONT = ("Poppins", 14)
        TITLE_FONT = ("Poppins", 22, "bold")
    except:
        FONT = ("Segoe UI", 14)
        TITLE_FONT = ("Segoe UI", 22, "bold")

    # Title
    title = ctk.CTkLabel(root, text="Image Downloader", font=TITLE_FONT, text_color="#3382CC")
    title.pack(pady=(24, 10))

    # URL/Batch Section
    url_frame = ctk.CTkFrame(root, fg_color="#232323", corner_radius=18)
    url_frame.pack(fill='x', padx=30, pady=5)
    ctk.CTkLabel(url_frame, text="Image URL:", font=FONT, text_color="#EEEEEE").grid(row=0, column=0, sticky='e', padx=5, pady=8)
    url_var = ctk.StringVar()
    url_entry = ctk.CTkEntry(url_frame, textvariable=url_var, width=320, font=FONT, corner_radius=12)
    url_entry.grid(row=0, column=1, columnspan=2, sticky='we', padx=5, pady=8)
    ctk.CTkLabel(url_frame, text="or Batch File:", font=FONT, text_color="#EEEEEE").grid(row=1, column=0, sticky='e', padx=5, pady=8)
    file_var = ctk.StringVar()
    file_entry = ctk.CTkEntry(url_frame, textvariable=file_var, width=220, font=FONT, corner_radius=12)
    file_entry.grid(row=1, column=1, sticky='we', padx=5, pady=8)
    def browse_file():
        filename = ctk.filedialog.askopenfilename(title="Select URL list file", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filename:
            file_var.set(filename)
            batch_var.set(True)
    ctk.CTkButton(url_frame, text="Browse", command=browse_file, width=80, font=FONT, fg_color="#3382CC", hover_color="#225A8F", corner_radius=12).grid(row=1, column=2, sticky='w', padx=5, pady=8)
    batch_var = ctk.BooleanVar()
    ctk.CTkCheckBox(url_frame, text="Batch Mode", variable=batch_var, font=FONT, text_color="#3382CC", corner_radius=10).grid(row=1, column=3, sticky='w', padx=5, pady=8)

    # Options Section
    options_frame = ctk.CTkFrame(root, fg_color="#232323", corner_radius=18)
    options_frame.pack(fill='x', padx=30, pady=10)
    ctk.CTkLabel(options_frame, text="Save Directory:", font=FONT, text_color="#EEEEEE").grid(row=0, column=0, sticky='e', padx=5, pady=8)
    path_var = ctk.StringVar(value=os.getcwd())
    path_entry = ctk.CTkEntry(options_frame, textvariable=path_var, width=220, font=FONT, corner_radius=12)
    path_entry.grid(row=0, column=1, sticky='we', padx=5, pady=8)
    def browse_folder():
        folder = ctk.filedialog.askdirectory(title="Select Save Directory")
        if folder:
            path_var.set(folder)
    ctk.CTkButton(options_frame, text="Browse", command=browse_folder, width=80, font=FONT, fg_color="#3382CC", hover_color="#225A8F", corner_radius=12).grid(row=0, column=2, sticky='w', padx=5, pady=8)
    ctk.CTkLabel(options_frame, text="Image Name (optional):", font=FONT, text_color="#EEEEEE").grid(row=1, column=0, sticky='e', padx=5, pady=8)
    name_var = ctk.StringVar()
    ctk.CTkEntry(options_frame, textvariable=name_var, width=120, font=FONT, corner_radius=12).grid(row=1, column=1, sticky='w', padx=5, pady=8)
    ctk.CTkLabel(options_frame, text="Format (jpg, png, ...):", font=FONT, text_color="#EEEEEE").grid(row=1, column=2, sticky='e', padx=5, pady=8)
    format_var = ctk.StringVar()
    ctk.CTkEntry(options_frame, textvariable=format_var, width=80, font=FONT, corner_radius=12).grid(row=1, column=3, sticky='w', padx=5, pady=8)
    preview_var = ctk.BooleanVar()
    ctk.CTkCheckBox(options_frame, text="Preview After Download", variable=preview_var, font=FONT, text_color="#3382CC", corner_radius=10).grid(row=2, column=1, sticky='w', padx=5, pady=8)
    ctk.CTkLabel(options_frame, text="Retries:", font=FONT, text_color="#EEEEEE").grid(row=2, column=2, sticky='e', padx=5, pady=8)
    retries_var = ctk.IntVar(value=3)
    ctk.CTkEntry(options_frame, textvariable=retries_var, width=50, font=FONT, corner_radius=12).grid(row=2, column=3, sticky='w', padx=5, pady=8)
    ctk.CTkLabel(options_frame, text="Proxy:", font=FONT, text_color="#EEEEEE").grid(row=3, column=0, sticky='e', padx=5, pady=8)
    proxy_var = ctk.StringVar()
    ctk.CTkEntry(options_frame, textvariable=proxy_var, width=120, font=FONT, corner_radius=12).grid(row=3, column=1, sticky='w', padx=5, pady=8)
    ctk.CTkLabel(options_frame, text="User-Agent:", font=FONT, text_color="#EEEEEE").grid(row=3, column=2, sticky='e', padx=5, pady=8)
    ua_var = ctk.StringVar()
    ctk.CTkEntry(options_frame, textvariable=ua_var, width=120, font=FONT, corner_radius=12).grid(row=3, column=3, sticky='w', padx=5, pady=8)

    # Progress Bar
    progress = ctk.CTkProgressBar(root, orientation='horizontal', mode='indeterminate', width=400, height=16, corner_radius=8)
    progress.pack(pady=(10, 0))

    # Start Button
    def start_download():
        log_text.set("")
        save_path = path_var.get()
        ensure_folder(save_path)
        progress.start()
        root.update()
        if batch_var.get() and file_var.get():
            try:
                with open(file_var.get(), 'r') as f:
                    urls = [line.strip() for line in f if line.strip()]
                log(f"Batch downloading {len(urls)} images...")
                batch_download(urls, save_path, retries=retries_var.get(), user_agent=ua_var.get() or None, proxy=proxy_var.get() or None, threads=4, target_format=format_var.get() or None, preview=preview_var.get())
                log("Batch download complete.")
            except Exception as e:
                log(f"Error: {e}")
        elif url_var.get():
            log(f"Downloading {url_var.get()}...")
            result = download_image(url_var.get(), save_path, filename=name_var.get() or None, retries=retries_var.get(), user_agent=ua_var.get() or None, proxy=proxy_var.get() or None, target_format=format_var.get() or None, preview=preview_var.get())
            if result:
                log("Download complete.")
            else:
                log("Error: Download or conversion failed. See log for details.")
        else:
            log("Please enter a URL or select a file.")
        progress.stop()
        root.update()

    ctk.CTkButton(root, text="Start Download", command=start_download, font=FONT, fg_color="#3382CC", hover_color="#225A8F", corner_radius=16, width=180, height=40).pack(pady=18)

    # Log Section
    log_frame = ctk.CTkFrame(root, fg_color="#232323", corner_radius=18)
    log_frame.pack(fill='both', expand=True, padx=30, pady=(0, 20))
    log_text = ctk.StringVar()
    log_area = ctk.CTkTextbox(log_frame, height=8, width=80, font=("Consolas", 12), fg_color="#393E46", text_color="#EEEEEE", corner_radius=12, wrap='word')
    log_area.pack(fill='both', expand=True, padx=5, pady=5)
    def log(msg):
        log_text.set(log_text.get() + msg + "\n")
        log_area.yview_moveto(1)
    def update_log(*args):
        log_area.delete("0.0", ctk.END)
        log_area.insert(ctk.END, log_text.get())
        log_area.yview_moveto(1)
    log_text.trace_add('write', update_log)

    root.mainloop()

def main():
    print_banner()
    parser = argparse.ArgumentParser(description="Advanced Image Downloader")
    parser.add_argument("--url", help="Image URL or path to file with URLs (for batch)")
    parser.add_argument("--name", help="Image name (optional)")
    parser.add_argument("--path", help="Save directory", default=os.getcwd())
    parser.add_argument("--retries", type=int, default=3, help="Number of retries on failure")
    parser.add_argument("--proxy", help="Proxy URL (e.g., http://127.0.0.1:8080)")
    parser.add_argument("--user-agent", help="Custom User-Agent header")
    parser.add_argument("--clipboard", action="store_true", help="Paste URL from clipboard")
    parser.add_argument("--batch", action="store_true", help="Batch mode: treat --url as file with URLs")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads for batch downloads")
    parser.add_argument("--format", help="Convert to format (e.g., jpg, png)")
    parser.add_argument("--preview", action="store_true", help="Preview image after download")
    parser.add_argument("--gui", action="store_true", help="Launch GUI")
    args = parser.parse_args()

    if args.gui:
        launch_gui()
        return

    if args.clipboard:
        url = pyperclip.paste()
        print(f"[INFO] URL from clipboard: {url}")
        args.url = url

    if args.batch and args.url:
        # Read URLs from file
        if not os.path.isfile(args.url):
            print(f"{red}[ERROR]{reset} Batch mode: file not found: {args.url}")
            sys.exit(1)
        with open(args.url, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        batch_download(urls, args.path, retries=args.retries, user_agent=args.user_agent, proxy=args.proxy, threads=args.threads, target_format=args.format, preview=args.preview)
        return
    if args.url:
        ensure_folder(args.path)
        filename = args.name if args.name else None
        download_image(args.url, args.path, filename=filename, retries=args.retries, user_agent=args.user_agent, proxy=args.proxy, target_format=args.format, preview=args.preview)
        return
    print(f"{red}[ERROR]{reset} No valid mode selected. Use --help for usage.")

if __name__ == "__main__":
    main()
