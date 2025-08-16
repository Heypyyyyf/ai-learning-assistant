import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
# --- 新的导入 ---
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

# --- 基础应用设置 ---
app = Flask(__name__)
CORS(app)

# --- 数据库配置 ---
# 我们从环境变量中获取数据库 URL 以确保安全
db_url = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 可选：减少开销
db = SQLAlchemy(app)

# --- Gemini API 配置 ---
# 我们从环境变量中获取 Gemini 密钥
gemini_api_key = os.environ.get('GEMINI_API_KEY')
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
else:
    print("GEMINI_API_KEY environment variable not set.")


# --------------------------------

# --- 数据库模型定义 ---
# 这个类定义了我们数据库中 'conversations' 表的结构。
class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Conversation {self.id}>'


# --- 创建数据库表 ---
# 这确保了上面定义的表会在我们的数据库中被创建（如果它还不存在）。
with app.app_context():
    db.create_all()


# -----------------------------

# --- API 端点 ---
@app.route('/ask-gemini', methods=['POST'])
def ask_gemini():
    order = request.get_json()
    if not order or 'question' not in order:
        return jsonify({"error": "Invalid order! Missing 'question'."}), 400

    prompt = order['question']

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        ai_answer = response.text

        # --- 新代码：保存到数据库 ---
        # 使用我们的 Conversation 模型创建一个新的对话记录
        new_conversation = Conversation(
            question=prompt,
            answer=ai_answer
        )
        # 将新记录添加到会话中，并将其提交到数据库
        db.session.add(new_conversation)
        db.session.commit()
        # ---------------------------------

        return jsonify({"answer": ai_answer})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "Something went wrong with the AI chef!"}), 500


# --- 标准 Flask 运行命令 (用于本地测试) ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)