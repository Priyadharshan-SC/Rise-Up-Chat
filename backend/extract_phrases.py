import pandas as pd
import re
from collections import Counter
import os

def clean_text(text):
    text = str(text).lower()
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)
    # Remove mentions
    text = re.sub(r'@\w+', '', text)
    # Remove special characters, keep only letters and spaces
    text = re.sub(r'[^a-z\s]', ' ', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_ngrams(text, n):
    words = text.split()
    return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]

def main():
    # Load dataset
    csv_path = 'dataset/Safety/Suicide_Ideation_Dataset(Twitter-based).csv'
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return
        
    df = pd.read_csv(csv_path)
    
    # Filter for Potential Suicide post
    df_suicide = df[df['Suicide'].str.strip() == 'Potential Suicide post']
    
    # Clean text
    cleaned_tweets = df_suicide['Tweet'].apply(clean_text)
    
    bigrams = []
    trigrams = []
    
    for tweet in cleaned_tweets:
        bigrams.extend(get_ngrams(tweet, 2))
        trigrams.extend(get_ngrams(tweet, 3))
        
    bigram_counts = Counter(bigrams)
    trigram_counts = Counter(trigrams)
    
    # Simple stopword filter
    stop_words = {'i', 'am', 'is', 'to', 'the', 'a', 'and', 'my', 'me', 'in', 'of', 'for', 'it', 'on', 'that', 'this', 'you', 'be', 'with', 'so', 'just', 'have', 'not', 'do', 'but', 'can', 'are', 'was', 'as', 'at', 'all', 'like', 'how', 'when', 'will', 'no', 'what', 'about'}
    
    def is_valid_ngram(ngram):
        words = ngram.split()
        # Filter out if ALL words are stop words
        if all(w in stop_words for w in words):
            return False
        return True

    print("Top 30 Bigrams:")
    b_count = 0
    for b, count in bigram_counts.most_common(200):
        if is_valid_ngram(b):
            print(f"{b} ({count})")
            b_count += 1
            if b_count == 30:
                break
                
    print("\nTop 30 Trigrams:")
    t_count = 0
    for t, count in trigram_counts.most_common(200):
        if is_valid_ngram(t):
            print(f"{t} ({count})")
            t_count += 1
            if t_count == 30:
                break

if __name__ == "__main__":
    main()
