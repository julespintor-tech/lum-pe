# Contributing to LUM-PE

Thank you for your interest in contributing! LUM-PE is an open framework and community contributions are welcome.

## Ways to Contribute

- **Bug reports:** Open an issue describing the problem, your environment, and steps to reproduce.
- **New domain packs:** Add a new `Pack` subclass under `lum_pe/packs/impl.py` and register it in `lum_pe/packs/registry.py`.
- **Index extractors:** Implement real extractors for IPU/CPV/A*/κ_conf/Cons/Conf/Coverage/Shadow.
- **Documentation:** Improve README, add docstrings, translate to other languages.
- **Tests:** Add unit or integration tests under `tests/`.

## Development Setup

```bash
git clone https://github.com/julespintor-tech/lum-pe.git
cd lum-pe
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/
```

## Code Style

- Follow PEP 8.
- Use type hints throughout.
- Every public function must have a docstring.

## Pull Request Process

1. Fork the repo and create a feature branch: `git checkout -b feature/my-pack`
2. Make your changes with tests.
3. Run `pytest tests/` and confirm all pass.
4. Open a PR with a clear description of what changes you made and why.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
