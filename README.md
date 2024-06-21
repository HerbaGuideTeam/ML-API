# ML-API README

This repository provides a FastAPI-based API (`main.py`) for a machine learning application that predicts herbal plant types from images. It integrates with Firebase for user authentication and Google Cloud services for storage and database operations.

## Table of Contents

- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Installation Instructions](#installation-instructions)
- [Endpoints](#endpoints)
- [Developers](#developers)

## Project Structure

```
ML-API-main/
├── .dockerignore
├── .gitattributes
├── .gitignore
├── Dockerfile
├── README.md
├── bestTFLHerbalGuide.h5
├── connect.py
├── main.py
├── requirements.txt
└── .vscode/
    └── setting.json
```


## Dependencies

### Python Libraries

- `uvicorn`: ASGI server for running FastAPI.
- `tensorflow`: Machine learning framework for loading and using the pre-trained model (`bestTFLHerbalGuide.h5`).
- `firebase_admin`: Firebase SDK for user authentication.
- `PIL`, `numpy`: Image processing and array operations.
- `fastapi`: Web framework for building APIs.
- `google-cloud-firestore`, `google-cloud-secret-manager`, `google-cloud-storage`: Google Cloud SDKs for Firestore, Secret Manager, and Cloud Storage.
- `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`: Google authentication libraries.
- `sqlalchemy`, `pymysql`: SQL database connection and operations.

## installation Instructions

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/ML-API.git
    cd ML-API
    ```

2. **Install the required packages**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Run the API**:
    ```sh
    python main.py
    ```

### Using Docker

1. **Build the Docker image**:
    ```sh
    docker build -t ml-api .
    ```

2. **Run the Docker container**:
    ```sh
    docker run -p 5000:5000 ml-api
    ```
## Endpoints

### Predict Image
- **URL:** `/predict_image`
- **Method:** `POST`
- **Headers:**
    - `Authorization`: `Bearer <token>` : use a token from login
- **Request Body (Form-data):**
      `photo`: Image file (JPEG or PNG)

#### Responses
- **Success Response (200 OK):**
```json
{
  "message": "Prediction saved successfully.",
  "prediction": {
    "tanaman_herbal": {
      "nama": "Sereh Dapur",
      "deskripsi": "Description of Sereh Dapur",
      "mengobati_apa": [
        {
          "penyakit": "Cold",
          "resep": ["Recipe 1"]
        }
      ],
      "photo_url": "url"
    },
    "confidence": 0.95,
    "created_at": "2024-06-21T12:34:56.789Z"
  }
```
- **Error Response (401 Unauthorized):**
```json
{
  "detail": "Authorization token missing"
}
```
- **Error Response (400 Bad Request):**
```json
{
  "detail": "File is Not an Image"
}
```
- **Error Response (500 Internal Server Error):**
```json
{
  "detail": "Internal Server Error"
}
```

### Predict Image Anonymously
- **URL:** `/predict_image_anon`
- **Method:** `POST`
- **Request Body (Form-data):**
      `photo`: Image file (JPEG or PNG)

#### Responses
- **Success Response (200 OK):**
```json
{
  "message": "Prediction successful.",
  "prediction": {
    "tanaman_herbal": {
      "nama": "Sereh Dapur",
      "deskripsi": "Description of Sereh Dapur",
      "mengobati_apa": [
        {
          "penyakit": "Cold",
          "resep": ["Recipe 1"]
        }
      ],
      "photo_url": "url"
    },
    "confidence": 0.95,
  }
```
- **Error Response (400 Bad Request):**
```json
{
  "detail": "File is Not an Image"
}
```
- **Error Response (500 Internal Server Error):**
```json
{
  "detail": "Internal Server Error"
}
```

### Get Prediction History
- **URL:** `/gethistory`
- **Method:** `GET`
- **Headers:**
    - `Authorization`: `Bearer <token>` : use a token from login

#### Responses
- **Success Response (200 OK):**
```json
{
  "message": "History retrieved successfully.",
  "history": [
    {
      "tanaman_herbal": {
        "nama": "Sereh Dapur",
        "deskripsi": "Description of Sereh Dapur",
        "mengobati_apa": [
          {
            "penyakit": "Cold",
            "resep": ["Recipe 1"]
          }
        ],
        "photo_url": "url"
      },
      "confidence": 0.95,
      "created_at": "2024-06-21T12:34:56.789Z"
    }
  ]
}
```
- **Error Response (401 Unauthorized):**
```json
{
  "detail": "Authorization token missing"
}
```
- **Error Response (500 Internal Server Error):**
```json
{
  "detail": "Internal Server Error"
}
```

### Search Prediction History
- **URL:** `/search_history?plant_name=<PLANT NAME>`
- **Method:** `GET`
- **Headers:**
    - `Authorization`: `Bearer <token>` : use a token from login

#### Responses
- **Success Response (200 OK):**
```json
{
  "message": "Filtered history retrieved successfully.",
  "history": [
    {
      "tanaman_herbal": {
        "nama": "Sereh Dapur",
        "deskripsi": "Description of Sereh Dapur",
        "mengobati_apa": [
          {
            "penyakit": "Cold",
            "resep": ["Recipe 1"]
          }
        ],
        "photo_url": "url"
      },
      "confidence": 0.95,
      "created_at": "2024-06-21T12:34:56.789Z"
    }
  ]
}
```
- **Error Response (401 Unauthorized):**
```json
{
  "detail": "Authorization token missing"
}
```
- **Error Response (500 Internal Server Error):**
```json
{
  "detail": "Internal Server Error"
}
```
