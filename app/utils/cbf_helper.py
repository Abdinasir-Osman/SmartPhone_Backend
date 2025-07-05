import pandas as pd
import os

def get_phone_id_by_model(model_name: str) -> str:
    # ❗ Absolute path oo sax ah
    dataset_path = r"C:\Users\SCRPC\Desktop\ML\CBF\CBF_Final_Feature_Dataset.csv"

    if not os.path.exists(dataset_path):
        raise FileNotFoundError("CBF dataset file not found at: " + dataset_path)

    df = pd.read_csv(dataset_path)

    match = df[df["Model"].str.strip().str.lower() == model_name.strip().lower()]
    if not match.empty:
        return match.iloc[0]["Phone_ID"]
    return None
