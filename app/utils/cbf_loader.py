import pandas as pd
import numpy as np
import os

def load_cbf_data():
    base_path = r"C:\Users\SCRPC\Desktop\ML\CBF"  # ✅ raw string
    df_features = pd.read_csv(os.path.join(base_path, "CBF_Final_Feature_Dataset.csv"))
    df_images = pd.read_csv(os.path.join(base_path, "CBF_Images_Cleaned.csv"))
    similarity_matrix = np.load(os.path.join(base_path, "CBF_Similarity_Matrix.npy"))
    return df_features, df_images, similarity_matrix
