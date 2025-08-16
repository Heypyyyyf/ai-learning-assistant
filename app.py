import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

# --- 基础应用设置 ---
app = Flask(__name__)
CORS(app)

# --- 数据库配置 ---
db_url = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Gemini API 配置 ---
gemini_api_key = os.environ.get('GEMINI_API_KEY')
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
else:
    print("GEMINI_API_KEY environment variable not set.")


# --- 数据库模型定义 ---
class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Conversation {self.id}>'


# --- 创建数据库表 ---
with app.app_context():
    db.create_all()


# --- API 端点 ---
@app.route('/ask-gemini', methods=['POST'])
def ask_gemini():
    order = request.get_json()
    if not order or 'question' not in order:
        return jsonify({"error": "Invalid order! Missing 'question'."}), 400

    prompt = order['question']

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        ai_answer = response.text

        new_conversation = Conversation(
            question=prompt,
            answer=ai_answer
        )
        db.session.add(new_conversation)
        db.session.commit()

        return jsonify({"answer": ai_answer})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "Something went wrong with the AI chef!"}), 500


# --- 新功能：获取对话历史 ---
@app.route('/get-history', methods=['GET'])
def get_history():
    try:
        # 查询数据库中的所有对话，按时间戳最新优先排序
        conversations = Conversation.query.order_by(Conversation.timestamp.desc()).all()

        # 将数据格式化为字典列表（以便与JSON兼容）
        history = []
        for conv in conversations:
            history.append({
                "id": conv.id,
                "question": conv.question,
                "answer": conv.answer,
                "timestamp": conv.timestamp.isoformat()
            })

        return jsonify(history)

    except Exception as e:
        print(f"An error occurred while fetching history: {e}")
        return jsonify({"error": "Could not retrieve conversation history."}), 500


# ---------------------------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)