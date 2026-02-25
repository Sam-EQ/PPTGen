def render_html(deck):
    html = "<html><body>"

    for slide in deck.slides:
        html += f"<h2>{slide.title}</h2><ul>"
        for bullet in slide.bullets:
            html += f"<li>{bullet}</li>"
        html += "</ul>"

    html += "</body></html>"
    return html