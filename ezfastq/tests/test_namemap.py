# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of ezfastq: https://github.com/bioforensics/ezfastq.
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from ezfastq.namemap import NameMap, SampleNameError
import pytest


@pytest.mark.parametrize(
    "arglist,expected",
    [
        (["s1", "s2", "s3"], {"s1": "s1", "s2": "s2", "s3": "s3"}),
        (["s1:Sample1", "s2:Sample2"], {"s1": "Sample1", "s2": "Sample2"}),
        (
            ["1-1:99-12-005-1-1", "99-12-005-1-2", "1-3:99-12-005-1-3"],
            {"1-1": "99-12-005-1-1", "99-12-005-1-2": "99-12-005-1-2", "1-3": "99-12-005-1-3"},
        ),
    ],
)
def test_name_map_from_arglist(arglist, expected):
    observed = NameMap.from_arglist(arglist)
    assert observed == expected


def test_name_map_bad_arglist():
    arglist = ["s1:Sample:1", "s2:Sample:2", "s3:Sample:3"]
    message = 'expected 1 or 2 values in sample name, not 3: "s1:Sample:1"'
    with pytest.raises(SampleNameError, match=message):
        NameMap.from_arglist(arglist)


def test_name_map_from_empty_arglist():
    namemap = NameMap.from_arglist([])
    assert len(namemap) == 0


@pytest.mark.parametrize(
    "contents,expected",
    [
        ("s1\ns2\ns3", {"s1": "s1", "s2": "s2", "s3": "s3"}),
        (
            "1-1\t99-12-005-1-1\n1-2\t99-12-005-1-2\n1-3\t99-12-005-1-3",
            {"1-1": "99-12-005-1-1", "1-2": "99-12-005-1-2", "1-3": "99-12-005-1-3"},
        ),
    ],
)
def test_name_map_from_file(contents, expected, tmp_path):
    mapfile = tmp_path / "map_file.txt"
    mapfile.write_text(contents)
    observed = NameMap.from_file(mapfile)
    assert observed == expected


def test_name_map_from_empty_file(tmp_path):
    mapfile = tmp_path / "map_file.txt"
    mapfile.touch()
    with pytest.raises(ValueError, match=r"sample name file .* is empty"):
        NameMap.from_file(mapfile)
