# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of ezfastq: https://github.com/bioforensics/ezfastq.
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .fastq import FastqFile
from .map import SampleFastqMap
from .namemap import NameMap
from .pair import PairMode
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
import rich
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.syntax import Syntax
import sys
from typing import List


@dataclass
class FastqCopier:
    """Recursively search a directory for FASTQ files to copy to another.

    FASTQ file names are streamlined in the process, and read pairing status is validated.
    """

    sample_name_map: NameMap
    copied_files: List
    skipped_files: List
    file_map: SampleFastqMap
    prefix: str = ""
    link: bool = False

    @classmethod
    def from_dir(
        cls, sample_name_map, data_path, prefix="", pair_mode=PairMode.Unspecified, link=False
    ):
        copied_files = list()
        skipped_files = list()
        file_map = SampleFastqMap.new(sample_name_map.keys(), data_path, pair_mode=pair_mode)
        copier = cls(sample_name_map, copied_files, skipped_files, file_map, prefix, link)
        return copier

    def copy_files(self, destination):
        progress = self.get_progress_tracker()
        progress.console.log(f"Copying {len(self)} FASTQ files")
        with progress:
            task = progress.add_task("[bold red]Copying...", total=len(self))
            for fastq in self:
                # There's an exact, closed-form solution to the problem addressed in the next few
                # lines that would involve str.format. I also think it would be much more difficult
                # to interpret that code's intent. -- DSS, 2025-05-27
                llsn = self.length_longest_sample_name
                if llsn < 8:
                    desc = f"[bold red]{fastq.sample:>8s} R{fastq.read}"
                elif llsn < 12:
                    desc = f"[bold red]{fastq.sample:>12s} R{fastq.read}"
                else:
                    desc = f"[bold red]{fastq.sample:>16s} R{fastq.read}"
                progress.update(task, description=desc)
                was_copied = fastq.check_and_copy(destination, link=self.link)
                progress.update(task, advance=1)
                if was_copied:
                    self.copied_files.append(fastq)
                else:
                    self.skipped_files.append(fastq)
            progress.update(task, description="[bold red]Finished!")

    @staticmethod
    def get_progress_tracker():
        return Progress(
            SpinnerColumn(),
            TextColumn("[bold red]{task.description}", justify="right"),
            BarColumn(complete_style="green"),
            TextColumn("[bold red]{task.percentage:>5.1f}%", justify="right"),
            TextColumn("[yellow]Time elapsed:"),
            TimeElapsedColumn(),
            TextColumn("[cyan]Est. time remaining:"),
            TimeRemainingColumn(compact=True),
            refresh_per_second=1,
        )

    def print_copy_log(self, outstream=sys.stderr):
        syntax = Syntax(str(self), "toml", theme="solarized-dark")
        panel = Panel(syntax, expand=False, title="FASTQ Copy Log", title_align="right")
        rich.print(panel, file=outstream)

    @property
    def length_longest_sample_name(self):
        return max(len(sample) for sample in self.sample_name_map.keys())

    def __len__(self):
        return sum(len(fqfiles) for fqfiles in self.file_map.values())

    def __iter__(self):
        for sample_name, fqfiles in sorted(self.file_map.items()):
            for n, fqfile in enumerate(fqfiles, 1):
                source_path = Path(fqfile).absolute()
                read = 0 if len(fqfiles) == 1 else n
                new_name = self.sample_name_map[sample_name]
                yield FastqFile(source_path, new_name, read, self.prefix)

    def __str__(self):
        output = StringIO()
        if len(self.copied_files) > 0:
            header = "[LinkedFiles]" if self.link else "[CopiedFiles]"
            print(header, file=output)
            for fastq in self.copied_files:
                print(fastq, file=output)
        if len(self.skipped_files) > 0:
            key = "linked" if self.link else "copied"
            print(f"\n[SkippedFiles]\nalready_{key} = [", file=output)
            for fastq in self.skipped_files:
                print(f'    "{fastq.source_path.name}",', file=output)
            print("]", file=output)
        return output.getvalue().strip()
