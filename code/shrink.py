"""

Randomly select documents from a directory and create a smaller directory from it.

Usage:

$ python shrink.py --source DIR1 --target DIR2 --size N

The input directory DIR1 should have subdirectories "scienceparse" and "text" and
optionally a file "metadata.json". The output directory DIR2 will have the same
structure, but with only N documents per subdirectory. Both subdirectories in DIR2
have documents with the same identifiers.

"""

import os, sys, shutil, json, random, argparse
import utils


SCIENCEPARSE_DIR = 'scienceparse'
TEXT_DIR = 'text'
METADATA_FILE = 'metadata.json'


def parse_args():
    parser = argparse.ArgumentParser(description='Randomly shrinking a directory')
    parser.add_argument('--source', help="source directory")
    parser.add_argument('--target', help="target directory")
    parser.add_argument('--size', help="desired size of target directory", type=int)
    return parser.parse_args()


def shrink(indir: str, outdir: str, size: int):
    """Randomly select {size} documents from the text and scienceparse subdirectories
    in {indir} and copy them to {outdir}, while preserving structure. This also makes
    sure that both subdirectories have documents with the same identifiers."""
    print(f'>>> Shrinking {indir} to {size} documents')
    os.makedirs(os.path.join(outdir, TEXT_DIR), exist_ok=True)
    os.makedirs(os.path.join(outdir, SCIENCEPARSE_DIR), exist_ok=True)
    text_path = os.path.join(indir, TEXT_DIR)
    selection = _get_selection(os.listdir(text_path), size)
    for scpa_file, text_file in selection.values():
        source_scpa = os.path.join(indir, SCIENCEPARSE_DIR, scpa_file)
        source_text = os.path.join(indir, TEXT_DIR, text_file)
        target_scpa = os.path.join(outdir, SCIENCEPARSE_DIR, scpa_file)
        target_text = os.path.join(outdir, TEXT_DIR, text_file)
        # print(f'{source_text} --> {target_text}')
        shutil.copyfile(source_text, target_text)
        # it is not guaranteed that there is a ScienceParse file for each text file
        try:
            shutil.copyfile(source_scpa, target_scpa)
        except FileNotFoundError:
            print(f"WARNING: there was no SCPA file for {source_text}")
    _shrink_metadata(indir, outdir, selection)
    _write_readme(indir, outdir, size, selection)
    print(f'>>> Results were written to {outdir}/')


def _get_selection(text_files: list, n: int) -> dict:
    """Return a dictionary indexed on identifiers where values are pairs of
    basenames <scpa_file, text_file>."""
    ids = [utils.trim_filename(f, '.txt') for f in text_files]
    random_ids = set()
    while len(random_ids) < n:
        random_ids.add(random.choice(ids))
    selection = {}
    for identifier in random_ids:
        selection[identifier] = (f'{identifier}_input.pdf.json', f'{identifier}.txt')
    return selection

def _shrink_metadata(indir: str, outdir: str, selection: dict):
    try:
        meta_in = json.load(open(os.path.join(indir, METADATA_FILE)))
        meta_out = [record for record in meta_in if record["_gddid"] in selection]
        with open(os.path.join(outdir, METADATA_FILE), 'w') as fh:
            json.dump(meta_out, fh, indent=4)
    except FileNotFoundError:
        print("WARNING: there was no metadata file")


def _write_readme(indir, outdir, size, selection):
    with open(os.path.join(outdir, 'readme.txt'), 'w') as fh:
        fh.write(f'$ python {" ".join(sys.argv)}\n\n')
        for scpa_file, text_file in selection.values():
            fh.write(f'{text_file[:-4]}\n')


if __name__ == '__main__':

    args = parse_args()
    shrink(args.source, args.target, args.size)
