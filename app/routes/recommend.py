from fastapi import APIRouter, Query
from fuzzywuzzy import process
from app.utils.cbf_loader import load_cbf_data
from app.schemas.recommend_schemas import PhoneOut
import random

# ✅ Load CBF model data
df_features, df_images, similarity_matrix = load_cbf_data()

router = APIRouter(prefix="/recommend", tags=["Recommendation"])

# ✅ Helper: Format phone recommendation message
def format_message(phone: dict, score: float = None) -> str:
    message = (
        f"\n Waxaan kuu haynaa xulashada ugu fiican!"
        f"\n Nooca: {phone.get('Brand', '')}"
        f"\n Model: {phone.get('Model', '')}"
        f"\n Xasuusta: {phone.get('Memory', '')}"
        f"\n Kaydinta: {phone.get('Storage', '')}"
        f"\n Qiimaha: ${phone.get('Selling Price', 0)}"
    )
    if score is not None:
        message += f"\n✅ Isku ekaanshaha: {round(score, 4)}"
    return message

# ✅ GET: All Phones (random, unique, valid images)
@router.get("/phones", response_model=list[PhoneOut])
def get_all_phones(limit: int = 25):
    phones = []
    try:
        df_features["model_lower"] = df_features["Model"].str.lower().str.strip()
        df_images["model_lower"] = df_images["Model"].str.lower().str.strip()

        merged = df_features.merge(
            df_images[["model_lower", "Image_URL"]],
            on="model_lower", how="left"
        )

        merged = merged[merged["Image_URL"].notnull()]
        merged = merged[~merged["Image_URL"].astype(str).str.lower().isin(
            ["", "nan", "none", "placeholder", "logo", "?"]
        )]
        merged = merged.drop_duplicates(subset="model_lower", keep="first")

        sample = merged.sample(n=min(limit, len(merged)), random_state=random.randint(1, 9999))

        for _, row in sample.iterrows():
            phones.append({
                "Brand": row.get("Brand", ""),
                "Model": row.get("Model", ""),
                "RAM": str(row.get("Memory", "")),
                "Storage": str(row.get("Storage", "")),
                "Rating": float(row.get("Rating", 0)),
                "Price": float(row.get("Selling Price", 0)),   # ✅ Sax column
                "Image_URL": row.get("Image_URL", ""),
                "similarity": None,
                "formatted_message": format_message(row)
            })

    except Exception as e:
        print("❌ Error in get_all_phones:", str(e))
    return phones

# ✅ GET: Recommendations by Model
@router.get("/card", response_model=list[PhoneOut])
def get_recommendations_card_api(model: str = Query(..., description="Phone model name"), top_n: int = 5):
    return get_recommendations(model, top_n)

# ✅ Recommendation Logic
def get_recommendations(model_name: str, top_n: int = 5):
    try:
        model_name = model_name.lower().strip()
        df_features["model_lower"] = df_features["Model"].str.lower().str.strip()
        df_images["model_lower"] = df_images["Model"].str.lower().str.strip()

        all_models = df_features["model_lower"].unique().tolist()
        matched_model, score = process.extractOne(model_name, all_models)

        if score < 70:
            return []

        index = df_features[df_features["model_lower"] == matched_model].index[0]
        scores = list(enumerate(similarity_matrix[index]))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)

        recommendations = []
        added_models = set()

        for i, score in scores:
            phone = df_features.iloc[i].copy()
            model_lower = phone.get("Model", "").lower().strip()

            if model_lower in added_models:
                continue

            image_row = df_images[df_images["model_lower"] == model_lower]
            image_url = image_row["Image_URL"].values[0] if not image_row.empty else ""
            if not isinstance(image_url, str) or image_url.strip().lower() in ["", "nan", "none", "placeholder", "logo", "?"]:
                continue

            recommendations.append({
                "Brand": phone.get("Brand", ""),
                "Model": phone.get("Model", ""),
                "RAM": str(phone.get("Memory", "")),
                "Storage": str(phone.get("Storage", "")),
                "Rating": float(phone.get("Rating", 0)),
                "Price": float(phone.get("Selling Price", 0)),   # ✅ Sax column
                "Image_URL": image_url,
                "similarity": round(score, 4),
                "formatted_message": format_message(phone, score)
            })

            added_models.add(model_lower)
            if len(recommendations) >= top_n:
                break

        return recommendations

    except Exception as e:
        print("❌ Error in get_recommendations:", str(e))
        return []

# ✅ GET: Single Phone Details by Model
@router.get("/one", response_model=PhoneOut)
def get_phone_details(model: str = Query(..., description="Phone model name")):
    try:
        model_lower = model.lower().strip()
        df_features["model_lower"] = df_features["Model"].str.lower().str.strip()
        df_images["model_lower"] = df_images["Model"].str.lower().str.strip()

        row = df_features[df_features["model_lower"] == model_lower].iloc[0]
        image_row = df_images[df_images["model_lower"] == model_lower]
        image_url = image_row["Image_URL"].values[0] if not image_row.empty else ""

        return {
            "Brand": row.get("Brand", ""),
            "Model": row.get("Model", ""),
            "RAM": str(row.get("Memory", "")),
            "Storage": str(row.get("Storage", "")),
            "Rating": float(row.get("Rating", 0)),
            "Price": float(row.get("Selling Price", 0)),   # ✅ Sax column
            "Image_URL": image_url,
            "similarity": None,
            "formatted_message": format_message(row)
        }

    except Exception as e:
        print("❌ Error in get_phone_details:", str(e))
        return {}
