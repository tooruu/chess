from itertools import product

import httpx

for p in map("".join, product("wb", "pnbrqk")):
    r = httpx.get(f"https://images.chesscomfiles.com/chess-themes/pieces/neo/150/{p}.png")
    r.raise_for_status()
    with open(f"resources/pieces/Neo-150/{p}.png", "wb") as f:
        f.write(r.read())
