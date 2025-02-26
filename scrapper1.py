import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from base64 import b64decode

# === STEP 1: Fetch HTML using Zyte API ===

zyte_api_key = "83f665c467c34fea8fe6b2ceda112b49"
product_url = "https://www.instacart.com/products/18684158-progresso-traditional-creamy-chicken-noodle-soup-18-500-oz?retailerSlug=foodsco"

# Send POST request to Zyte API endpoint to extract the HTML content
api_response = requests.post(
    "https://api.zyte.com/v1/extract",
    auth=(zyte_api_key, ""),
    json={
        "url": product_url,
        "httpResponseBody": True,
    },
)

# Decode the base64 encoded HTML body
html_bytes = b64decode(api_response.json()["httpResponseBody"])
html_content = html_bytes.decode("utf-8")

# Optionally, save the HTML content locally for debugging
with open("http_response_body.html", "w", encoding="utf-8") as fp:
    fp.write(html_content)
print("Fetched and saved HTML from Zyte.")

# === STEP 2: Parse HTML and Extract Image URLs ===

# Folder to store downloaded images
images_folder = "downloaded_images"
os.makedirs(images_folder, exist_ok=True)

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Base URL for relative URLs (adjust as needed)
base_url = "https://www.instacart.com/"

# Set to hold unique image URLs
image_urls = set()

# 1. Extract from <img> tags
for img in soup.find_all("img"):
    for attr in ["src", "data-src", "srcset"]:
        url = img.get(attr)
        if url:
            if attr == "srcset":
                # For srcset, use the first URL
                url = url.split(",")[0].strip().split(" ")[0]
            image_urls.add(url)

# 2. Extract from <source> tags (inside <picture> elements)
for source in soup.find_all("source"):
    src = source.get("src")
    if src:
        image_urls.add(src)
    srcset = source.get("srcset")
    if srcset:
        url = srcset.split(",")[0].strip().split(" ")[0]
        image_urls.add(url)

# 3. Extract from <a> tags that might link directly to an image
img_exts = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg")
for a in soup.find_all("a"):
    href = a.get("href")
    if href and href.lower().endswith(img_exts):
        image_urls.add(href)

# 4. Extract from inline styles (e.g., background-image)
bg_img_pattern = re.compile(r'background(?:-image)?\s*:\s*url\(["\']?(.*?)["\']?\)', re.IGNORECASE)
for tag in soup.find_all(True):
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

# === STEP 3: Download the Images ===

for i, url in enumerate(image_urls):
    if not url.startswith("http"):
        img_url = urljoin(base_url, url)
    else:
        img_url = url

    print(f"[{i}] Downloading: {img_url}")
    try:
        response = requests.get(img_url)
        response.raise_for_status()
        ext = os.path.splitext(img_url)[1] or ".jpg"
        if ext.lower() not in img_exts:
            ext = ".jpg"
        filename = os.path.join(images_folder, f"image_{i}{ext}")
        with open(filename, "wb") as img_file:
            img_file.write(response.content)
        print(f"Saved image to {filename}")
    except Exception as e:
        print(f"Failed to download {img_url}: {e}")
