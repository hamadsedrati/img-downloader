# 🖼️ Advanced Image Downloader

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)]()
[![GUI](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet)](https://github.com/TomSchimansky/CustomTkinter)

> An **Advanced Python Image Downloader** with **CLI** and **GUI** modes — batch downloads, format conversion, image validation, previews, multi-threading, proxy support, logging, and more.

---

## ✨ Features

- 🖥️ **GUI Mode** – Modern interface built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)  
- 💻 **CLI Mode** – Flexible command-line control  
- 📂 **Single & Batch Downloads**  
- 📋 **Clipboard Support** – Paste URL directly  
- ⚡ **Multi-threaded Downloads** for speed  
- 📝 **Custom File Names**  
- 🔄 **Format Conversion** (e.g., PNG → JPG)  
- 🛡 **Image Validation** before saving  
- 👀 **Preview After Download**  
- 🌐 **Proxy & Custom User-Agent** support  
- 🗂 **Logging** to `img-downloader.log`  
- 📊 **Progress Bar** for real-time tracking  

---

## 📦 Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/image-downloader.git
cd image-downloader

# 2. Install dependencies
pip install -r requirements.txt
````

**`requirements.txt`**

```
requests
colorama
tqdm
pillow
pyperclip
customtkinter
```

---

## 🚀 Usage

### 1️⃣ Command Line Interface (CLI)

```bash
python img-downloader.py --url "https://example.com/image.jpg" --path ./images --name my_image --preview
```

#### Arguments

| Flag           | Description                                | Example                       |
| -------------- | ------------------------------------------ | ----------------------------- |
| `--url`        | Image URL or path to text file (for batch) | `"https://..."` or `urls.txt` |
| `--name`       | Custom file name                           | `myphoto`                     |
| `--path`       | Save directory                             | `./downloads`                 |
| `--retries`    | Retries on failure                         | `5`                           |
| `--proxy`      | Use a proxy                                | `http://127.0.0.1:8080`       |
| `--user-agent` | Custom User-Agent string                   | `"Mozilla/5.0 ..."`           |
| `--clipboard`  | Use URL from clipboard                     | *(no value)*                  |
| `--batch`      | Treat `--url` as file of URLs              | *(no value)*                  |
| `--threads`    | Number of threads for batch                | `8`                           |
| `--format`     | Convert to format                          | `jpg`                         |
| `--preview`    | Preview after download                     | *(no value)*                  |
| `--gui`        | Launch GUI mode                            | *(no value)*                  |

**Example – Batch Download**

```bash
python img-downloader.py --url urls.txt --batch --threads 6 --path ./downloads
```

**Example – Clipboard**

```bash
python img-downloader.py --clipboard --path ./images
```

---

### 2️⃣ Graphical User Interface (GUI)

Launch the GUI:

```bash
python img-downloader.py --gui
```

**GUI Features:**

* Enter **URL** or load a **batch file**
* Choose **save folder**
* Set **custom name** and **format**
* Enable **preview**
* Configure **proxy** and **user-agent**
* See **progress bar** & **live logs**

---

## 🛠 How It Works

1. **URL Parsing** → Extracts filename or generates one from timestamp
2. **Download** → Uses `requests` with optional proxy & headers
3. **Progress Tracking** → via `tqdm` progress bar
4. **Validation** → Ensures downloaded file is a valid image
5. **Conversion** → Optional format change via `Pillow`
6. **Preview** → Opens image with default viewer
7. **Logging** → Saves details & errors to `img-downloader.log`

---

## 📝 Logging

All downloads and actions are recorded in:

```
img-downloader.log
```

Includes:

* Download start/completion
* Errors & retries
* Conversion details
* Validation results

---

## ⚠️ Notes

* Batch file = **one URL per line**
* Supported formats: `jpg`, `jpeg`, `png`, `gif`, `bmp`, `webp`
* `--preview` may open multiple windows in batch mode
* GUI mode requires a display environment

---

## 📜 License

This project is licensed under the **MIT License** – you are free to use, modify, and distribute it.

---

💡 *Tip: Want to download hundreds of images? Use batch mode with `--threads` for maximum speed!*

