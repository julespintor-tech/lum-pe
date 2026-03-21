# Dev notes

Run:
- pip install -e .
- lum run --problem "..." --input examples/container_nat_general.json --payload examples/payload_nat_general.json --out out_bundle.json
- lum validate --bundle out_bundle.json

Run tests:
- python -m pytest -q

No external dependencies by default.
