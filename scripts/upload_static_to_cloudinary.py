"""
AgroTech — One-time script to upload all project static images to Cloudinary (ddwrdkpkv).
Run: python scripts/upload_static_to_cloudinary.py
"""

import os
import sys
import cloudinary
import cloudinary.uploader

# Configure Cloudinary (new account)
cloudinary.config(
    cloud_name="ddwrdkpkv",
    api_key="283771221969341",
    api_secret="Gp1ngeDJTKuP6sDsewz-cDOwflc",
    secure=True
)

# Static directory path
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")

# Image extensions to upload
IMAGE_EXTENSIONS = {".webp", ".jpg", ".jpeg", ".png"}

def upload_all_static_images():
    uploaded = {}
    failed = []

    for root, dirs, files in os.walk(STATIC_DIR):
        # Skip css and js folders
        dirs[:] = [d for d in dirs if d not in ("css", "js")]

        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in IMAGE_EXTENSIONS:
                continue

            filepath = os.path.join(root, filename)
            # Create a public_id like "agrotech/logo" or "agrotech/legends/ms_swaminathan"
            rel = os.path.relpath(filepath, STATIC_DIR)
            public_id = "agrotech/" + os.path.splitext(rel.replace("\\", "/"))[0]

            print(f"Uploading: {rel} -> {public_id} ...", end=" ", flush=True)
            try:
                result = cloudinary.uploader.upload(
                    filepath,
                    public_id=public_id,
                    overwrite=True,
                    resource_type="image",
                    quality="auto",
                    fetch_format="auto",
                )
                secure_url = result["secure_url"]
                key = os.path.splitext(filename)[0].lower()
                uploaded[key] = secure_url
                print(f"✅ {secure_url}")
            except Exception as e:
                print(f"❌ FAILED: {e}")
                failed.append(rel)

    print("\n" + "=" * 70)
    print("UPLOAD COMPLETE")
    print(f"✅ Uploaded: {len(uploaded)} images")
    print(f"❌ Failed:   {len(failed)} images")
    print("=" * 70)
    print("\n# Copy these to settings.py CLOUDINARY_IMAGE_URLS dict:\n")
    print("CLOUDINARY_IMAGE_URLS = {")
    for key, url in uploaded.items():
        print(f'    "{key}": "{url}",')
    print("}")

    if failed:
        print("\nFailed files:")
        for f in failed:
            print(f"  - {f}")

    return uploaded

if __name__ == "__main__":
    upload_all_static_images()
