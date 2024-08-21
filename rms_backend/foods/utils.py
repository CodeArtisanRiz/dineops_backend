# utils.py
import requests
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)

def upload_image(image_file, tenant_name):
    # Uploads an image file to the remote server and returns the URL.
    files = {'file': (image_file.name, image_file.read(), image_file.content_type)}
    data = {'tenant': tenant_name}
    response = requests.post('https://techno3gamma.in/bucket/dineops/handle_food_image.php', files=files, data=data)

    if response.status_code == 200:
        data = response.json()
        image_url = data.get('image_url')
        logger.debug(f'Uploaded image URL: {image_url}')
        return image_url
    return None

def handle_image_upload(request, tenant_name):
    # Helper method to handle image file upload
    image_file = request.FILES.get('image')
    if image_file:
        image_url = upload_image(image_file, tenant_name)
        if image_url:
            # Validate URL
            validate = URLValidator()
            try:
                validate(image_url)
                request.data._mutable = True  # Make request data mutable
                request.data['image'] = image_url
                request.data._mutable = False  # Make request data immutable
                logger.debug(f'Successfully added image URL to request data: {request.data["image"]}')
            except ValidationError as e:
                logger.error(f'Invalid image URL: {image_url}, Error: {e}')
                raise PermissionDenied('Failed to upload image: Invalid URL.')
        else:
            raise PermissionDenied('Failed to upload image.')
        