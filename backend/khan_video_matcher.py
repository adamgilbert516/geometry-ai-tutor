import pandas as pd
from rapidfuzz import fuzz
from geogebra_topics import topics

# Load Khan Academy video CSV
df = pd.read_csv("khan_videos.csv")

# Normalize topics
normalized_topics = [t.lower().strip() for t in topics]

def find_all_matches(title, threshold=60):
    title = title.lower()
    matches = [
        topic for topic in normalized_topics
        if fuzz.token_set_ratio(topic, title) >= threshold
    ]
    return ", ".join(sorted(set(matches)))

# Apply multi-match logic to ALL videos (don't filter)
df["matched_topics"] = df["video_title"].apply(find_all_matches)

# Add youtube_id if not present (for backward compatibility)
if 'youtube_id' not in df.columns:
    df['youtube_id'] = None

# Save ALL videos with their matches (empty string means no matches)
df.to_csv("khan_video_matches.csv", index=False)
print(f"✅ Saved {len(df)} videos (matched and unmatched) to khan_video_matches.csv")