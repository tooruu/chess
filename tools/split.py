import re

with open("resources/pieces.svg", "r", newline=None) as pieces:
    while header := pieces.read(209):
        piece = re.sub(r"    <!-- (\w)\w+ (?:k(n)ight|(\w)\w+) -->\n", r"\1\2\3", pieces.readline())
        with open(f"resources/pieces/{piece}.svg", "w", newline="\n") as piece_svg:
            piece_svg.write(header)
            while (line := pieces.readline()) not in {"\n", ""}:
                piece_svg.write(line)
