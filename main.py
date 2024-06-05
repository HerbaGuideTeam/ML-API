import os
import uvicorn
import tensorflow as tf
import numpy as np
from io import BytesIO
from PIL import Image
from fastapi import FastAPI, Response, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse

# Load the model
model = tf.keras.models.load_model('./model.h5')
app = FastAPI(title="ML Try FastAPI")

# Define CIFAR-10 class names
class_names = [
    'airplane', 'automobile', 'bird', 'cat', 'deer',
    'dog', 'frog', 'horse', 'ship', 'truck'
]

# In-memory storage for prediction history
prediction_history = []

# Image processing function
def process_image(image_bytes):
    image = Image.open(BytesIO(image_bytes))
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image = image.resize((32, 32))  # Resize the image as per the model requirements
    image = np.array(image) / 255.0  # Normalize pixel values
    return image

# Health check endpoint
@app.get("/")
def index():
    return Response(content="API WORKING", status_code=200)

# Endpoint for image prediction
@app.post("/predict_image")
async def predict_image(photo: UploadFile = File(...)):
    try:
        if photo.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is Not an Image")
        
        contents = await photo.read()
        processed_image = process_image(contents)
        processed_image = np.expand_dims(processed_image, axis=0)

        prediction = model.predict(processed_image)
        predicted_class = np.argmax(prediction)
        predicted_class_name = class_names[predicted_class]
        
        response = {
            'prediction': {
                'class': predicted_class_name,
                'confidence': float(np.max(prediction))
            }
        }

        # Save prediction to history
        prediction_history.append(response)

        return JSONResponse(content=response, status_code=200)
    
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Endpoint to get prediction history
@app.get("/gethistory")
def get_history():
    return JSONResponse(content={"history": prediction_history}, status_code=200)

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8080)
