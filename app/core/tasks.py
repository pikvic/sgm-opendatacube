import rasterio
from PIL import Image
from pyproj import Transformer

import app.core.config as config


def clear_files_for_job(job_id):
    path = config.UPLOAD_DIR / job_id
    if path.exists():
        for f in path.iterdir():
            f.unlink()
        path.rmdir()
    path = config.DOWNLOAD_DIR / job_id
    if path.exists():
        for f in path.iterdir():
            f.unlink()
        path.rmdir()

def get_or_create_dir(root, job_id):
    path = root / job_id
    if not path.exists():
        path.mkdir()
    return path

def generate_filename(path, prefix, name):
    return path / f'{prefix}_{name}'

def error(message):
    return {'success': False, 'error': message}

def ready(results):
    return {'ready': True, 'results': results}
    

def transform_coords(points, crs1, crs2=4326):
    transformer = Transformer.from_crs(crs1, crs2, always_xy=True)
    result = [transformer.transform(x, y) for x, y in points]
    return result

def save_png(arr, filename='temp.png'):
    img = Image.fromarray(arr)
    img.save(filename)

def get_overview(url, factor=1):
    with rasterio.open(url) as src:
        overviews = src.overviews(1)
        factor = factor if factor <= len(overviews) else len(overviews)
        scale = overviews[-factor]
        arr = src.read(1, out_shape=(src.height // scale, src.width // scale))        
        metadata = {'profile': src.profile, 'bounds': src.bounds}
        bounds = metadata['bounds']
        points = [
            (bounds.left, bounds.bottom),
            (bounds.left, bounds.top),
            (bounds.right, bounds.top),
            (bounds.right, bounds.bottom)
        ]
        points = transform_coords(points, metadata['profile']['crs'])
        metadata['points'] = points
    return arr, metadata