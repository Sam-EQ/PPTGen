import asyncio
import json
import uuid
from pathlib import Path

from core.markdown_loader import load_markdown
from core.executive_summary_llm import generate_executive_summary
from core.slide_planner_llm import plan_slides
from core.visual_enrichment_engine import enrich_slides
from core.validator import validate_deck
from renderers.pptx_renderer import render_pptx


BASE_DEBUG_DIR = Path("tmp/deck_runs")
BASE_DEBUG_DIR.mkdir(parents=True, exist_ok=True)


def save_text(path: Path, content: str):
    path.write_text(content, encoding="utf-8")


def save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


async def build_deck_from_markdown(md_path: Path):
    run_id = uuid.uuid4().hex[:8]
    run_dir = BASE_DEBUG_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nRun ID: {run_id}")
    print(f"Debug folder: {run_dir}")

    markdown = load_markdown(md_path)
    save_text(run_dir / "1_input_markdown.md", markdown)
    print("Saved raw markdown")

    print("Generating executive summary...")
    summary = await generate_executive_summary(markdown)
    save_text(run_dir / "2_executive_summary.md", summary)
    print("Saved executive summary")

    print("Planning slides...")
    deck = await plan_slides(summary)
    save_json(run_dir / "3_slide_plan.json", deck.dict())
    print("Saved slide plan")

    print("Enriching slides...")
    enriched_deck = enrich_slides(deck)
    save_json(run_dir / "4_enriched_slides.json", enriched_deck.dict())
    print("Saved enriched slides")

    print("Validating deck...")
    try:
        validate_deck(enriched_deck)
        validation_status = "VALID"
        print("Deck validation passed")
    except Exception as e:
        validation_status = f"FAILED → {str(e)}"
        print(f"Validation failed: {e}")

    save_text(run_dir / "5_validation.txt", validation_status)

    output_pptx = run_dir / "final_deck.pptx"

    if validation_status == "VALID":
        print("Rendering PPTX...")
        render_pptx(enriched_deck, output_pptx)
        print("PPTX generated")
    else:
        print("Skipping PPTX due to validation failure")

    return {
        "run_id": run_id,
        "slides": len(deck.slides),
        "validation": validation_status,
        "output": str(output_pptx),
    }


if __name__ == "__main__":
    import sys

    result = asyncio.run(build_deck_from_markdown(Path(sys.argv[1])))
    print("\nPipeline Result:")
    print(json.dumps(result, indent=2))