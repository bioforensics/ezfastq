# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of MAnaT: https://maestro.dhs.gov/gitlab-ce/nbfac/manat
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .copier import FastqCopier
from argparse import ArgumentParser
from importlib.metadata import version
from pathlib import Path


def main(arglist=None):
    args = parse_args(arglist)
    copier = FastqCopier.from_dir(args.samples, args.seq_path, prefix=args.prefix, paired=True)
    copier.copy_files(args.workdir / "seq")
    write_logs(copier, args.workdir)


def write_logs(copier, workdir):
    copier.print_copy_log()
    nlogs = len(list((workdir / "seq").glob("copy-log-*.toml")))
    with open(workdir / "seq" / f"copy-log-{nlogs + 1}.toml", "w") as fh:
        print(copier, file=fh)
    added_samples = set(fastq.sample for fastq in copier.copied_files)
    added_samples = sorted(added_samples)
    with open(workdir / "samples.txt", "a") as fh:
        print(*added_samples, sep="\n", file=fh)


def parse_args(arglist=None):
    if arglist:
        arglist = map(str, arglist)
    args = get_parser().parse_args(arglist)
    samples_file = Path(args.samples[0])
    samples_file_exists = samples_file.is_file() or samples_file.is_fifo()
    if len(args.samples) == 1 and samples_file_exists:
        args.samples = samples_file.read_text().strip().split("\n")
    return args


def get_parser():
    parser = ArgumentParser(description="Copy FASTQ files and update sample names")
    parser.add_argument(
        "seq_path",
        help="path to directory containing sequences in FASTQ format; subdirectories will be searched recursively",
    )
    parser.add_argument(
        "samples",
        nargs="+",
        help="name of one or more samples to process; can be provided as command-line arguments or as a file with one sample name per line",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"fq v{version('fq')}",
    )
    parser.add_argument(
        "-w",
        "--workdir",
        metavar="WD",
        type=Path,
        default=Path("."),
        help="directory to which input files will be copied and renamed",
    )
    parser.add_argument(
        "-p",
        "--prefix",
        metavar="P",
        default="",
        help="prefix to prepend to sample names; resulting file path will be '{workdir}/seq/{prefix}_{sample}_R{1,2}.fastq.gz'",
    )
    return parser
