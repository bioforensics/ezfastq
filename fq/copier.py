# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of fq.
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .fastq import FastqFile
from .map import SampleFastqMap
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
import rich
from rich.panel import Panel
from rich.pretty import Pretty
import sys

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
from typing import List


@dataclass
class FastqCopier:
    """Recursively search a directory for FASTQ files to copy to another.

    FASTQ file names are streamlined in the process, and read pairing status is validated.
    """

    sample_names: List
    copied_files: List
    skipped_files: List
    file_map: SampleFastqMap
    prefix: str = ""

    @classmethod
    def from_dir(cls, sample_names, data_path, prefix="", paired=True):
        copied_files = list()
        skipped_files = list()
        file_map = SampleFastqMap.new(sample_names, data_path, reads_are_paired=paired)
        copier = cls(sorted(sample_names), copied_files, skipped_files, file_map, prefix)
        return copier

    def copy_files(self, destination):
        for fastq in self:
            was_copied = fastq.check_and_copy(destination)
            if was_copied:
                self.copied_files.append(fastq)
            else:
                self.skipped_files.append(fastq)

    def print_copy_log(self, outstream=sys.stderr):
        log_data = tomllib.loads(str(self))
        pretty = Pretty(log_data)
        panel = Panel(pretty, expand=False, title="FASTQ Copy Log", title_align="right")
        rich.print(panel, file=outstream)

    def __iter__(self):
        for sample_name, fqfiles in sorted(self.file_map.items()):
            for n, fqfile in enumerate(fqfiles, 1):
                source_path = Path(fqfile).absolute()
                yield FastqFile(source_path, sample_name, n, self.prefix)

    def __str__(self):
        output = StringIO()
        if len(self.copied_files) > 0:
            print("[UpdatedFileNames]", file=output)
            for fastq in self.copied_files:
                print(fastq, file=output)
        if len(self.skipped_files) > 0:
            print("\n[SkippedFileNames]\nalready_processed = [", file=output)
            for fastq in self.skipped_files:
                print(f'    "{fastq.source_path.name}",', file=output)
            print("]", file=output)
        return output.getvalue()
