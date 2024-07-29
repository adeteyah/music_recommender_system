import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from nltk.stem import WordNetLemmatizer

# Ensure you have the required NLTK data files
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# List of song titles
song_titles = [
    "Shape of You",
    "Blinding Lights",
    "Dance Monkey",
    "Rockstar",
    "Someone Like You",
    "Happier",
    "Senorita",
    "Bad Guy",
    "Sunflower",
    "Without Me"
]

# Initialize a lemmatizer
lemmatizer = WordNetLemmatizer()

# Define a function to clean and process the titles


def extract_keywords_from_title(title, max_keywords=5):
    stop_words = set(stopwords.words('english'))

    # Tokenize the title
    words = word_tokenize(title)
    # Remove stopwords and non-alphabetic characters, then lemmatize
    words = [lemmatizer.lemmatize(word.lower()) for word in words if word.isalpha(
    ) and word.lower() not in stop_words]

    # Frequency distribution (in this context, it is not very useful since the title words are unique)
    # but we'll use it to get the top words based on our max_keywords limit
    freq_dist = FreqDist(words)

    # Extract most common words
    common_words = freq_dist.most_common(max_keywords)

    # Return keywords separated by commas
    return ', '.join(word for word, _ in common_words)


# Extract predicted keywords for each song title
predicted_lyrics = {title: extract_keywords_from_title(
    title) for title in song_titles}

# Display the predicted lyrics for each title
for title, keywords in predicted_lyrics.items():
    print(f"{title}: {keywords}")
