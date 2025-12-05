#!/usr/bin/env python3
"""Patch notebook to remove problematic metadata.widgets entries and update training args.

Usage: python scripts/patch_notebook.py [--nb path]
"""
import json
import re
import sys
from pathlib import Path


def load_nb(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_nb(path, nb):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)


def fix_widgets(nb):
    changed = False
    for cell in nb.get('cells', []):
        meta = cell.get('metadata', {})
        if 'widgets' in meta:
            # remove to avoid missing 'state' error in GitHub viewer
            del meta['widgets']
            cell['metadata'] = meta
            changed = True
    return changed


def update_training_args(nb):
    changed = False
    for cell in nb.get('cells', []):
        if cell.get('cell_type') != 'code':
            continue
        src = ''.join(cell.get('source', []))
        new_src = src

        # Update OUTPUT_DIR assignments
        new_src = re.sub(r"OUTPUT_DIR\s*=\s*[\"'].*?[\"']", 'OUTPUT_DIR = "/content/checkpoints/granite-ft"', new_src)

        # Replace common hyperparams
        new_src = new_src.replace('learning_rate=2e-4', 'learning_rate=5e-5')
        new_src = new_src.replace('gradient_accumulation_steps=4', 'gradient_accumulation_steps=8')
        new_src = new_src.replace('fp16=True', 'fp16=False')
        new_src = new_src.replace('fp16 = True', 'fp16 = False')
        new_src = new_src.replace('max_grad_norm=0.0', 'max_grad_norm=1.0')
        new_src = new_src.replace('max_grad_norm = 0.0', 'max_grad_norm = 1.0')

        # Ensure save strategy settings exist inside TrainingArguments
        if 'TrainingArguments' in new_src and 'save_strategy' not in new_src:
            new_src = new_src.replace('TrainingArguments(', 'TrainingArguments(\n    save_strategy="steps",\n    save_steps=1000,\n    save_total_limit=1,')

        if new_src != src:
            cell['source'] = [new_src]
            changed = True

    return changed


def main():
    nb_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('notebooks/granite_fine_tuning_colab.ipynb')
    if not nb_path.exists():
        print('Notebook not found:', nb_path)
        sys.exit(2)

    nb = load_nb(nb_path)
    a = fix_widgets(nb)
    b = update_training_args(nb)

    if a or b:
        save_nb(nb_path, nb)
        print(f'Patched notebook: widgets_removed={a}, training_args_updated={b}')
        sys.exit(0)
    else:
        print('No changes necessary')
        sys.exit(0)


if __name__ == '__main__':
    main()
