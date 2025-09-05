#!/usr/bin/env python3
import os
import shutil
import subprocess
from pathlib import Path
from flask import Flask, render_template, send_from_directory, request, jsonify, abort

# ====== CONFIG ======
RAW_DIR   = Path("/home/kcooney/CalendarScreenSaver/raw_images")
COOKED_DIR   = Path("/home/kcooney/CalendarScreenSaver/cooked_images")
ALL_DIR      = Path("/home/kcooney/CalendarScreenSaver/all_images")
DELETED_DIR  = Path("/home/kcooney/CalendarScreenSaver/deleted_images")
DROPBOX_DIR   = Path("/home/kcooney/Pictures/Dropbox/Frame")  # Dropbox folder syncs here

# Path to the Dropbox-Uploader script and its config file
DROPBOX_UPLOADER = Path("/home/kcooney/Dropbox-Uploader/dropbox_uploader.sh")  # adjust if needed
DROPBOX_CONFIG   = Path("/home/kcooney/.dropbox_uploader")

# Allowed image extensions (case-insensitive)
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"}

# ====== APP ======
app = Flask(__name__)

def list_gallery_images():
    if not COOKED_DIR.exists():
        return []
    files = []
    for p in COOKED_DIR.iterdir():
        if p.is_file() and p.suffix.lower() in ALLOWED_EXTS:
            files.append(p.name)
    # Newest first by mtime
    files.sort(key=lambda n: (COOKED_DIR / n).stat().st_mtime, reverse=True)
    return files

@app.route("/")
def index():
    images = list_gallery_images()
    return render_template("index.html", images=images)

# Serve cooked_images files directly
@app.route("/media/<path:filename>")
def media(filename):
    # Prevent path traversal; only allow basenames that actually exist in cooked dir
    safe = os.path.basename(filename)
    if safe != filename:
        abort(400, description="Invalid path.")
    target = COOKED_DIR / safe
    if not target.exists():
        abort(404)
    return send_from_directory(COOKED_DIR, safe, as_attachment=False)

@app.post("/api/delete")
def api_delete():
    data = request.get_json(silent=True) or {}
    filename = data.get("filename", "")

    # Basic safety: only allow deleting a plain filename found in cooked dir
    if not filename or os.path.basename(filename) != filename:
        return jsonify(ok=False, error="Invalid filename."), 400

    cooked_path = COOKED_DIR / filename
    raw_path = COOKED_DIR / filename
    all_rel_path = filename.replace("--", "/")
    all_path = ALL_DIR / all_rel_path
    deleted_backup_path = DELETED_DIR / all_rel_path
    dropbox_local_path = DROPBOX_DIR / all_rel_path

    results = {"cooked": None, "raw": None, "dropbox_local": None, "all_images_move": None, "dropbox": None}

    # 1) Delete from cooked_images
    try:
        if cooked_path.exists():
            cooked_path.unlink()
            results["cooked"] = "deleted"
        else:
            results["cooked"] = "not_found"
    except Exception as e:
        results["cooked"] = f"error: {e}"

    # 2) Delete from raw_images
    try:
        if raw_path.exists():
            raw_path.unlink()
            results["raw"] = "deleted"
        else:
            results["raw"] = "not_found"
    except Exception as e:
        results["raw"] = f"error: {e}"

    # 3) Delete from dropbox local folder
    try:
        if dropbox_local_path.exists():
            dropbox_local_path.unlink()
            results["dropbox_local"] = "deleted"
        else:
            results["dropbox_local"] = "not_found"
    except Exception as e:
        results["dropbox_local"] = f"error: {e}"

    # 4) Move from all_images to deleted_images (preserving subfolder structure)
    try:
        if all_path.exists():
            deleted_backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(all_path), str(deleted_backup_path))
            results["all_images_move"] = f"moved_to_backup:{deleted_backup_path}"
        else:
            results["all_images_move"] = "not_found"
    except Exception as e:
        results["all_images_move"] = f"error: {e}"

    # 5) Remove from Dropbox using Dropbox-Uploader
    try:
        if DROPBOX_UPLOADER.exists() and DROPBOX_CONFIG.exists():
            # Use leading slash for a clear root-relative path in Dropbox
            remote_path = "/Photos/Frame/" + all_rel_path
            proc = subprocess.run(
                [str(DROPBOX_UPLOADER), "-f", str(DROPBOX_CONFIG), "delete", remote_path],
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode == 0:
                results["dropbox"] = "deleted"
            else:
                # Dropbox-Uploader prints errors on stdout/stderr; return a snippet for visibility
                results["dropbox"] = f"error: rc={proc.returncode} out={proc.stdout.strip()} err={proc.stderr.strip()}"
        else:
            results["dropbox"] = "skipped: uploader or config not found"
    except Exception as e:
        results["dropbox"] = f"error: {e}"

    # Consider it success if at least one of the three actions either deleted/moved or wasn't present
    ok = any(
        s in ("deleted", "not_found") or (isinstance(s, str) and s.startswith("moved_to_backup"))
        for s in results.values()
    )

    status = 200 if ok else 500
    return jsonify(ok=ok, results=results), status

if __name__ == "__main__":
    # Listen on all interfaces so your phone on LAN can reach it
    app.run(host="0.0.0.0", port=8123)
