from pptx import Presentation


def render_pptx(deck, output_path):
    prs = Presentation()

    for slide_data in deck.slides:
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)

        slide.shapes.title.text = slide_data.title
        slide.placeholders[1].text = "\n".join(slide_data.bullets)

        if slide_data.notes:
            slide.notes_slide.notes_text_frame.text = slide_data.notes

    prs.save(output_path)