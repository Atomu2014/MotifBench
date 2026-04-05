from pathlib import Path

def count_items_in_subdirs(root_dir: str) -> None:
    root = Path(root_dir)

    if not root.is_dir():
        raise ValueError(f"Not a valid directory: {root_dir}")

    for subdir in sorted(root.iterdir()):
        if subdir.is_dir():
            count = sum(1 for _ in subdir.iterdir())
            print(f"{subdir.name}: {count}")

# example
count_items_in_subdirs("output_ppflow")
