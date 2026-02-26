def validate_deck(deck):
    assert len(deck.slides) > 0, "Deck has no slides"

    for i, slide in enumerate(deck.slides):
        assert slide.title.strip(), "Slide missing title"

        if i == 0:
            continue

        assert len(slide.bullets) > 0, f"{slide.title} has no bullets"

    return True