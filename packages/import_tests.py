from pathlib import Path

from pyodide_build.recipe.spec import MetaConfig

def gen(packages: list[str], packages_dir: Path = Path("packages")) -> dict[str, list[str]]:
    res = {}
    for package in packages:
        if package == "test":
            continue
        try:
            meta = MetaConfig.from_yaml(packages_dir / package / "meta.yaml")
        except FileNotFoundError:
            print(f"package {package}'s meta.yaml not found")

        imports = set()
        # add package -> top-level if it exists
        imports.update(meta.package.top_level)
        imports.update(meta.test.imports)
        if imports:
            res[package] = sorted(list(imports))

    return res
