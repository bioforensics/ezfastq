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
    def from_list(cls, name_list):
        name_map = cls()
        for value in name_list:
            num_fields = value.count(":")
            if num_fields != 1 and num_fields != 2:
                message = f"expected 1 or 2 values in sample name, not {num_fields}"
                raise ValueError(message)
            if num_fields == 1:
                name_map[value] = value
            else:
                old_name, new_name = value.split(":")
                name_map[old_name] = new_name
        return name_map

    @classmethod
    def from_file(cls, path):
        name_map = cls()
        with open(path, "r") as fh:
            for line in fh:
                line = line.strip()
                num_columns = line.count("\t") + 1
                if num_columns != 1 and num_columns != 2:
                    message = f"expected 1 or 2 columns in sample name file, not {num_columns}"
                    raise ValueError(message)
                if num_columns == 1:
                    name_map[line] = line
                else:
                    old_name, new_name = line.split("\t")
                    name_map[old_name] = new_name
        if len(name_map) == 0:
            raise ValueError(f"sample name file {path} is empty")
        return name_map
