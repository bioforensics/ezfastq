# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of fq. https://github.com/bioforensics/fq
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .copier import FastqCopier
from pathlib import Path


def copy(sample_names, seq_path, prefix="", workdir=Path(".")):
    copier = FastqCopier.from_dir(sample_names, seq_path, prefix=prefix, paired=True)
    copier.copy_files(workdir / "seq")
    copier.print_copy_log()
    nlogs = len(list((workdir / "seq").glob("copy-log-*.toml")))
    with open(workdir / "seq" / f"copy-log-{nlogs + 1}.toml", "w") as fh:
        print(copier, file=fh)
    added_samples = set(fastq.sample for fastq in copier.copied_files)
    added_samples = sorted(added_samples)
    with open(workdir / "samples.txt", "a") as fh:
        print(*added_samples, sep="\n", file=fh)
