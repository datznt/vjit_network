from django.conf import settings
from django.contrib.sites.models import Site

from PIL import Image
from PIL.ExifTags import TAGS
from cv2 import cv2
from urllib.parse import urljoin
import mimetypes as mt
import os

def create_thumbnail(source, storage, dimensions) -> (bool, Image):
    _result, _thumbnails, file_type = False, None, None
    def _keep_orientation(image):
        exif = image.getexif()
        orientation_to_rotation_map = {
            3 : Image.ROTATE_180,
            6 : Image.ROTATE_270,
            8 : Image.ROTATE_90,
        }
        if exif != None:
            for tag,value in exif.items():
                decoded = TAGS.get(tag,tag)
                if decoded == "Orientation":
                    rotation = orientation_to_rotation_map.get(value)
                    if rotation:
                        image = image.transpose(rotation)
                    break
        return image
    try:    
        if not storage.exists(source.path):
            return (_result, _thumbnails, file_type)
        file = source.file
        mimetype = mt.guess_type(file.name)
        if not mimetype[0]:
            return (_result, _thumbnails, file_type)
        file_type = mimetype[0].split('/')[0]
        if file_type not in ['video', 'image']:
            return (_result, _thumbnails, file_type)
        if file_type == 'image':
            # processing heic
            _origin = Image.open(file.name, mode='r')
            _thumbnails = []
            for dimention in dimensions:
                _origin_copy = _keep_orientation(_origin.copy())
                _origin_copy.thumbnail(dimention, Image.ANTIALIAS)
                _thumbnails.append(_origin_copy)
            _result = True
        elif file_type == 'video':
            # processing hevc
            video_capture = cv2.VideoCapture(file.name)
            _, cv2_im = video_capture.read()
            cv2_im = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
            if _:
                _origin = Image.fromarray(cv2_im)
                _thumbnails = []
                for dimention in dimensions:
                    _origin_copy = _origin.copy()
                    _origin_copy.thumbnail(dimention,Image.ANTIALIAS)
                    _thumbnails.append(_origin_copy)
                _result = True
        
        return (_result, _thumbnails, file_type)
    except Exception as e:
        print(str(e))
        return _result, _thumbnails, file_type

def save_thumbnail(image: Image, path) -> bool:
    path = os.path.join(settings.MEDIA_ROOT, path)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        image.save(path)
        return True
    except Exception as e:
        print(str(e))
        return False

def save_thumbnails(thumbnails, file_modal, file_type):
    thumbnails_folder = {
        'path' : file_modal.thumbnail_directory_path(''),
        'thumbs' : [] 
    }
    for thumbnail in thumbnails:
        file_extention = 'png'
        file_name = str(thumbnail.size[0])+'x'+str(thumbnail.size[1])+'.' + file_extention
        path_thumbnail = os.path.join(thumbnails_folder['path'],file_name)
        save_ok = save_thumbnail(thumbnail,path_thumbnail)
        if save_ok:
            thumbnails_folder['thumbs'].append(file_name)
    return thumbnails_folder

def get_absolute_media_path(media_path, domain):
    assert media_path and domain, "To convert media to url you need media_path"
    settings.MEDIA_ROOT, "You need set MEDIA_ROOT in your project"
    settings.MEDIA_URL, "You need set MEDIA_ROOT in your project"
    # settings.MEDIA_ROOT, "You need set MEDIA_ROOT in your project"
    absolute_path = os.path.join(settings.BASE_DIR,settings.MEDIA_ROOT,media_path)
    if not os.path.exists(absolute_path):
        raise "The file does not exist"

    return urljoin(domain,settings.MEDIA_URL,media_path)