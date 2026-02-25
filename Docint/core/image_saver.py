from pathlib import Path
import uuid


def save_marker_image(marker_image, output_dir: Path, page: int | None):

    output_dir.mkdir(parents=True, exist_ok=True)

    page_str = f"page_{page}_" if page is not None else "page_unknown_"
    filename = f"{page_str}{uuid.uuid4().hex[:8]}.jpg"

    path = output_dir / filename

    if hasattr(marker_image, "save"):
        marker_image.save(path, format="JPEG")

    elif hasattr(marker_image, "image"):
        marker_image.image.save(path, format="JPEG")

    else:
        raise TypeError(f"Unsupported image type: {type(marker_image)}")

    return path