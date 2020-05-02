from pathlib import Path

def _get_ext_path() -> Path:
    for file in Path('cogs').glob('**/*.py'):
        *tree, _ = file.parts
        print(tree)
        yield f"{'.'.join(tree)}.{file.stem}"
        
[*_get_ext_path()]