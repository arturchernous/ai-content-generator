from flask import Flask, request, render_template, jsonify
import openai
from dotenv import load_dotenv
import os
import sqlite3
from database import init_db

load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')
init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    posts = get_recent_posts()
    content = None
    if request.method == 'POST':
        topic = request.form['topic']
        platform = request.form['platform']
        prompt = f"Generate an engaging {platform} post about '{topic}'. Include 3-5 emojis, 4 hashtags, and a call-to-action. Keep under 150 words. Make it professional and fun."
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            content = response.choices[0].message.content.strip()
            save_post(topic, platform, content)
            posts = get_recent_posts()
        except Exception as e:
            content = f"Error: {str(e)}"
    return render_template('index.html', posts=posts, content=content)

def save_post(topic, platform, content):
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO posts (topic, platform, content) VALUES (?, ?, ?)", (topic, platform, content))
    conn.commit()
    conn.close()

def get_recent_posts():
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT topic, platform, content FROM posts ORDER BY timestamp DESC LIMIT 5")
    posts = [{'topic': row[0], 'platform': row[1], 'content': row[2]} for row in cursor.fetchall()]
    conn.close()
    return posts

@app.route('/api/generate', methods=['POST'])
def api_generate():
    data = request.json
    prompt = f"Generate {data['platform']} post on {data['topic']} with emojis and hashtags."
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
    return jsonify({'content': response.choices[0].message.content})

if __name__ == '__main__':
    app.run(debug=True, port=5000)