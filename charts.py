import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

# Set styles
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

# Load CSV
df = pd.read_csv("Books_rating.csv")  # Update the path if needed

# Clean & Prepare
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
df['Votes'] = pd.to_numeric(df['Votes'], errors='coerce')
df['ReviewTime'] = pd.to_datetime(df['ReviewTime'], errors='coerce')
df.dropna(subset=['Rating'], inplace=True)

# ---- Plot 1: Ratings Distribution ----
sns.countplot(data=df, x='Rating', palette='viridis')
plt.title("Ratings Distribution")
plt.xlabel("Rating")
plt.ylabel("Number of Reviews")
plt.tight_layout()
plt.show()

# ---- Plot 2: Review Volume Over Time ----
df['YearMonth'] = df['ReviewTime'].dt.to_period('M')
reviews_over_time = df.groupby('YearMonth').size()
reviews_over_time.index = reviews_over_time.index.to_timestamp()
reviews_over_time.plot()
plt.title("Reviews Over Time")
plt.xlabel("Time")
plt.ylabel("Number of Reviews")
plt.tight_layout()
plt.show()

# ---- Plot 3: Word Cloud from Reviews ----
text = " ".join(str(review) for review in df['Review'].dropna())
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.title("Common Words in Reviews")
plt.show()

# ---- Plot 4: Top 10 Reviewed Books ----
top_books = df['Name'].value_counts().nlargest(10)
sns.barplot(x=top_books.values, y=top_books.index, palette='magma')
plt.title("Top 10 Reviewed Books")
plt.xlabel("Number of Reviews")
plt.ylabel("Book Name")
plt.tight_layout()
plt.show()

# ---- Plot 5: Average Rating of Top Books ----
avg_ratings = df[df['Name'].isin(top_books.index)].groupby('Name')['Rating'].mean()
avg_ratings = avg_ratings.loc[top_books.index]  # Keep same order
sns.barplot(x=avg_ratings.values, y=avg_ratings.index, palette='coolwarm')
plt.title("Avg Rating of Top Reviewed Books")
plt.xlabel("Average Rating")
plt.ylabel("Book Name")
plt.tight_layout()
plt.show()

# ---- Plot 6: Votes vs Rating ----
sns.scatterplot(data=df, x='Rating', y='Votes', alpha=0.3)
plt.title("Votes vs Rating")
plt.xlabel("Rating")
plt.ylabel("Votes")
plt.tight_layout()
plt.show()
