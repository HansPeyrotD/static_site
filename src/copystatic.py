import os
import shutil


def copy_directory(source: str, destination: str) -> None:
    if os.path.exists(destination):
        shutil.rmtree(destination)
    os.mkdir(destination)
    _copy_contents(source, destination)


def _copy_contents(source: str, destination: str) -> None:
    for name in os.listdir(source):
        source_path = os.path.join(source, name)
        destination_path = os.path.join(destination, name)
        if os.path.isfile(source_path):
            print(f"Copying {source_path} -> {destination_path}")
            shutil.copy(source_path, destination_path)
        else:
            os.mkdir(destination_path)
            _copy_contents(source_path, destination_path)
