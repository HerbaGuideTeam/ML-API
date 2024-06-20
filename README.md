# ML-API README

This repository provides a FastAPI-based API (`main.py`) for a machine learning application that predicts herbal plant types from images. It integrates with Firebase for user authentication and Google Cloud services for storage and database operations.

## Table of Contents

- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Setup Instructions](#setup-instructions)
  - [Environment Setup](#environment-setup)
  - [Google Cloud Setup](#google-cloud-setup)
  - [Database Setup](#database-setup)
  - [Running the API](#running-the-api)
- [Endpoints](#endpoints)
- [Additional Notes](#additional-notes)
- [Authors](#authors)
- [License](#license)

## Project Structure

- **main.py**: Contains the FastAPI application with endpoints for image prediction, user authentication, and database operations.
- **connect.py**: Establishes a connection pool to a MySQL database hosted on Google Cloud SQL using SQLAlchemy and Google Secret Manager.

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

## Setup Instructions

### Environment Setup

Ensure Python 3.7+ is installed.

```bash
pip install -r requirements.txt
