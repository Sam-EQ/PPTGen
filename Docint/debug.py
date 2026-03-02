import asyncio
import sys
import time
import json
import shutil
from pathlib import Path
from PIL import Image
from pdf2image import convert_from_path

# Internal imports from our new pipeline
from config import TEMP_DIR
from core.pipeline import _PIPELINE
from core.vlm_processor import describe_page_visuals

async def debug_docling_pipeline(pdf_path: Path):
    start_total = time.perf_counter()

    # 1. Setup Debug Directory
    debug_out = TEMP_DIR / "debug_docling" / pdf_path.stem
    if debug_out.exists():
        shutil.rmtree(debug_out)
    debug_out.mkdir(parents=True, exist_ok=True)
    
    pages_dir = debug_out / "page_renders"
    pages_dir.mkdir(exist_ok=True)

    print(f"Starting Debug for: {pdf_path.name}")
    print(f"Debug files will be in: {debug_out}")

    # 2. Run Docling (Structural Extraction)
    print("Running Docling conversion...")
    t0 = time.perf_counter()
    # Note: convert is sync, so we run in thread to not block event loop
    result = await asyncio.to_thread(_PIPELINE.converter.convert, str(pdf_path))
    doc = result.document
    raw_md = doc.export_to_markdown()
    
    # Save raw docling output
    (debug_out / "01_raw_docling.md").write_text(raw_md, encoding="utf-8")
    print(f"⏱ Docling took: {time.perf_counter() - t0:.2f}s")

    # 3. Render Pages for VLM
    print("Rendering PDF pages to images...")
    t0 = time.perf_counter()
    page_images = convert_from_path(str(pdf_path), dpi=300)
    for i, img in enumerate(page_images):
        img.save(pages_dir / f"page_{i+1}.jpg", "JPEG")
    print(f"⏱ Rendering took: {time.perf_counter() - t0:.2f}s")

    # 4. Detect Visual Pages
    visual_pages = set()
    for table in doc.tables:
        visual_pages.add(table.prov[0].page_no)
    for pic in doc.pictures:
        visual_pages.add(pic.prov[0].page_no)
    
    print(f"Docling detected visuals on pages: {sorted(list(visual_pages))}")

    # 5. Run VLM descriptions
    print(f"⏳ending {len(visual_pages)} pages to VLM (OpenAI)...")
    t0 = time.perf_counter()
    
    descriptions = {}
    
    async def process_page(p_num):
        img = page_images[p_num - 1]
        desc = await describe_page_visuals(img)
        # Save individual description for debugging
        (debug_out / f"desc_page_{p_num}.txt").write_text(desc, encoding="utf-8")
        return p_num, desc

    tasks = [process_page(p) for p in sorted(visual_pages)]
    vlm_results = await asyncio.gather(*tasks)
    
    for p_num, desc in vlm_results:
        descriptions[p_num] = desc
        
    print(f"⏱ VLM Processing took: {time.perf_counter() - t0:.2f}s")

    # 6. Final Assembly
    print("Injecting VLM descriptions into Markdown...")
    final_md = raw_md
    registry = []

    for p_num in sorted(descriptions.keys()):
        desc = descriptions[p_num]
        marker = f"## Page {p_num}"
        rich_injection = f"\n\n> ### VLM VISUAL ANALYSIS (Page {p_num})\n> {desc.replace('', '')}\n\n"
        
        if marker in final_md:
            final_md = final_md.replace(marker, f"{marker}\n{rich_injection}")
        
        registry.append({
            "page": p_num,
            "image_path": str(pages_dir / f"page_{p_num}.jpg"),
            "description": desc
        })

    # Save Final Outputs
    (debug_out / "02_final_rag_ready.md").write_text(final_md, encoding="utf-8")
    (debug_out / "manifest.json").write_text(json.dumps(registry, indent=2), encoding="utf-8")

    total_time = time.perf_counter() - start_total
    print("\nDebug Pipeline Complete!")
    print(f"⏱ TOTAL TIME: {total_time:.2f}s")
    print(f"Final Markdown: {debug_out / '02_final_rag_ready.md'}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_docling.py <path_to_pdf>")
        sys.exit(1)
        
    pdf = Path(sys.argv[1])
    asyncio.run(debug_docling_pipeline(pdf))