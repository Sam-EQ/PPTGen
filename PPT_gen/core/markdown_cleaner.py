import re


def clean_markdown(md: str) -> str:

    lines = md.splitlines()
    cleaned_lines = []

    previous_blank = False

    for line in lines:
        original_line = line

        if re.match(r"\{\d+\}[-]{10,}", line):
            continue

        if re.match(r"[-]{20,}", line.strip()):
            continue

        line = re.sub(r"\s+", " ", line).rstrip()

        line = re.sub(r"^\s*[\•\-\–]\s*", "- ", line)

        if line.strip().startswith("#"):
            line = re.sub(r"\s+", " ", line)

        if cleaned_lines:
            prev = cleaned_lines[-1]

            if (
                prev and
                not prev.startswith("#") and
                not prev.startswith("- ") and
                not line.startswith("#") and
                not line.startswith("- ") and
                not prev.endswith((".", ":", ";")) and
                line
            ):
                cleaned_lines[-1] = prev + " " + line
                continue

        if not line.strip():
            if previous_blank:
                continue
            previous_blank = True
            cleaned_lines.append("")
        else:
            previous_blank = False
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()