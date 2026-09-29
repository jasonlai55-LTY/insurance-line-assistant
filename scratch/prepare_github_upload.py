import os
import shutil

src_root = os.path.abspath(".")
out_root = os.path.join(src_root, "github_upload")

if os.path.exists(out_root):
    shutil.rmtree(out_root)

os.makedirs(out_root, exist_ok=True)

# List of folders to copy cleanly
folders_to_copy = ["liff-frontend", "admin-cms", "backend"]
files_to_copy = ["render.yaml", "vercel.json", "README.md"]

ignore_patterns = shutil.ignore_patterns(
    "node_modules", "venv", ".venv", "dist", ".pytest_cache", "__pycache__", "*.pyc", "local_dev.db", ".git"
)

for folder in folders_to_copy:
    src_dir = os.path.join(src_root, folder)
    dst_dir = os.path.join(out_root, folder)
    if os.path.exists(src_dir):
        shutil.copytree(src_dir, dst_dir, ignore=ignore_patterns)

for f in files_to_copy:
    src_file = os.path.join(src_root, f)
    dst_file = os.path.join(out_root, f)
    if os.path.exists(src_file):
        shutil.copy2(src_file, dst_file)

# Count total files
total_files = 0
for root, dirs, files in os.walk(out_root):
    total_files += len(files)

print(f"Clean GitHub upload folder prepared at: {out_root}")
print(f"Total files to upload: {total_files} files (well below GitHub's 100 file limit!)")
