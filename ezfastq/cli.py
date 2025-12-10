# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of ezfastq: https://github.com/bioforensics/ezfastq.
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .api import copy
from .namemap import NameMap
from .pair import PairMode
from argparse import ArgumentParser
from importlib.metadata import version
from pathlib import Path
from rich.text import Text
from rich_argparse import RawDescriptionRichHelpFormatter
from shutil import get_terminal_size


def main(arglist=None):
    args = parse_args(arglist)
    copy(
        args.samples,
        args.seq_path,
        pair_mode=args.pair_mode,
        prefix=args.prefix,
        workdir=args.workdir,
        subdir=args.subdir,
        verbose=args.verbose,
    )


def parse_args(arglist=None):
    if arglist:  # pragma: no cover
        arglist = map(str, arglist)
    args = get_parser().parse_args(arglist)
    samples_file = Path(args.samples[0])
    samples_file_exists = samples_file.is_file() or samples_file.is_fifo()
    if len(args.samples) == 1 and samples_file_exists:
        args.samples = NameMap.from_file(samples_file)
    else:
        args.samples = NameMap.from_arglist(args.samples)
    args.pair_mode = PairMode(args.pair_mode)
    return args


def get_parser():
    epilog = """
[bold cyan]Examples:[/bold cyan]
    [dim]ezfastq /path/to/fastqs/ sample1 sample2 sample3
    ezfastq /path/to/fastqs/ s1:Sample1 s2:Sample2 s3:Sample3
    ezfastq /path/to/fastqs/ samplenames.txt
    ezfastq /path/to/fastqs/ samplenames.txt --workdir /path/to/projectdir/ --subdir seq/Run01/
    ezfastq /path/to/fastqs/ samplenames.txt --pair-mode 2[/dim]
"""
    width = min(99, get_terminal_size().columns - 2)
    parser = ArgumentParser(
        description="Copy FASTQ files and use sample names to make filenames consistent",
        formatter_class=lambda prog: RawDescriptionRichHelpFormatter(prog, width=width),
        epilog=epilog,
    )
    parser.add_argument(
        "seq_path",
        help="path to directory containing sequences in FASTQ format; subdirectories will be searched recursively",
    )
    parser.add_argument(
        "samples",
        nargs="+",
        help="name of one or more samples to process; samples can optionally be renamed by appending a colon and new name to each sample name; alternatively, sample names can be provided as a file with one sample name per line, or two tab-separated values to rename samples",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"ezfastq v{version('ezfastq')}",
    )
    parser.add_argument(
        "-w",
        "--workdir",
        metavar="PATH",
        type=Path,
        default=Path("."),
        help="project directory to which input files will be copied and renamed; current directory is used by default",
    )
    parser.add_argument(
        "-s",
        "--subdir",
        metavar="PATH",
        default="seq",
        help="subdirectory path under --workdir to which sequence files will be written; PATH=`seq` by default, but can contain nesting (e.g. `seq/study`)",
    )
    parser.add_argument(
        "-p",
        "--prefix",
        metavar="P",
        default="",
        help="prefix to prepend to sample names; resulting file path will be '{workdir}/seq/{prefix}_{sample}_R{1,2}.fastq.gz'",
    )
    parser.add_argument(
        "-m",
        "--pair-mode",
        metavar="M",
        type=int,
        choices=[0, 1, 2],
        default=0,
        help="specify 1 to indicate that all samples are single-end, or 2 to indicate that all samples are paired-end; by default, read layout is inferred automatically on a per-sample basis",
    )
    parser.add_argument(
        "-V",
        "--verbose",
        action="store_true",
        help="include source and destination in copy log",
    )
    return parser
