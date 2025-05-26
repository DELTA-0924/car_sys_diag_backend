from pathlib import Path
import joblib
import os

BASE_DIR = Path(__file__).resolve().parent.parent

model = joblib.load(os.path.join(BASE_DIR,"ml_models/model_tree.pkl"))
model2 = joblib.load(os.path.join(BASE_DIR,"ml_models/model_gradientboosting.pkl"))
