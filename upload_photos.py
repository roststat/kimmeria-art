"""
Загрузка фото на Cloudinary.
Использование:
  python3 upload_photos.py foto1.jpg foto2.jpg
  python3 upload_photos.py C:/путь/к/папке/
  python3 upload_photos.py  (загружает всё из папки photos/)
"""

import cloudinary
import cloudinary.uploader
import os
import sys

cloudinary.config(
    cloud_name = "dmzsczjzd",
    api_key    = "733872474498717",
    api_secret = "uNCuefDPhmOb8XOhACLdJZUeW9s"
)

EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.webp')

def upload(path):
    fname = os.path.basename(path)
    public_id = "kimmeria/" + os.path.splitext(fname)[0]
    try:
        r = cloudinary.uploader.upload(
            path,
            public_id=public_id,
            overwrite=True,
            resource_type="image"
        )
        print(f"OK  {fname}")
        print(f"    {r['secure_url']}")
        return r['secure_url']
    except Exception as e:
        print(f"ERR {fname} — {e}")
        return None

def collect_files(args):
    files = []
    if not args:
        # Загрузить всё из папки photos/
        photos_dir = os.path.join(os.path.dirname(__file__), 'photos')
        if os.path.isdir(photos_dir):
            files = [os.path.join(photos_dir, f) for f in sorted(os.listdir(photos_dir))
                     if f.lower().endswith(EXTENSIONS)]
        else:
            print("Папка photos/ не найдена. Укажите файлы или папку аргументом.")
    else:
        for arg in args:
            if os.path.isdir(arg):
                files += [os.path.join(arg, f) for f in sorted(os.listdir(arg))
                          if f.lower().endswith(EXTENSIONS)]
            elif os.path.isfile(arg):
                files.append(arg)
            else:
                print(f"Не найдено: {arg}")
    return files

if __name__ == "__main__":
    files = collect_files(sys.argv[1:])
    if not files:
        print("Нет файлов для загрузки.")
        sys.exit(1)

    print(f"Загружаю {len(files)} файл(ов)...\n")
    urls = {}
    for f in files:
        url = upload(f)
        if url:
            urls[os.path.basename(f)] = url

    print(f"\nГотово: {len(urls)}/{len(files)} загружено.")
    if urls:
        print("\nURL для вставки в HTML:")
        for fname, url in urls.items():
            print(f"  {fname} → {url}")
