set -euo pipefail
cd "$(dirname "$0")/.."
pytest --cov --cov-report=term-missing --cov-report=xml --cov-report=html "$@"
