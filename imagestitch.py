from operator import truediv
from PIL import Image
from glob import glob


def merge_images(files: list, ver: bool = False):
    """Stitch together multiple images
    :param files: list of image filepaths
    :param ver: if true stitches vertically, else stitch horizantally
    :return: the merged Image object
    """
    images = []
    dimensions = []
    cumdim = [0]
    for file in files:
        images.append(Image.open(file))
        dimensions.append(images[-1].size)

    result_width = 0
    result_height = 0
    for dim in dimensions:
        if ver:
            result_width = dim[0] if dim[0] > result_width else result_width
            result_height += dim[1]
            cumdim.append(cumdim[-1] + dim[1])
        else:
            result_width += dim[0]
            result_height = dim[1] if dim[1] > result_height else result_height
            cumdim.append(cumdim[-1] + dim[0])

    result = Image.new("RGB", (result_width, result_height))
    for i in range(len(images)):
        if ver:
            result.paste(im=images[i], box=(0, cumdim[i]))
        else:
            result.paste(im=images[i], box=(cumdim[i], 0))
    return result


merge_images(glob("*.jpg"), True).save("merged.jpg", "JPEG")
