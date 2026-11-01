from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def find_similar(text, category, location, candidates, threshold=0.48, limit=5):
    eligible = [c for c in candidates if c.description.strip() and (c.confirmed_category or c.predicted_category) == category]
    if not text.strip() or not eligible: return []
    docs = [text + ' ' + location] + [c.description + ' ' + c.location for c in eligible]
    try:
        vectors = TfidfVectorizer(stop_words='english', ngram_range=(1,2)).fit_transform(docs)
    except ValueError: return []
    scores = cosine_similarity(vectors[0], vectors[1:]).ravel()
    return sorted([(c, round(float(score)*100,1)) for c,score in zip(eligible,scores) if score >= threshold], key=lambda x:-x[1])[:limit]
