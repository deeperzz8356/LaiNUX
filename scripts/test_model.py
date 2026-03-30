import os
from sentence_transformers import SentenceTransformer, util

def classify_extension(ext):
    categories = ["Image (photo, picture, drawing)", 
                 "Audio (music, sound, voice)", 
                 "Document (text, report, spreadsheet, presentation)",
                 "Other (data, code, hidden)"]
    
    # We load a small, fast model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    ext_emb = model.encode(ext)
    cat_embs = model.encode(categories)
    
    # Compute similarities
    cos_scores = util.cos_sim(ext_emb, cat_embs)[0]
    
    # Find the best match
    best_idx = cos_scores.argmax()
    return categories[best_idx].split(' ')[0]

if __name__ == "__main__":
    test_exts = [".jpeg", ".wav", ".pdf", ".exe"]
    for e in test_exts:
        print(f"{e} -> {classify_extension(e)}")
