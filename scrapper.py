import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Path to your HTML file
html_file = "http_response_body.html"

# Folder to store downloaded images
images_folder = "downloaded_images"
os.makedirs(images_folder, exist_ok=True)

# Read the HTML content (adjust encoding if needed)
with open(html_file, "r", encoding="utf-8") as f:
    html_content = f.read()

# Parse the HTML
soup = BeautifulSoup(html_content, "html.parser")

# Base URL for relative URLs (adjust as needed)
base_url = "https://www.instacart.com/"

# Set to hold unique image URLs
image_urls = set()

# 1. Extract from <img> tags
for img in soup.find_all("img"):
    # Check standard attributes
    for attr in ["src", "data-src", "srcset"]:
        url = img.get(attr)
        if url:
            # For srcset, it might have multiple URLs; take the first one.
            if attr == "srcset":
                url = url.split(",")[0].strip().split(" ")[0]
            image_urls.add(url)

# 2. Extract from <source> tags (commonly inside <picture>)
for source in soup.find_all("source"):
    src = source.get("src")
    if src:
        image_urls.add(src)
    srcset = source.get("srcset")
    if srcset:
        # Use the first URL from srcset
        url = srcset.split(",")[0].strip().split(" ")[0]
        image_urls.add(url)

# 3. Extract from <a> tags that might link directly to an image
# Check if href ends with common image extensions.
img_exts = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg")
for a in soup.find_all("a"):
    href = a.get("href")
    if href and href.lower().endswith(img_exts):
        image_urls.add(href)

# 4. Extract from inline styles containing background images.
# This regex will look for patterns like background(-image)?: url("...")
bg_img_pattern = re.compile(r'background(?:-image)?\s*:\s*url\(["\']?(.*?)["\']?\)', re.IGNORECASE)
for tag in soup.find_all(True):  # all tags
    style = tag.get("style")
    if style:
        matches = bg_img_pattern.findall(style)
        for match in matches:
            if match:
                image_urls.add(match)

if not image_urls:
    print("No image URLs found in the HTML.")
else:
    print(f"Found {len(image_urls)} candidate image URLs.")

# Download each unique image
for i, url in enumerate(image_urls):
    # Convert relative URLs to absolute URLs
    if not url.startswith("http"):
        img_url = urljoin(base_url, url)
    else:
        img_url = url

    print(f"[{i}] Downloading: {img_url}")
    try:
        response = requests.get(img_url)
        response.raise_for_status()
        # Get the extension; default to .jpg if not found
        ext = os.path.splitext(img_url)[1]
        if ext.lower() not in img_exts:
            ext = ".jpg"
        filename = os.path.join(images_folder, f"image_{i}{ext}")
        with open(filename, "wb") as img_file:
            img_file.write(response.content)
        print(f"Saved image to {filename}")
    except Exception as e:
        print(f"Failed to download {img_url}: {e}")
