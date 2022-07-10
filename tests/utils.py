# Copyright (c) 2021 Shuhei Nitta. All rights reserved.
import os
import shutil


def create_go_pkg(package_path: str) -> None:
    os.makedirs(package_path)
    main = os.path.join(package_path, "main.go")
    with open(main, "w") as f:
        f.write(f"package pkg{os.path.basename(package_path)}")


def clean_up_go_pkg(package_path: str) -> None:
    if os.path.exists("go.sum"):
        os.unlink("go.sum")
    if os.path.exists(package_path):
        shutil.rmtree(package_path)
