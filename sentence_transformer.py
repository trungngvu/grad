from sentence_transformers import SentenceTransformer
modelPath = "/bert"

model = SentenceTransformer('all-MiniLM-L12-v2')
model.save(modelPath)
model = SentenceTransformer(modelPath)