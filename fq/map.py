# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of fq. https://github.com/bioforensics/fq
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------

from .scanner import FastqFileScanner
from collections import defaultdict


class SampleFastqMap(defaultdict):
    "Map sample names to lists of corresponding FASTQ files."

    @classmethod
    def new(cls, sample_names, data_path, reads_are_paired=True):
        files_by_sample = cls(list)
        scanner = FastqFileScanner.new(sample_names)
        for sample_name, fastq in scanner.scan(data_path):
            files_by_sample[sample_name].append(fastq)
            files_by_sample[sample_name].sort()
        cls.validate_sample_files(sample_names, files_by_sample, reads_are_paired=reads_are_paired)
        return files_by_sample

    @staticmethod
    def validate_sample_files(sample_names, files_by_sample, reads_are_paired=True):
        for sample in sample_names:
            file_list = files_by_sample[sample]
            num_files = len(file_list)
            if num_files == 0:
                raise FileNotFoundError(f"sample {sample}: found 0 FASTQ files")
            if reads_are_paired:
                exp_num_fastq_files = 2
                mode = "paired"
            else:
                exp_num_fastq_files = 1
                mode = "single"
            if num_files != exp_num_fastq_files:
                message = f"sample {sample}: found {num_files} FASTQ files, expected {exp_num_fastq_files} in {mode}-end mode"
                raise ValueError(message)
