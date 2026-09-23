# El cielo de Lior

The Python scripts behind Semilla Cósmica — my little star-map and natal-chart shop. Every image I sell is rendered locally from real ephemeris (pyswisseph + skyfield), no stock art, no stock sky.

## Scripts

| script | what it does |
|---|---|
| `scripts/carta_wheel.py` | Natal chart wheel: real ephemeris positions, houses, aspect lines, drawn with PIL |
| `scripts/cielo_cuadrado.py` | Square birth-sky maps: real star field (HYG catalog), constellation lines, the Moon with its correct phase |
| `scripts/poster_a3.py` | A3 poster renderer for the printed star-map listings |
| `scripts/cielo_momento.py` | Skies of a specific moment — a date, a place, a real sky |
| `scripts/eventos_2026_27.py` | Astronomical events for 2026-27 (meteor showers, full moons) that feed the event posters |
| `scripts/cuaderno.py` | Build-your-own workbook/notebook pages |
| `scripts/frame_mockup.py` | Product mockups (framed prints) via PIL |

## Data files (not committed, downloaded separately)

- `hygdata_v41.csv` — HYG star catalog
- `constellationship.fab` — constellation line data (Stellarium)
- Swiss ephemeris `.se1` files

## Notes

Ephemeris work: RA is in hours (×15 to degrees), negative RA wraps with `%360`, lunar phase k = (1+cos|180−elong|)/2. Every render is QA'd numerically before it becomes a product.
