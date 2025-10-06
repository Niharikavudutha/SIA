import requests
from datetime import datetime
 
api_key = "0df5b37ce8dc49ea88dd9259054d4487"
 
def get_news(topic):
    url = f"https://newsapi.org/v2/everything?q={topic}&language=en&pageSize=2&sortBy=publishedAt&apiKey={api_key}"
    response = requests.get(url)
    data = response.json()
 
    if response.status_code == 200 and data["status"] == "ok":
        articles = data["articles"]
        if not articles:
            return f"No news found for {topic}."
        else:
            result = ""
            for i, article in enumerate(articles, start=1):
                title = article.get('title', 'No title')
                source = article['source'].get('name', 'Unknown Source')
                result += f"{i}. {title} from {source}. "
            return result
    else:
        return "Sorry, couldn't fetch news at the moment."