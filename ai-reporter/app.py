import os
from flask import Flask, render_template_string, request, jsonify
from google import genai

app = Flask(__name__)

# --- CONFIGURATION ---
API_KEY = "AIzaSyBv7HJoehRyua_WhUb9sW9tuJ7KQYu-4zI"
client = genai.Client(api_key=API_KEY)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>The AI Reporter | 2026 Edition</title>
    <style>
        body { background: #fdfaf0; font-family: 'Times New Roman', serif; padding: 20px; color: #1a1a1a; }
        .paper { max-width: 950px; margin: auto; background: #fff; padding: 40px; border: 1px solid #000; box-shadow: 12px 12px 0px #ddd; }
        header { text-align: center; border-bottom: 5px double #000; margin-bottom: 20px; }
        header h1 { font-size: 4rem; margin: 0; text-transform: uppercase; font-weight: 900; }
        .masthead { display: flex; justify-content: space-between; border-bottom: 1px solid #000; padding: 5px 0; margin-bottom: 30px; font-weight: bold; font-size: 0.85rem; text-transform: uppercase; }
        .controls { background: #f0f0f0; padding: 20px; border: 1px solid #ccc; margin-bottom: 30px; display: flex; gap: 10px; border-radius: 4px; }
        input, select, button { padding: 12px; border: 1px solid #777; font-size: 1rem; }
        button { background: #000; color: #fff; cursor: pointer; transition: 0.2s; font-weight: bold; }
        button:hover { background: #333; }
        #article-area { display: none; }
        .headline { font-size: 3rem; line-height: 1; font-weight: bold; text-align: center; margin-bottom: 25px; border-bottom: 1px solid #eee; padding-bottom: 15px; }
        .content-body { column-count: 2; column-gap: 50px; text-align: justify; line-height: 1.6; font-size: 1.15rem; white-space: pre-wrap; }
        .content-body::first-letter { float: left; font-size: 5.5rem; line-height: 0.7; padding: 10px 12px 0 0; font-weight: bold; }
        @media (max-width: 750px) { .content-body { column-count: 1; } }
    </style>
</head>
<body>
    <div class="paper">
        <header>
            <h1>The AI Reporter</h1>
            <div class="masthead">
                <span>By Satprem</span>
                <span>GLOBAL DESK</span>
                <span>Price: Free AI Tier</span>
            </div>
        </header>
        <div class="controls">
            <input type="text" id="topic" placeholder="Breaking News Topic..." style="flex: 2;">
            <input type="number" id="lines" value="35" style="width: 70px;">
            <select id="style">
                <option value="deep">In-Depth Report</option>
                <option value="crisp">Bullet Fact-Sheet</option>
            </select>
            <button onclick="generateNews()">PRINT ARTICLE</button>
        </div>
        <div id="article-area">
            <div id="res-headline" class="headline"></div>
            <div id="res-body" class="content-body"></div>
        </div>
    </div>
    <script>
        async function generateNews() {
            const btn = document.querySelector('button');
            const topic = document.getElementById('topic').value;
            const lines = document.getElementById('lines').value;
            const style = document.getElementById('style').value;
            if(!topic) return alert("Please enter a news topic.");
            btn.innerText = "PRINTING...";
            btn.disabled = true;
            try {
                const response = await fetch('/get_news', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ topic, lines, style })
                });
                const data = await response.json();
                if(data.success) {
                    document.getElementById('res-headline').innerText = data.headline;
                    document.getElementById('res-body').innerText = data.body;
                    document.getElementById('article-area').style.display = 'block';
                } else { alert("AI Error: " + data.error); }
            } catch (e) { alert("Server Connection Failed."); }
            finally { btn.innerText = "PRINT ARTICLE"; btn.disabled = false; }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/get_news', methods=['POST'])
def get_news():
    data = request.json
    topic = data.get('topic')
    target_lines = data.get('lines', 30)
    style = data.get('style')

    prompt = f"Write a professional news article about: {topic}. Length: {target_lines} lines. " \
             f"Style: {'Detailed narrative' if style == 'deep' else 'Crisp points'}. " \
             "First line: Headline. Following lines: The story content. " \
             "DO NOT include a dateline (no City name at start). No bold stars (**)."

    try:
        response = client.models.generate_content(
           model="gemini-2.5-flash", # Latest stable 2026 model
            contents=prompt
        )
        
        full_text = response.text.replace('**', '').replace('###', '').strip()
        lines_list = full_text.split('\n')
        
        headline = lines_list[0]
        body = '\n'.join(lines_list[1:]).strip()

        return jsonify({"success": True, "headline": headline, "body": body})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# This allows it to run locally, but Vercel will ignore it and handle the serving itself
if __name__ == "__main__":
    app.run()
