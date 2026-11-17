"""Regression tests for executable README examples."""

import re
import shlex
from pathlib import Path

from evo.cli import ape, ape_parser
from evo.tools import file_interface


def test_readme_monocular_ape_corrects_scale(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    readme = (root / "README.md").read_text(encoding="utf-8")
    commands = [
        shlex.split(block.replace("\\\n", ""), comments=True)
        for block in re.findall(r"```bash\n(.*?)```", readme, re.DOTALL)
    ]
    monocular_commands = [
        command
        for command in commands
        if command[:2] == ["evo_ape", "tum"]
        and "freiburg1_xyz-ORB_kf_mono.txt" in command
    ]
    assert len(monocular_commands) == 1
    args = ape_parser.parser().parse_args(monocular_commands[0][1:])
    # Resolve the example's data paths without changing the process directory.
    args.ref_file = str(root / "test" / "data" / args.ref_file)
    args.est_file = str(root / "test" / "data" / args.est_file)
    args.save_results = str(tmp_path / "ORB.zip")
    ape.run(args)

    result = file_interface.load_res_file(args.save_results)
    assert "Sim(3)" in result.info["title"]
    # With SE(3) alone this fixture has an RMSE of about 0.0243 m.
    assert 0.009 < result.stats["rmse"] < 0.011
