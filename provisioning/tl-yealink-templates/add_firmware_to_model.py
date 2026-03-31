#!/usr/bin/env python3
"""Add firmware= line to each section in yealink_model.txt after lines=N.
Firmware filename is extracted from input_1 device cfg (firmware.url).
"""
import re
import os

DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(DIR, "yealink_model.txt")


def get_firmware_from_device_cfg(device_cfg_path):
    """Read device cfg and return firmware filename from firmware.url or None."""
    path = os.path.join(DIR, device_cfg_path)
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        for line in f:
            m = re.search(r"firmware\.url\s*=\s*\S+/([^\s/]+)", line)
            if m:
                return m.group(1)
    return None


def main():
    with open(MODEL_FILE) as f:
        content = f.read()

    # Split into sections: [header]\nkey=val...
    sections = re.split(r"\n(?=\[yealink-)", content)
    if sections and not sections[0].strip().startswith("["):
        # leading empty or non-section
        preamble = sections[0]
        sections = sections[1:]
    else:
        preamble = ""

    out_sections = []
    for block in sections:
        if not block.strip():
            out_sections.append(block)
            continue
        lines = block.split("\n")
        # First line is [yealink-...]
        # Find input_1= and lines=
        input_1 = None
        lines_line_idx = None
        for i, line in enumerate(lines):
            if line.startswith("input_1="):
                input_1 = line.split("=", 1)[1].strip()
            if re.match(r"^lines=\d+", line):
                lines_line_idx = i
        if input_1 is None or lines_line_idx is None:
            out_sections.append(block)
            continue
        firmware = get_firmware_from_device_cfg(input_1)
        if not firmware:
            out_sections.append(block)
            continue
        # Check if firmware= already present in this section
        if any(re.match(r"^firmware=", l) for l in lines):
            out_sections.append(block)
            continue
        # Insert "firmware=XXX" after lines_line_idx
        new_lines = (
            lines[: lines_line_idx + 1]
            + [f"firmware={firmware}"]
            + lines[lines_line_idx + 1 :]
        )
        out_sections.append("\n".join(new_lines))

    result = (preamble + "\n" if preamble else "") + "\n".join(out_sections)
    if not result.endswith("\n"):
        result += "\n"
    with open(MODEL_FILE, "w") as f:
        f.write(result)
    print("Updated yealink_model.txt with firmware= lines.")


if __name__ == "__main__":
    main()
