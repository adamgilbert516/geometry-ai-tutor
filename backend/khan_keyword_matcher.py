import pandas as pd
from difflib import get_close_matches

# Load CSV
df = pd.read_csv("khan_video_matches.csv")

# Load GeoGebra topics
from geogebra_topics import topics as geogebra_topics

geo_topics = [t.lower() for t in geogebra_topics]

def map_keywords(row):
    if pd.isna(row['matched_topics']):
        return ""

    raw_keywords = [k.strip().lower() for k in row['matched_topics'].split(',')]
    improved_keywords = set()

    for keyword in raw_keywords:
        match = get_close_matches(keyword, geo_topics, n=1, cutoff=0.6)
        if match:
            improved_keywords.add(match[0])
        else:
            if len(keyword) > 3:
                improved_keywords.add(keyword)

    # Plain, clean comma-separated string
    return ', '.join(sorted(improved_keywords))

# Apply cleaning
df['keywords'] = df.apply(map_keywords, axis=1)

# Select only necessary columns
clean_df = df[['subject', 'video_title', 'video_url', 'video_id', 'keywords']]

# Save directly—no need for escapechar or manual cleanup
clean_df.to_csv("khan_video_matches_cleaned.csv", index=False)

print("✅ CSV saved cleanly without extra commas or backslashes.")
