# -------------------------------------------------------------------------------------------------
# Copyright (c) 2025, DHS. This file is part of ezfastq: https://github.com/bioforensics/ezfastq.
#
# This software was prepared for the Department of Homeland Security (DHS) by the Battelle National
# Biodefense Institute, LLC (BNBI) as part of contract HSHQDC-15-C-00064 to manage and operate the
# National Biodefense Analysis and Countermeasures Center (NBACC), a Federally Funded Research and
# Development Center.
# -------------------------------------------------------------------------------------------------


class NameMap(dict):
    @classmethod
    def from_arglist(cls, arg_list):
        name_map = cls()
        for argument in arg_list:
            old_name, new_name = cls.parse_name(argument, sep=":")
            name_map[old_name] = new_name
        return name_map

    @classmethod
    def from_file(cls, path):
        name_map = cls()
        with open(path, "r") as fh:
            for line in fh:
                if line.strip():
                    old_name, new_name = cls.parse_name(line, sep="\t")
                    name_map[old_name] = new_name
        if len(name_map) == 0:
            raise ValueError(f'sample name file "{path}" is empty')
        return name_map

    @staticmethod
    def parse_name(name_string, sep=":"):
        name_string = name_string.strip()
        num_values = name_string.count(sep) + 1
        if num_values != 1 and num_values != 2:
            message = f'expected 1 or 2 values in sample name, not {num_values}: "{name_string}"'
            raise SampleNameError(message)
        if num_values == 1:
            return name_string, name_string
        else:
            old_name, new_name = name_string.split(sep)
            return old_name, new_name


class SampleNameError(ValueError):
    pass
