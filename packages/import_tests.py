from pathlib import Path

from typing import List
import yaml

def gen(packages: List[str], packages_dir = Path("packages")):
    res = {}
    for package in packages:
        try:
            with open(packages_dir / package / "meta.yaml", "r") as file:
                imports = set()
                meta = yaml.load(file, Loader=yaml.FullLoader)
                # add package -> top-level if it exists
                if "package" in meta:
                    if "top-level" in meta["package"]:
                        imports.update(meta["package"]["top-level"])
                # add test -> imports if it exists
                if "test" in meta:
                    if "imports" in meta["test"]:
                        imports.update(meta["test"]["imports"])
                
                if len(imports) > 0:
                    res[package] = list(imports)
        except FileNotFoundError:
            pass
    return res