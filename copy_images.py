import re
import shutil
from pathlib import Path
from urllib.parse import quote

# ==================================================
# CONFIG - Change only this
# ==================================================
VAULT_PATH = "~/syncthing/obsidian-vault"

# Vault folders
POSTS_FOLDER = "posts"
ATTACHMENTS_FOLDER = "97 - Resources"
# ==================================================

# Script location = Hugo root
SCRIPT_DIR = Path(__file__).resolve().parent
HUGO_ROOT = SCRIPT_DIR

# Expand vault path
vault_root = Path(VAULT_PATH).expanduser()

posts_dir = vault_root / POSTS_FOLDER
attachments_dir = vault_root / ATTACHMENTS_FOLDER

# Hugo paths relative to script location
output_dir = HUGO_ROOT / "content/posts"
static_images_dir = HUGO_ROOT / "static/images"

# Create folders if missing
output_dir.mkdir(parents=True, exist_ok=True)
static_images_dir.mkdir(parents=True, exist_ok=True)

# Match:
# ![[image.png]]
# ![[image.png|500]]
image_pattern = re.compile(
    r"!\[\[([^|\]]+\.(?:png|jpg|jpeg|gif|webp))(?:\|[^\]]+)?\]\]", re.IGNORECASE
)

print("Vault Root:", vault_root)
print("Posts Folder:", posts_dir)
print("Attachments Folder:", attachments_dir)
print("Hugo Root:", HUGO_ROOT)
print()

# Process markdown files
for source_path in posts_dir.glob("*.md"):
    output_path = output_dir / source_path.name

    with open(source_path, "r", encoding="utf-8") as f:
        content = f.read()

    def replace_image(match):
        image_name = match.group(1)
        image_path = attachments_dir / image_name

        if image_path.exists():
            shutil.copy2(image_path, static_images_dir / image_name)
            print(f"Copied image: {image_name}")
        else:
            print(f"Missing image: {image_name}")

        alt_text = Path(image_name).stem.replace("-", " ").replace("_", " ")
        return f"![{alt_text}](/images/{quote(image_name)})"

    new_content = image_pattern.sub(replace_image, content)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Processed post: {source_path.name}")

print()
print("Done.")
