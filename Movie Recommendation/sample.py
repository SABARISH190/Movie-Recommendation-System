from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import pymongo
from bson.binary import Binary
from typing import List

# Initialize FastAPI app
app = FastAPI()

# Mount static directory for CSS, JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Jinja2 templates for HTML pages
templates = Jinja2Templates(directory="templates")

# MongoDB connection
mongo_uri = "mongodb+srv://saisabarishwins:Sabarish18@cineheist.6om63.mongodb.net/"
db_name = "CineHeist"
collection_name = "Movies_with_vectors"

# SentenceTransformer model for encoding prompts
encoder = SentenceTransformer("paraphrase-mpnet-base-v2")

# FAISS index for movie vectors
faiss_index = None

# Function to load vectors from MongoDB and build FAISS index
def load_vectors_from_mongodb():
    global faiss_index
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]

        cursor = collection.find({})
        vectors = []
        for doc in cursor:
            vector_data = doc.get("vectors")

            # Convert from Binary to numpy array if necessary
            if isinstance(vector_data, Binary):
                vector_data = np.frombuffer(vector_data, dtype=np.float32)

            vectors.append(vector_data)

        # Convert list of vectors into a NumPy array
        vectors_array = np.array(vectors)

        # Build FAISS index
        vector_dimension = vectors_array.shape[1]
        faiss_index = faiss.IndexFlatL2(vector_dimension)
        faiss_index.add(vectors_array.astype(np.float32))  # Add vectors to FAISS index
        
        client.close()

    except Exception as e:
        print(f"Error loading vectors from MongoDB: {e}")

# Load vectors once at the start
load_vectors_from_mongodb()

# Function to encode the user's prompt and perform similarity search
def get_similar_movies(prompt: str, top_k=5):
    try:
        # Encode the user's prompt into a vector
        prompt_vector = encoder.encode([prompt])[0]

        # Perform the similarity search in FAISS
        distances, indices = faiss_index.search(np.array([prompt_vector]).astype(np.float32), top_k)

        # Retrieve the movie details from MongoDB based on indices
        client = pymongo.MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        similar_movies = []

        for idx in indices[0]:
            movie = collection.find_one({"_id": idx})
            if movie:
                similar_movies.append(movie)

        client.close()
        return similar_movies

    except Exception as e:
        print(f"Error performing similarity search: {e}")
        return []

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_prompt_page(request: Request):
    return templates.TemplateResponse("prompt page.html", {"request": request})

@app.get("/result/", response_class=HTMLResponse)
async def show_results(request: Request, prompt: str):
    # Check if prompt is empty
    if not prompt:
        return HTMLResponse(content="<p>Prompt is required!</p>", status_code=422)

    similar_movies = get_similar_movies(prompt)
    return templates.TemplateResponse("result.html", {"request": request, "movies": similar_movies, "prompt": prompt})


@app.get("/feedback/", response_class=HTMLResponse)
async def show_feedback_page(request: Request):
    return templates.TemplateResponse("feedback.html", {"request": request})
