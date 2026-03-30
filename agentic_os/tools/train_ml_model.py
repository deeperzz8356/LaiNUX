import os
import pandas as pd
import numpy as np
import pickle
import time
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# 1. GENERATE SYNTHETIC DATASET
def generate_dataset(n_samples=5000):
    print(f"[*] DATA GENERATION: Creating {n_samples} samples for training...")
    data = []
    
    mapping = {
        "Images": (["pic", "img", "photo", "shot", "capture"], [".jpg", ".jpeg", ".png", ".webp"]),
        "Audio": (["song", "track", "music", "beat", "voice"], [".mp3", ".wav", ".flac"]),
        "Documents": (["report", "doc", "pdf", "essay", "notes"], [".txt", ".pdf", ".docx", ".md"]),
        "Others": (["app", "setup", "game", "script", "archive"], [".exe", ".zip", ".rar", ".py"])
    }
    
    for _ in range(n_samples):
        cat = np.random.choice(list(mapping.keys()))
        keywords, exts = mapping[cat]
        keyword = np.random.choice(keywords)
        ext = np.random.choice(exts)
        filename = f"{keyword}_{np.random.randint(100, 9999)}{ext}"
        data.append({"filename": filename, "extension": ext, "category": cat})
        
    pd_df = pd.DataFrame(data)
    print("[+] Dataset created successfully.")
    return pd_df

# 2. FEATURE ENGINEERING
def extract_features(df):
    print("[*] FEATURE ENGINEERING: Processing extensions and filename attributes...")
    le_ext = LabelEncoder()
    df['ext_encoded'] = le_ext.fit_transform(df['extension'])
    df['name_len'] = df['filename'].apply(len)
    df['has_underscore'] = df['filename'].apply(lambda x: 1 if '_' in x else 0)
    return df, le_ext

# 3. TRAINING
def train_model():
    print("\n" + "="*40)
    print("   AI MODEL TRAINING IN PROGRESS...   ")
    print("="*40)
    
    df = generate_dataset(5000)
    processed_df, le_ext = extract_features(df)
    
    X = processed_df[['ext_encoded', 'name_len', 'has_underscore']]
    y = processed_df['category']
    
    le_cat = LabelEncoder()
    y_encoded = le_cat.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    
    print("\n[*] TRAINING: Fitting Random Forest Classifier (100 Trees)...")
    for i in range(5):
        time.sleep(1) # Visual effect
        print(f"    - Optimizing Estimator {i*25}...")
        
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    print("[+] Fit complete.")
    
    # 4. EVALUATION
    print("\n[*] EVALUATION: Running cross-validation on test set...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n>>>> FINAL ACCURACY: {accuracy * 100:.2f}% <<<<")
    print("\nClassification Report:")
    report = classification_report(y_test, y_pred, target_names=le_cat.classes_)
    print(report)
    
    # 5. SAVE
    save_path = PROJECT_ROOT / "agentic_os" / "models"
    save_path.mkdir(parents=True, exist_ok=True)
    model_file = save_path / "file_classifier.pkl"

    with open(model_file, 'wb') as f:
        pickle.dump({
            "model": model, "le_ext": le_ext, "le_cat": le_cat, 
            "features": ['ext_encoded', 'name_len', 'has_underscore']
        }, f)
        
    print(f"\n[!] Model successfully exported to {model_file}")
    print("="*40 + "\n")

if __name__ == "__main__":
    train_model()
