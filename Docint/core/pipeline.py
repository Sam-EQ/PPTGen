import asyncio
from pathlib import Path
from pdf2image import convert_from_path
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption  # Added PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from core.vlm_processor import describe_page_visuals

class DoclingPipeline:
    def __init__(self):
        # 1. Configure the low-level pipeline options
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_table_structure = True
        pipeline_options.do_ocr = True 
        pipeline_options.generate_page_images = False
        pipeline_options.generate_picture_images = True
        
        # 2. In Docling v2, wrap pipeline_options in a PdfFormatOption
        # and pass it via the format_options mapping
        self.converter = DocumentConverter(
            allowed_formats=[InputFormat.PDF],
            format_options={ 
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

    async def process_pdf(self, pdf_path: Path) -> str:
        # 1. Convert PDF to Docling Document (Text & Layout)
        # We run this in a thread because Docling's convert is a blocking CPU-bound task
        result = await asyncio.to_thread(self.converter.convert, str(pdf_path))
        doc = result.document
        
        # 2. Render all pages to images for VLM context
        page_images = convert_from_path(str(pdf_path), dpi=300)

        # 3. Identify which pages have visual assets
        visual_pages = set()
        for table in doc.tables:
            if table.prov:
                visual_pages.add(table.prov[0].page_no)
        for pic in doc.pictures:
            if pic.prov:
                visual_pages.add(pic.prov[0].page_no)

        # 4. Process Visual Pages with VLM in parallel
        page_descriptions = {}
        if visual_pages:
            async def get_desc(page_num):
                img = page_images[page_num - 1]
                desc = await describe_page_visuals(img)
                return page_num, desc

            tasks = [get_desc(page_num) for page_num in sorted(visual_pages)]
            vlm_results = await asyncio.gather(*tasks)
            for page_num, desc in vlm_results:
                page_descriptions[page_num] = desc

        # 5. Assemble Final Markdown
        base_md = doc.export_to_markdown()
        
        final_md = base_md
        for page_num, desc in page_descriptions.items():
            # Injecting description into the Markdown
            # Docling uses headers for pages like "## Page 1"
            insertion_marker = f"## Page {page_num}"
            rich_desc = f"\n\n> ### VISUAL ANALYSIS (Page {page_num})\n> {desc}\n\n"
            
            if insertion_marker in final_md:
                final_md = final_md.replace(insertion_marker, f"{insertion_marker}\n{rich_desc}")
            else:
                final_md += f"\n\n--- Page {page_num} Visuals ---\n{desc}"

        return final_md

_PIPELINE = DoclingPipeline()