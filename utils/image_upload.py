# utils.py
import requests
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)

def upload_image(image_files, tenant_name, img_type):
    # Uploads multiple image files to the remote server and returns the URLs.
    files = [('file[]', (image_file.name, image_file.read(), image_file.content_type)) for image_file in image_files]
    data = {'tenant': tenant_name, 'imgType': img_type}
    response = requests.post('https://techno3gamma.in/bucket/dineops/handle_image.php', files=files, data=data)

    if response.status_code == 200:
        data = response.json()
        image_urls = data.get('images')
        if image_urls:
            logger.debug(f'Uploaded image URLs: {image_urls}')
            return image_urls
    return None

def handle_image_upload(request, tenant_name, img_type, field_name):
    # Helper method to handle image file upload
    image_files = request.FILES.getlist(field_name) or request.FILES.getlist(field_name + '[]')
    if image_files:
        image_urls = upload_image(image_files, tenant_name, img_type)
        if image_urls:
            # Validate each URL
            validate = URLValidator()
            try:
                for image_url in image_urls:
                    validate(image_url)
                request.data._mutable = True  # Make request data mutable
                request.data['images'] = image_urls
                request.data._mutable = False  # Make request data immutable
                logger.debug(f'Successfully added image URLs to request data: {request.data["images"]}')
                return image_urls
            except ValidationError as e:
                logger.error(f'Invalid image URL: {image_url}, Error: {e}')
                raise PermissionDenied('Failed to upload image: Invalid URL.')
        else:
            raise PermissionDenied('Failed to upload image.')
    return None
