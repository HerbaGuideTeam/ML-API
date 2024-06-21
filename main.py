import os
import uvicorn
import tensorflow as tf
import numpy as np
import firebase_admin
import json
from io import BytesIO
from PIL import Image
from fastapi import FastAPI, Response, UploadFile, File, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from google.cloud import firestore, secretmanager, storage
from google.cloud.storage import Blob
from connect import create_connection_pool
from sqlalchemy import text
from google.oauth2 import service_account
from firebase_admin import auth, credentials
from datetime import datetime 

def access_secret_version(project_id, secret_id, version_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")
    return json.loads(payload)

model = tf.keras.models.load_model('./bestTFLHerbalGuide.h5')

app = FastAPI(title="ML Try FastAPI")

pool = create_connection_pool()


class_names = ['Badabotan', 'Bakung', 'Belimbing Wuluh', 'Bunga Tasbih', 'Kumis Kucing', 'Lidah Buaya', 'Mimba',
               'Sambiloto', 'Sereh Dapur', 'Sirih']

if not firebase_admin._apps:
    firebaseSa = access_secret_version('c241-ps193', 'firebase_sa','1')
    cred = credentials.Certificate(firebaseSa)
    firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.Client()

# Initialize Google Cloud Storage client
storage_client = storage.Client()
bucket_name = 'c241-ps193-bucket'
bucket = storage_client.bucket(bucket_name)

def save_image_to_bucket(image_bytes, filename):
    blob = bucket.blob(f"uploaded_images/{filename}")
    blob.upload_from_string(image_bytes, content_type="image/jpeg")
    return blob.public_url

def process_image(image_bytes):
    image = Image.open(BytesIO(image_bytes))
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image = image.resize((256, 256))
    image = np.array(image) / 255.0 
    return image

@app.get("/")
def index():
    return Response(content="API WORKING", status_code=200)

# Function to fetch product details
def fetch_product_details(nama):
    with pool.connect() as conn:
        sql_statement = text(
            "SELECT th.nama, th.deskripsi, pr.penyakit, pr.resep "
            "FROM tanaman_herbal th "
            "JOIN penyakit_resep pr ON th.id = pr.tanaman_herbal_id "
            "WHERE th.nama = :nama;"
        )
        sql_statement = sql_statement.bindparams(nama=nama)
        result = conn.execute(sql_statement)
        query_results = result.fetchall()

    if not query_results:
        return []

    formatted_results = {
        'nama': query_results[0][0],
        'deskripsi': query_results[0][1],
        'mengobati_apa': []
    }

    for row in query_results:
        formatted_results['mengobati_apa'].append({
            'penyakit': row[2],
            'resep': [row[3]] 
        })

    penyakit_dict = {}
    for item in formatted_results['mengobati_apa']:
        if item['penyakit'] not in penyakit_dict:
            penyakit_dict[item['penyakit']] = {'penyakit': item['penyakit'], 'resep': []}
        penyakit_dict[item['penyakit']]['resep'].extend(item['resep'])

    formatted_results['mengobati_apa'] = list(penyakit_dict.values())

    return formatted_results


# Endpoint for image prediction
@app.post("/predict_image")
async def predict_image(request: Request, photo: UploadFile = File(...)):
    try:
        jwt = request.headers.get('Authorization')
        if not jwt:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization token missing")

        user = auth.verify_id_token(jwt)
        user_id = user['user_id']

        if photo.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is Not an Image")

        contents = await photo.read()
        processed_image = process_image(contents)
        processed_image = np.expand_dims(processed_image, axis=0)

        prediction = model.predict(processed_image)

        predicted_class = np.argmax(prediction)
        predicted_class_name = class_names[predicted_class]
        product_details = fetch_product_details(predicted_class_name)

        if not product_details:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product details not found")

        photo_url = save_image_to_bucket(contents, f"{user_id}_{datetime.utcnow().timestamp()}.jpeg")

        product_details['photo_url'] = photo_url

        new_prediction = {
            'tanaman_herbal': product_details,
            'confidence': float(np.max(prediction)),
            'created_at': datetime.utcnow().isoformat(),
        }

        user_doc_ref = db.collection('user_prediction_history').document(user_id)
        user_doc = user_doc_ref.get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            if 'predictions' in user_data:
                user_data['predictions'].append(new_prediction)
            else:
                user_data['predictions'] = [new_prediction]
        else:
            user_data = {'predictions': [new_prediction]}

        user_doc_ref.set(user_data)

        response = {
            'message': 'Prediction saved successfully.',
            'prediction': new_prediction
        }

        return JSONResponse(content=response, status_code=200)

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/predict_image_anon")
async def predict_image_anon(photo: UploadFile = File(...)):
    try:
        if photo.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is Not an Image")

        contents = await photo.read()
        processed_image = process_image(contents)
        processed_image = np.expand_dims(processed_image, axis=0)

        prediction = model.predict(processed_image)

        predicted_class = np.argmax(prediction)
        predicted_class_name = class_names[predicted_class]
        product_details = fetch_product_details(predicted_class_name)

        if not product_details:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product details not found")

        photo_url = save_image_to_bucket(contents, f"anonymous_{datetime.utcnow().timestamp()}.jpeg")

        product_details['photo_url'] = photo_url

        new_prediction = {
            'tanaman_herbal': product_details,
            'confidence': float(np.max(prediction)),
        }

        response = {
            'message': 'Prediction successful.',
            'prediction': new_prediction
        }

        return JSONResponse(content=response, status_code=200)

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")



# Endpoint to get prediction history for the authenticated user
@app.get("/gethistory")
async def get_history(request: Request):
    try:
        jwt = request.headers.get('Authorization')
        if not jwt:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization token missing")

        user = auth.verify_id_token(jwt)
        user_id = user['user_id']

        user_doc_ref = db.collection('user_prediction_history').document(user_id)
        doc = user_doc_ref.get()
        if doc.exists:
            history = doc.to_dict().get('predictions', [])
            sorted_history = sorted(history, key=lambda x: x['created_at'], reverse=True)
            response = {
                'message': 'History retrieved successfully.',
                'history': sorted_history
            }
            return JSONResponse(content=response, status_code=200)
        else:
            response = {
                'message': 'No history found.',
                'history': []
            }
            return JSONResponse(content=response, status_code=200)
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
# Endpoint to search prediction history by plant name
@app.get("/search_history")
async def search_history(request: Request, plant_name: str):
    try:
        jwt = request.headers.get('Authorization')
        if not jwt:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization token missing")

        user = auth.verify_id_token(jwt)
        user_id = user['user_id']

        user_doc_ref = db.collection('user_prediction_history').document(user_id)
        doc = user_doc_ref.get()
        if doc.exists:
            history = doc.to_dict().get('predictions', [])
            filtered_history = [prediction for prediction in history if plant_name.lower() in prediction['tanaman_herbal']['nama'].lower()]
            sorted_filtered_history = sorted(filtered_history, key=lambda x: x['created_at'], reverse=True)
            response = {
                'message': 'Filtered history retrieved successfully.',
                'history': sorted_filtered_history
            }
            return JSONResponse(content=response, status_code=200)
        else:
            response = {
                'message': 'No history found.',
                'history': []
            }
            return JSONResponse(content=response, status_code=200)
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
