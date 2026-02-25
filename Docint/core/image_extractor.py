import re
from typing import List, Dict
from pathlib import Path

from core.image_saver import save_marker_image

PAGE_RE = re.compile(r"_page_(\d+)_", re.IGNORECASE)


def extract_images(rendered, image_output_dir: Path) -> List[Dict]:
    images = []

    if not rendered.images:
        return images

    for name, img in rendered.images.items():
        m = PAGE_RE.search(name)
        page = int(m.group(1)) if m else None

        saved_path = save_marker_image(img, image_output_dir, page)

        images.append({
            "id": name,
            "name": name,              # markdown reference
            "image": img,              # in-memory object
            "page": page,
            "path": str(saved_path),   
        })

    return images