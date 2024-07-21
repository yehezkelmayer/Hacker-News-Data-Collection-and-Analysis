import requests
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_top_stories():
    url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
    response = requests.get(url)
    top_stories = response.json()
    return top_stories

def get_story_details(story_id):
    url = f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
    response = requests.get(url)
    story_details = response.json()
    return story_details

def save_stories_to_csv(stories):
    with open('hacker_news_stories.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'url', 'score', 'author', 'time', 'num_comments']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_story = {executor.submit(get_story_details, story_id): story_id for story_id in stories}
            for future in as_completed(future_to_story):
                story = future.result()
                writer.writerow({
                    'title': story.get('title', ''),
                    'url': story.get('url', ''),
                    'score': story.get('score', 0),
                    'author': story.get('by', ''),
                    'time': datetime.fromtimestamp(story.get('time', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                    'num_comments': story.get('descendants', 0)
                })

def analyze_and_plot(data):
    titles = [story['title'] for story in data]
    scores = [story['score'] for story in data]

    plt.figure(figsize=(10, 7))
    plt.pie(scores, labels=titles, autopct='%1.1f%%', startangle=140, colors=plt.cm.tab20.colors)
    plt.title('Distribution of Scores for Top Stories')
    plt.axis('equal')  
    plt.tight_layout()
    plt.savefig('hacker_news_pie_chart.png')
    plt.show()

def main():
    top_stories = get_top_stories()
    save_stories_to_csv(top_stories)
    
    stories_data = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_story = {executor.submit(get_story_details, story_id): story_id for story_id in top_stories[:10]}
        for future in as_completed(future_to_story):
            story_details = future.result()
            stories_data.append({
                'title': story_details.get('title', ''),
                'url': story_details.get('url', ''),
                'score': story_details.get('score', 0),
                'author': story_details.get('by', ''),
                'time': datetime.fromtimestamp(story_details.get('time', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                'num_comments': story_details.get('descendants', 0)
            })
    
    analyze_and_plot(stories_data)

if __name__ == '__main__':
    main()

