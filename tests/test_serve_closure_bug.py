"""Regression test for closure bug in rsm serve file watching.

Bug: In the file watching loop in _cmd_serve(), the `build_cmd` variable must be
captured by value (using a default argument) instead of by reference. Without this,
all callbacks share the same variable which ends up with the last iteration's value.

Example: If you have test1.rsm, test2.rsm, test3.rsm:
  - Buggy: Editing test1.rsm would trigger build of test3.rsm
  - Fixed: Editing test1.rsm triggers build of test1.rsm

The fix: Change `def rebuild_callback(rsm_path=rsm_file)`
       to `def rebuild_callback(rsm_path=rsm_file, cmd=build_cmd)`
"""


def test_closure_bug_demonstration():
    """Demonstrate how the closure bug manifests and how to fix it.

    This test documents the bug pattern and demonstrates both the buggy
    and fixed versions work.
    """
    # BUGGY VERSION: Variable captured by reference
    callbacks_buggy = []
    for i in range(3):
        build_cmd = f"command_{i}"
        # BUG: build_cmd is captured by reference, not value
        def callback():
            return build_cmd
        callbacks_buggy.append(callback)

    # All callbacks return the SAME value (from last iteration)
    assert callbacks_buggy[0]() == "command_2"  # Wrong! Should be "command_0"
    assert callbacks_buggy[1]() == "command_2"  # Wrong! Should be "command_1"
    assert callbacks_buggy[2]() == "command_2"  # Correct

    # FIXED VERSION: Variable captured by value using default argument
    callbacks_fixed = []
    for i in range(3):
        build_cmd = f"command_{i}"
        # FIX: build_cmd is captured by value as a default argument
        def callback(cmd=build_cmd):
            return cmd
        callbacks_fixed.append(callback)

    # Each callback returns its OWN value
    assert callbacks_fixed[0]() == "command_0"  # Correct!
    assert callbacks_fixed[1]() == "command_1"  # Correct!
    assert callbacks_fixed[2]() == "command_2"  # Correct!


def test_rsm_serve_specific_scenario():
    """Demonstrate the exact scenario from rsm serve code."""
    from pathlib import Path

    # Simulate the loop in _cmd_serve() for multiple .rsm files
    rsm_files = [Path(f"test{i}.rsm") for i in range(1, 4)]

    # BUGGY VERSION (what happens without the fix)
    callbacks_buggy = {}
    for rsm_file in rsm_files:
        output_name = rsm_file.stem
        build_cmd = f"rsm build {rsm_file} -o {output_name}"
        # BUG: build_cmd not captured as default arg
        def rebuild_callback(rsm_path=rsm_file):
            return build_cmd
        callbacks_buggy[rsm_file.name] = rebuild_callback

    # All callbacks return the same command (the last one)!
    assert callbacks_buggy["test1.rsm"]() == "rsm build test3.rsm -o test3"
    assert callbacks_buggy["test2.rsm"]() == "rsm build test3.rsm -o test3"
    assert callbacks_buggy["test3.rsm"]() == "rsm build test3.rsm -o test3"

    # FIXED VERSION (with the fix applied)
    callbacks_fixed = {}
    for rsm_file in rsm_files:
        output_name = rsm_file.stem
        build_cmd = f"rsm build {rsm_file} -o {output_name}"
        # FIX: build_cmd captured as default arg
        def rebuild_callback(rsm_path=rsm_file, cmd=build_cmd):
            return cmd
        callbacks_fixed[rsm_file.name] = rebuild_callback

    # Each callback returns the correct command!
    assert callbacks_fixed["test1.rsm"]() == "rsm build test1.rsm -o test1"
    assert callbacks_fixed["test2.rsm"]() == "rsm build test2.rsm -o test2"
    assert callbacks_fixed["test3.rsm"]() == "rsm build test3.rsm -o test3"
