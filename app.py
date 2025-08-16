# 导入 "厨房工具箱" Flask，以及处理订单格式的工具
from flask import Flask, request, jsonify
# 导入我们之前用过的 "AI 大厨电话"
import google.generativeai as genai
import os
# --- 新增代码：导入 CORS 模块 ---
from flask_cors import CORS

# --- 像之前一样，配置你的 API 密钥 ---
os.environ["GEMINI_API_KEY"] = "AIzaSyAOYMkvCk3dlj4Syz-sx88wR7H3oRk47Kg"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
# ---------------------------------------------

# 创建我们的 "厨房服务" 应用
app = Flask(__name__)
# --- 新增代码：为我们的应用启用 CORS ---
CORS(app)

# 连接到 'gemini-1.5-flash' 这位 AI 大厨
model = genai.GenerativeModel('gemini-2.5-flash')


# 定义我们的 "点餐电话号码" 和 "接单规则"
@app.route('/ask-gemini', methods=['POST'])
def ask_gemini():
    # 1. 服务员从订单(request)中，把 JSON 格式的菜谱拿出来
    order = request.get_json()
    if not order or 'question' not in order:
        # 如果订单是空的，或者没有'question'这个关键项，就告诉对方订单格式不对
        return jsonify({"error": "Invalid order! Missing 'question'."}), 400

    # 2. 从菜谱中提取具体的问题
    prompt = order['question']

    try:
        # 3. 把问题转告给 AI 大厨，等待祂做好菜
        response = model.generate_content(prompt)

        # 4. 把 AI 大厨做好的菜（回答），打包好准备送回给顾客
        return jsonify({"answer": response.text})

    except Exception as e:
        # 如果中间出了任何问题（比如大厨今天罢工了），就告诉顾客服务暂时出问题了
        print(f"An error occurred: {e}")
        return jsonify({"error": "Something went wrong with the AI chef!"}), 500


# 这行代码是启动我们的 "厨房" 服务
if __name__ == '__main__':
    # 在 0.0.0.0 地址的 5000 端口开张营业，所有人都能访问
    app.run(host='0.0.0.0', port=5000, debug=True)

# 这行代码是启动我们的 "厨房" 服务
if __name__ == '__main__':
    # 在 0.0.0.0 地址的 5000 端口开张营业，所有人都能访问
    app.run(host='0.0.0.0', port=5000, debug=True)