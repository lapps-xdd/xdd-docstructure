"""

Randomly select documents from the full corpus and create a smaller corpus from it.

This is mostly so that we can play with the code without needing oodles of disk space
(the text directory is about 5GB and the ScienceParse directory is about 6GB).

Usage:

$ python shrink n

The shrunken corpus is written to the base directory (config.BASE_DIR) and includes
all four domains.

"""

import os, sys, shutil, random

import utils
import config


def print_corpus():
    for name, index in [('TEXT', config.text_directories_idx()),
                        ('SCPA', config.scpa_directories_idx())]:
        print(f'\n{name}\n')
        for domain, path in index.items():
            file_count = len(os.listdir(path))
            print(f'    {domain:4}  ==>  {file_count:-6d}  {path}')
    print()


def shrink(domain, text_path, scpa_path, requested_size, output_dir: str):
    print(f'>>> Shrinking domain {domain} to {requested_size} documents')
    print(f'--- text path = {text_path}')
    print(f'--- scpa path = {scpa_path}')
    text_files = os.listdir(text_path)
    scpa_files = os.listdir(scpa_path)
    text_files_names = [utils.trim_filename(f, '.txt') for f in text_files]
    scpa_files_names = [utils.trim_filename(f, '_input.pdf.json') for f in scpa_files]
    print(f'--- example text file : {text_files_names[0]} <-- {text_files[0]}')
    print(f'--- example scpa file : {scpa_files_names[0]} <-- {scpa_files[0]}')
    print(type(text_files), text_files)
    selection = _get_selection(text_files, requested_size)
    text_files_selection = [f'{f}.txt' for f in selection]
    scpa_files_selection = [f'{f}_input.pdf.json' for f in selection]
    selection = list(zip(text_files_selection, scpa_files_selection))
    _create_directory_structure(output_dir)
    for text_file, scpa_file in selection:
        new_text_path = text_path[len(config.DATA_DIR) + 1:]
        new_text_path = os.path.join(output_dir, new_text_path, text_file)
        new_scpa_path = scpa_path[len(config.DATA_DIR) + 1:]
        new_scpa_path = os.path.join(output_dir, new_scpa_path, scpa_file)
        text_file = os.path.join(text_path, text_file)
        scpa_file = os.path.join(scpa_path, scpa_file)
        print(text_file)
        new_text_dir = os.path.split(new_text_path)[0]
        new_scpa_dir = os.path.split(new_scpa_path)[0]
        for new_dir in (new_text_dir, new_scpa_dir):
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
        shutil.copyfile(text_file, new_text_path)
        shutil.copyfile(scpa_file, new_scpa_path)


def _get_selection(text_files: list, n: int):
    text_files = [utils.trim_filename(f, '.txt') for f in text_files]
    # use a set so we avoid duplicates
    text_files_selection = set()
    while len(text_files_selection) < n:
        text_files_selection.add(random.choice(text_files))
    return list(sorted(text_files_selection))


def _create_directory_structure(output_dir: str):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


if __name__ == '__main__':

    requested_size = int(sys.argv[1])
    output_directory = os.path.join(
        config.DATA_DIR, f'shrunk-{requested_size:04d}-{utils.timestamp()}')
    for domain in config.DOMAINS:
        shrink(domain,
               config.text_directories_idx()[domain],
               config.scpa_directories_idx()[domain],
               requested_size, output_directory)
