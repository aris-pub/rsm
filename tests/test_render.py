import subprocess
import sys
from importlib.metadata import version
from textwrap import dedent

import pytest


def cmd(src):
    return " ".join(["rsm", "render", f"'{src}'"])


@pytest.mark.slow
def test_render(tmp_path):
    want = dedent(
        """
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Foo.</p>

        </div>

        <div class="paragraph" data-nodeid="3">

        <p>Bar.</p>

        </div>

        <div class="paragraph" data-nodeid="5">

        <p>Baz.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """
    )
    # In this source code, we use the \r\n line ending typical in Windows systems.  When
    # running this test on a UNIX machine, they will simply be ignored.  When running on
    # a Windows machine, the test will fail if they are not present.
    src = "Foo.\r\n\r\nBar.\r\n\r\nBaz.\r\n"
    file = tmp_path / "test.rsm"
    file.write_text(src)
    result = subprocess.run(
        f"rsm render {str(file.resolve())}",
        stdout=subprocess.PIPE,
        check=True,
        shell=True,
    )

    # get rid of any logs appearing before the html body, and decode
    output = result.stdout[result.stdout.find(b"<body>") :].decode("utf-8")
    if sys.platform == "win32":
        output = output.replace("\r", "")
    assert output.strip() == want.strip()


@pytest.mark.slow
def test_invalid_rsm():
    have = "test_file.rsm"
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run(cmd(have), stdout=subprocess.PIPE, check=True, shell=True)


@pytest.mark.slow
def test_render_version():
    result = subprocess.run(
        "rsm --version", stdout=subprocess.PIPE, check=True, shell=True
    )
    output = result.stdout.decode("utf-8").strip()
    assert output == f"rsm-markup v{version('rsm-markup')}"
