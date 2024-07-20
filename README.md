# rms_backend

1.Clone the repository:

git clone https://github.com/CodeArtisanRiz/rms_backend.git
cd rms_backend

2. Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. Install the required packages and change dir:

pip install -r requirements.txt
cd rms_backend

<!-- Create the project -->
<!-- django-admin startproject rms_backend -->
<!-- cd rms_backend -->
<!-- python manage.py startapp accounts  -->
<!-- Configure Project settings -->
<!-- setup Project urls -->

<!-- Create account - models, serializers, views, urls and management command -->
<!-- python manage.py makemigrations -->
<!-- python manage.py migrate -->




# EndPoints:
All Products
Method: GET
URL: http://127.0.0.1:8000/api/foods/fooditems/
Headers:
Key: Authorization
Value: Bearer <your_access_token>

View Products filtered by Category
Method: GET
URL: http://127.0.0.1:8000/api/foods/fooditems/?category=<category_name>
Headers:
Key: Authorization
Value: Bearer <your_access_token>

View Specific Product:
Method: GET
URL: http://127.0.0.1:8000/api/foods/fooditems/<id>/
Headers:
Key: Authorization
Value: Bearer <your_access_token>

Create a New Product:
Method: POST
URL: http://127.0.0.1:8000/api/foods/fooditems/
Headers:
Key: Authorization
Value: Bearer <your_access_token>
Key: Content-Type
Value: multipart/form-data
Body: form-data
Key: name
Value: <product_name>
Key: description
Value: <product_description>
Key: price
Value: <product_price>
Key: image
Value: <upload_image_file>
Key: category
Value: <product_category>

Update a Product:
Method: PUT or PATCH
URL: http://127.0.0.1:8000/api/foods/fooditems/<id>/
Headers:
Key: Authorization
Value: Bearer <your_access_token>
Key: Content-Type
Value: multipart/form-data
Body: form-data
Key: name
Value: <product_name>
Key: description
Value: <product_description>
Key: price
Value: <product_price>
Key: image
Value: <upload_image_file>
Key: category
Value: <product_category>

Delete a Product:
Method: DELETE
URL: http://127.0.0.1:8000/api/foods/fooditems/<id>/
Headers:
Key: Authorization
Value: Bearer <your_access_token>
[20/07/24, 15:02:41] H M Rizwan Mazumder: View All Products: