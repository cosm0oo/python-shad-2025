from pathlib import Path
from importlib.resources import files, as_file


from PIL import Image
import numpy as np
import numpy.typing as npt


def read_file(filename: str | Path) -> npt.NDArray[np.ubyte]:
    with Image.open(filename) as img:
        data = np.array(img, dtype=np.ubyte)
    return data


def write_file(data: npt.NDArray[np.ubyte], filename: str | Path) -> None:
    new_img = Image.fromarray(data)
    new_img.save(filename)


def get_base_file() -> npt.NDArray[np.ubyte]:
    package_files = files('steganography_tool')
    lenna_resource = package_files / 'lenna.png'
    with as_file(lenna_resource) as lenna_path:
        return read_file(lenna_path)
