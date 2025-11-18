#!/usr/bin/env python3

from utils import find_dataparser_transforms_file
import argparse
import sys


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find the dataparser transforms file.")
    parser.add_argument("search_dir", type=str, help="Directory to search.")
    args = parser.parse_args()

    file_path = find_dataparser_transforms_file(args.search_dir)
    print(file_path)
