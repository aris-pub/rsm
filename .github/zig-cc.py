"""C compiler for CI jobs that run in the Playwright image, which has no gcc.

The image ships Chromium and its system libraries, so those jobs skip the slow
apt install, but tree-sitter-rsm is built from source and needs a compiler.
This runs zig's C compiler (from the ziglang pip package) and drops the one GNU
linker flag that zig's linker rejects.
"""

import subprocess
import sys

args = [a for a in sys.argv[1:] if not a.startswith("-Wl,--exclude-libs")]
sys.exit(subprocess.call(["/usr/bin/python3", "-m", "ziglang", "cc", *args]))
