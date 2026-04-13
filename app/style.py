# Shared visual constants used across pages.

# FDR colour scheme: maps fixture difficulty rating (1-5) to (background, foreground).
FDR_COLOURS: dict[int, tuple[str, str]] = {
    1: ("darkgreen", "white"),
    2: ("#09fc7b", "black"),
    3: ("#e7e7e8", "black"),
    4: ("#ff1651", "white"),
    5: ("#80072d", "white"),
}
