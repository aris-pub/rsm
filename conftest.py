# conftest.py - pytest configuration for the entire project

# Import doctest setup to register custom IGNORE_RESULT flag
# This must be imported before pytest collects doctests
import sys
from pathlib import Path

# Add docs/source to path to import doctest_setup
docs_source = Path(__file__).parent / "docs" / "source"
sys.path.insert(0, str(docs_source))

# Import to register the custom doctest flag
import doctest_setup  # noqa: F401
