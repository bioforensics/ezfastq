# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of ezfastq: https://github.com/bioforensics/ezfastq.
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from ezfastq import cli
from importlib.resources import files
from pathlib import Path
import pytest
from subprocess import run

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def test_copy(tmp_path):
    seq_path = files("ezfastq") / "tests" / "data" / "flat"
    arglist = [seq_path, "test1", "test2", "test3", "--workdir", tmp_path]
    cli.main(arglist)
    assert len(list((tmp_path / "seq").glob("*_R?.fastq.gz"))) == 6
    copy_log = tmp_path / "seq" / "copy-log-1.toml"
    with open(copy_log, "rb") as fh:
        log_data = tomllib.load(fh)
    assert len(log_data["CopiedFiles"]) == 6
    assert "SkippedFiles" not in log_data


def test_copy_verbose(tmp_path):
    seq_path = files("ezfastq") / "tests" / "data" / "flat"
    arglist = [seq_path, "test1", "test2", "test3", "--workdir", tmp_path, "--verbose"]
    cli.main(arglist)
    copy_log = tmp_path / "seq" / "copy-log-1.toml"
    with open(copy_log, "rb") as fh:
        log_data = tomllib.load(fh)
    assert "Paths" in log_data
    assert "source" in log_data["Paths"]
    assert "destination" in log_data["Paths"]
    assert Path(log_data["Paths"]["source"]) == seq_path
    assert Path(log_data["Paths"]["destination"]) == tmp_path / "seq"


def test_link(tmp_path):
    seq_path = files("ezfastq") / "tests" / "data" / "flat"
    arglist = [seq_path, "test1", "test2", "--workdir", tmp_path, "--link"]
    cli.main(arglist)
    assert len(list((tmp_path / "seq").glob("*_R?.fastq.gz"))) == 4
    copy_log = tmp_path / "seq" / "copy-log-1.toml"
    with open(copy_log, "rb") as fh:
        log_data = tomllib.load(fh)
    assert len(log_data["LinkedFiles"]) == 4
    assert "CopiedFiles" not in log_data
    assert "SkippedFiles" not in log_data


def test_copy_subdir(tmp_path):
    seq_path = files("ezfastq") / "tests" / "data" / "flat"
    arglist = [seq_path, "test1", "test2", "--workdir", tmp_path, "--subdir", "seq/PROJa/RUNb"]
    cli.main(arglist)
    rundir = tmp_path / "seq" / "PROJa" / "RUNb"
    assert rundir.is_dir()
    assert len(list(rundir.glob("*_R?.fastq.gz"))) == 4


def test_copy_sample_names_file(tmp_path):
    sample_names_file = tmp_path / "sample-names.txt"
    sample_names_file.write_text("test1\ntest3\ntest2\n")
    seq_path = files("ezfastq") / "tests" / "data" / "nested"
    arglist = [seq_path, sample_names_file, "--workdir", tmp_path]
    cli.main(arglist)
    assert len(list((tmp_path / "seq").glob("*_R?.fastq.gz"))) == 6
    copy_log = tmp_path / "seq" / "copy-log-1.toml"
    with open(copy_log, "rb") as fh:
        log_data = tomllib.load(fh)
    assert len(log_data["CopiedFiles"]) == 6
    assert "SkippedFiles" not in log_data


def test_fq_command(tmp_path):
    seq_path = files("ezfastq") / "tests" / "data" / "nested"
    arglist = ["ezfastq", seq_path, "test1", "test2", "test3", "--workdir", tmp_path]
    run(arglist)
    assert len(list((tmp_path / "seq").glob("*_R?.fastq.gz"))) == 6


def test_duplicate_samples(tmp_path):
    seq_path = files("ezfastq") / "tests" / "data" / "flat"
    arglist = [seq_path, "test1", "test2", "test3", "--workdir", tmp_path]
    cli.main(arglist)
    with open(tmp_path / "samples.txt", "r") as fh:
        num_lines = len(fh.readlines())
        assert num_lines == 3
    cli.main(arglist)
    with open(tmp_path / "samples.txt", "r") as fh:
        num_lines = len(fh.readlines())
        assert num_lines == 3
