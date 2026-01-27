from pathlib import Path

from kaitai_pretty_print import _render_file


def test_pretty_print_matches_snapshot():
    from soudan import Soudan

    snapshot_path = Path("kaitai_pretty_print.md")
    snapshot = snapshot_path.read_text()

    with open("minimal_sample.soudan", "rb") as infile:
        data = Soudan.from_io(infile)

    rendered = _render_file(data, max_records=None)
    assert rendered == snapshot
