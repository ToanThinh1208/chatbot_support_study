Tuyệt vời! Đây là một kế hoạch chi tiết để bạn xây dựng webchat AI hỗ trợ bài tập, sử dụng Gemini API làm nòng cốt và ChatterBot để tùy chỉnh, với FastAPI cho backend và Railway để triển khai.

## Tài liệu Hướng dẫn Xây dựng Webchat AI Hỗ trợ Bài tập

**Mục tiêu:** Tạo một webchat AI cơ bản, nơi người dùng có thể đặt câu hỏi liên quan đến bài tập và nhận được câu trả lời từ Gemini API, với khảibility tùy chỉnh và fallback bằng ChatterBot.

**Công nghệ sử dụng:**

*   **Frontend:** HTML, CSS, JavaScript (cơ bản), Bootstrap 5
*   **Backend:** Python, FastAPI
*   **AI Core:** Google Gemini API
*   **Chatbot Framework (Tùy chỉnh/Fallback):** ChatterBot
*   **Deployment:** Railway.app

---

### Bước 1: Chuẩn bị

1.  **Tài khoản Google AI Studio & API Key:**
    *   Truy cập [Google AI Studio](https://aistudio.google.com/).
    *   Tạo API Key cho Gemini. Lưu lại key này cẩn thận.
2.  **Cài đặt Python:** Đảm bảo bạn đã cài đặt Python 3.8 trở lên.
3.  **Tài khoản Railway:** Đăng ký tài khoản trên [Railway.app](https://railway.app/).
4.  **IDE/Text Editor:** VS Code, PyCharm, Sublime Text, etc.
5.  **Git:** Cài đặt Git để quản lý source code và deploy lên Railway.

---

### Bước 2: Cấu trúc Thư mục Dự án

Tạo một thư mục gốc cho dự án, ví dụ `gemini_chatterbot_homework`:

```
gemini_chatterbot_homework/
├── backend/                     # Thư mục chứa code FastAPI
│   ├── main.py                  # File chính của FastAPI app
│   ├── .env                     # Chứa API key (không commit lên Git)
│   └── requirements.txt         # Danh sách các thư viện Python cần thiết
├── frontend/                    # Thư mục chứa code HTML, CSS, JS
│   ├── index.html
│   ├── style.css
│   └── script.js
├── Procfile                     # File cấu hình cho Railway
└── .gitignore                   # Các file/folder không muốn đưa lên Git
```

---

### Bước 3: Xây dựng Backend với FastAPI

1.  **Tạo môi trường ảo (khuyến khích):**
    ```bash
    cd gemini_chatterbot_homework
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

2.  **Cài đặt thư viện:**
    Tạo file `backend/requirements.txt` với nội dung:
    ```txt
    fastapi
    uvicorn[standard]
    google-generativeai
    chatterbot==1.0.5
    chatterbot-corpus
    python-dotenv
    pydantic  # Thường đi kèm FastAPI, nhưng thêm cho chắc
    ```
    (Lưu ý: `chatterbot==1.0.5` là phiên bản ổn định. Các phiên bản mới hơn có thể có thay đổi.)

    Cài đặt:
    ```bash
    pip install -r backend/requirements.txt
    ```
    Nếu có lỗi với `spacy` (dependency của ChatterBot), bạn có thể cần cài thêm:
    ```bash
    python -m spacy download en_core_web_sm
    ```

3.  **Tạo file `.env`:**
    Trong thư mục `backend/`, tạo file `.env`:
    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    ```
    Thay `YOUR_GEMINI_API_KEY_HERE` bằng API key bạn đã tạo.

4.  **Viết code `backend/main.py`:**

    ```python
    import os
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware # Để cho phép FE gọi BE
    from pydantic import BaseModel
    import google.generativeai as genai
    from chatterbot import ChatBot
    from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer
    from dotenv import load_dotenv

    # Tải biến môi trường từ .env
    load_dotenv()

    # --- Cấu hình Gemini API ---
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        print("Lỗi: GEMINI_API_KEY chưa được thiết lập trong .env")
        # exit() # Nên dừng chương trình nếu không có API key khi deploy

    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-pro') # Hoặc 'gemini-1.5-flash' cho tốc độ nhanh hơn

    # --- Cấu hình ChatterBot ---
    # Tạo một instance ChatBot mới
    # storage_adapter: Chỉ định cách lưu trữ dữ liệu (ví dụ: SQL, JSON). Mặc định là JSONFileStorageAdapter.
    # logic_adapters: Danh sách các bộ điều hợp logic mà bot sẽ sử dụng để chọn phản hồi.
    #                 'chatterbot.logic.BestMatch' là một lựa chọn phổ biến.
    #                 'chatterbot.logic.MathematicalEvaluation' cho phép tính toán cơ bản.
    # preprocessors: Các bước tiền xử lý văn bản đầu vào.
    chatbot = ChatBot(
        'HomeworkHelper',
        storage_adapter='chatterbot.storage.SQLStorageAdapter', # Dùng SQL cho bền hơn JSON, sẽ tạo file db.sqlite3
        database_uri='sqlite:///db.sqlite3', # File database sẽ được tạo trong thư mục backend
        logic_adapters=[
            {
                'import_path': 'chatterbot.logic.BestMatch',
                'default_response': 'Xin lỗi, tôi chưa hiểu ý bạn. Bạn có thể diễn đạt khác được không?',
                'maximum_similarity_threshold': 0.90 # Ngưỡng tương đồng để trả lời
            },
            # 'chatterbot.logic.MathematicalEvaluation' # Bỏ comment nếu muốn bot có thể tính toán
        ],
        preprocessors=[
            'chatterbot.preprocessors.clean_whitespace'
        ],
        read_only=True # Khi deploy, đặt read_only=True để không train lại
    )

    # --- Huấn luyện ChatterBot (chỉ chạy một lần hoặc khi cần cập nhật) ---
    # Bạn có thể tạo một script riêng để huấn luyện, hoặc bỏ phần này đi nếu chỉ dựa vào Gemini
    # Kiểm tra xem database đã có dữ liệu chưa để tránh train lại mỗi lần khởi động
    # Điều này đơn giản, trong thực tế có thể cần cơ chế phức tạp hơn
    if not os.path.exists('backend/db.sqlite3') or os.path.getsize('backend/db.sqlite3') < 10000: # Giả sử file db nhỏ là chưa train
        print("Đang huấn luyện ChatterBot...")
        trainer_corpus = ChatterBotCorpusTrainer(chatbot)
        trainer_corpus.train("chatterbot.corpus.english.greetings", # Có thể thêm tiếng Việt nếu có corpus
                             "chatterbot.corpus.english.conversations")
        # "chatterbot.corpus.vietnamese" # Thử nếu bạn cài được corpus tiếng Việt

        # Huấn luyện với dữ liệu tùy chỉnh về bài tập
        custom_training_data = [
            "Chào bạn", "Chào bạn, tôi có thể giúp gì cho bạn về bài tập?",
            "Bạn tên gì?", "Tôi là Homework Helper Bot, được tạo ra để hỗ trợ bạn.",
            "Định nghĩa của danh từ là gì?", "Danh từ là những từ chỉ người, vật, hiện tượng, khái niệm...",
            "Công thức tính diện tích hình chữ nhật?", "Diện tích hình chữ nhật bằng chiều dài nhân chiều rộng.",
            "Nguyên hàm của x^2 là gì?", "Nguyên hàm của x^2 là (x^3)/3 + C.",
            # Thêm nhiều cặp câu hỏi - trả lời về các môn học ở đây
        ]
        trainer_list = ListTrainer(chatbot)
        trainer_list.train(custom_training_data)
        print("Huấn luyện ChatterBot hoàn tất.")
    else:
        print("ChatterBot đã được huấn luyện.")


    # --- FastAPI App ---
    app = FastAPI()

    # Cấu hình CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # Cho phép tất cả origins (thay đổi thành domain cụ thể khi deploy production)
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Pydantic model cho request body
    class ChatRequest(BaseModel):
        message: str
        user_id: str = "default_user" # Có thể dùng để quản lý session/lịch sử chat

    class ChatResponse(BaseModel):
        reply: str
        source: str # "gemini" hoặc "chatterbot"

    @app.post("/api/chat", response_model=ChatResponse)
    async def chat_endpoint(request: ChatRequest):
        user_message = request.message
        print(f"Nhận được tin nhắn: {user_message}")

        # Ưu tiên sử dụng Gemini API
        try:
            # Xây dựng prompt cho Gemini để nó hiểu vai trò là người hỗ trợ bài tập
            prompt = f"""Bạn là một trợ lý AI thông minh và thân thiện, chuyên hỗ trợ giải đáp các câu hỏi liên quan đến bài tập cho học sinh.
            Hãy trả lời câu hỏi sau một cách rõ ràng, dễ hiểu và chính xác. Nếu không biết, hãy nói là bạn không biết.
            Không bịa đặt thông tin.
            Câu hỏi của học sinh: {user_message}
            Câu trả lời của bạn: """

            gemini_response = gemini_model.generate_content(prompt)

            if gemini_response.text and len(gemini_response.text.strip()) > 10: # Kiểm tra phản hồi có ý nghĩa
                print(f"Gemini trả lời: {gemini_response.text}")
                return ChatResponse(reply=gemini_response.text, source="gemini")
            else:
                # Nếu Gemini không trả lời tốt, thử ChatterBot
                print("Gemini không có câu trả lời phù hợp, thử ChatterBot...")
                raise Exception("Gemini response not suitable") # Chuyển sang ChatterBot

        except Exception as e:
            print(f"Lỗi khi gọi Gemini API hoặc Gemini không trả lời tốt: {e}")
            # Nếu Gemini lỗi hoặc không trả lời phù hợp, dùng ChatterBot
            try:
                bot_response = chatbot.get_response(user_message)
                print(f"ChatterBot trả lời: {str(bot_response)}")
                return ChatResponse(reply=str(bot_response), source="chatterbot")
            except Exception as chatter_e:
                print(f"Lỗi khi dùng ChatterBot: {chatter_e}")
                return ChatResponse(reply="Xin lỗi, tôi đang gặp chút sự cố. Vui lòng thử lại sau.", source="error")

    @app.get("/")
    async def read_root():
        return {"message": "Chào mừng bạn đến với API Chatbot Hỗ trợ Bài tập!"}

    # Để chạy local: uvicorn backend.main:app --reload --port 8000
    ```

5.  **Kiểm tra chạy local:**
    Mở terminal trong thư mục `gemini_chatterbot_homework` (đã activate `venv`):
    ```bash
    uvicorn backend.main:app --reload --port 8000
    ```
    Mở trình duyệt và truy cập `http://localhost:8000/docs` để xem giao diện Swagger UI và thử nghiệm API.

---

### Bước 4: Xây dựng Frontend (HTML, CSS, JavaScript, Bootstrap)

1.  **`frontend/index.html`:**

    ```html
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Webchat Hỗ trợ Bài tập</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="style.css">
    </head>
    <body>
        <div class="container mt-5">
            <div class="chat-container card">
                <div class="card-header bg-primary text-white">
                    <h4><i class="fas fa-brain"></i> AI Homework Helper</h4>
                </div>
                <div class="card-body chat-box" id="chatBox">
                    <!-- Tin nhắn sẽ được thêm vào đây -->
                    <div class="message bot-message">
                        <p>Chào bạn! Tôi có thể giúp gì cho bạn về bài tập hôm nay?</p>
                    </div>
                </div>
                <div class="card-footer chat-input-area">
                    <div class="input-group">
                        <input type="text" id="userInput" class="form-control" placeholder="Nhập câu hỏi của bạn..." aria-label="User input">
                        <button class="btn btn-primary" id="sendButton">
                            <i class="fas fa-paper-plane"></i> Gửi
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://kit.fontawesome.com/a076d05399.js" crossorigin="anonymous"></script> <!-- Font Awesome Icons -->
        <script src="script.js"></script>
    </body>
    </html>
    ```

2.  **`frontend/style.css`:**

    ```css
    body {
        background-color: #f4f7f6;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .chat-container {
        max-width: 700px;
        margin: auto;
        box-shadow: 0 0 15px rgba(0,0,0,0.1);
        border-radius: 10px;
        overflow: hidden; /* Để bo tròn card-header */
    }

    .card-header h4 {
        margin-bottom: 0;
    }
    .card-header i {
        margin-right: 8px;
    }

    .chat-box {
        height: 450px;
        overflow-y: auto;
        padding: 15px;
        background-color: #fff;
        display: flex;
        flex-direction: column;
    }

    .message {
        margin-bottom: 15px;
        padding: 10px 15px;
        border-radius: 18px;
        max-width: 80%;
        word-wrap: break-word;
    }

    .user-message {
        background-color: #0d6efd;
        color: white;
        align-self: flex-end;
        border-bottom-right-radius: 5px;
    }

    .bot-message {
        background-color: #e9ecef;
        color: #333;
        align-self: flex-start;
        border-bottom-left-radius: 5px;
    }
    .bot-message.gemini {
        border-left: 4px solid #4285F4; /* Màu Google */
    }
    .bot-message.chatterbot {
        border-left: 4px solid #f0ad4e; /* Màu cam cho ChatterBot */
    }
    .bot-message.error {
        border-left: 4px solid #d9534f; /* Màu đỏ cho lỗi */
    }

    .message p {
        margin-bottom: 0;
        white-space: pre-wrap; /* Giữ nguyên định dạng xuống dòng của bot */
    }

    .chat-input-area {
        background-color: #f8f9fa;
    }

    #userInput {
        border-radius: 20px 0 0 20px;
    }

    #sendButton {
        border-radius: 0 20px 20px 0;
    }
    #sendButton i {
        margin-right: 5px;
    }

    /* Typing indicator */
    .typing-indicator {
        display: flex;
        align-items: center;
        padding: 5px 10px;
        margin-left: 10px; /* Để nó không dính sát lề trái */
    }
    .typing-indicator span {
        height: 8px;
        width: 8px;
        background-color: #adb5bd;
        border-radius: 50%;
        display: inline-block;
        margin: 0 2px;
        animation: bounce 1.4s infinite ease-in-out both;
    }
    .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
    .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1.0); }
    }
    ```

3.  **`frontend/script.js`:**

    ```javascript
    const chatBox = document.getElementById('chatBox');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');

    // URL của API backend - Thay đổi nếu bạn deploy ở đâu đó khác
    const API_URL = 'http://localhost:8000/api/chat'; // Sửa khi deploy lên Railway

    // Thêm typing indicator
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('message', 'bot-message', 'typing-indicator');
        typingDiv.innerHTML = `<span></span><span></span><span></span>`;
        chatBox.appendChild(typingDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function removeTypingIndicator() {
        const typingIndicator = chatBox.querySelector('.typing-indicator');
        if (typingIndicator) {
            chatBox.removeChild(typingIndicator);
        }
    }

    function addMessageToChat(message, sender, source = '') {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        if (sender === 'user') {
            messageDiv.classList.add('user-message');
        } else {
            messageDiv.classList.add('bot-message');
            if (source) {
                messageDiv.classList.add(source); // Thêm class 'gemini' hoặc 'chatterbot'
            }
        }

        const p = document.createElement('p');
        p.textContent = message;
        messageDiv.appendChild(p);
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight; // Cuộn xuống tin nhắn mới nhất
    }

    async function sendMessage() {
        const messageText = userInput.value.trim();
        if (messageText === '') return;

        addMessageToChat(messageText, 'user');
        userInput.value = '';
        showTypingIndicator(); // Hiển thị "đang gõ"

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: messageText }),
            });

            removeTypingIndicator(); // Xóa "đang gõ"

            if (!response.ok) {
                // Thử parse lỗi từ server nếu có
                let errorMsg = `Lỗi: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMsg = errorData.detail || errorMsg;
                } catch (e) { /* không làm gì */ }
                addMessageToChat(`Lỗi từ server: ${errorMsg}`, 'bot', 'error');
                return;
            }

            const data = await response.json();
            addMessageToChat(data.reply, 'bot', data.source);

        } catch (error) {
            removeTypingIndicator(); // Xóa "đang gõ"
            console.error('Error sending message:', error);
            addMessageToChat('Không thể kết nối tới server. Vui lòng thử lại.', 'bot', 'error');
        }
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Chỉnh sửa URL API khi deploy
    // Nếu đang chạy trên Railway, URL sẽ khác
    // Ví dụ: nếu Railway cấp cho bạn domain là my-chat-app.up.railway.app
    // thì API_URL sẽ là 'https://my-chat-app.up.railway.app/api/chat'
    // Bạn có thể kiểm tra window.location.hostname để tự động điều chỉnh
    if (window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1") {
        // Giả sử URL của Railway là `https://<tên-dịch-vụ>-<tên-project>.up.railway.app`
        // Chúng ta cần tên dịch vụ và tên project
        // Cách đơn giản là bạn tự cập nhật URL khi biết domain của Railway
        // Hoặc để an toàn, bạn có thể build frontend với URL đúng khi deploy
        // Ví dụ: API_URL = 'YOUR_RAILWAY_APP_URL/api/chat';
        // Tạm thời comment ra để tránh lỗi nếu bạn chưa deploy
        // API_URL = `https://${window.location.hostname}/api/chat`;
        // console.log("Chạy trên server, API URL được cập nhật thành:", API_URL);
    }
    ```

4.  **Mở `frontend/index.html` trên trình duyệt:**
    Bạn có thể mở file `index.html` trực tiếp bằng trình duyệt để xem giao diện.
    Nếu backend (FastAPI) đang chạy ở `http://localhost:8000`, chat sẽ hoạt động.

---

### Bước 5: Chuẩn bị Deploy lên Railway

1.  **`Procfile`:**
    Trong thư mục gốc `gemini_chatterbot_homework/`, tạo file `Procfile` (không có đuôi file):
    ```Procfile
    web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
    ```
    `$PORT` là biến môi trường mà Railway sẽ cung cấp.

2.  **`.gitignore`:**
    Trong thư mục gốc `gemini_chatterbot_homework/`, tạo file `.gitignore`:
    ```gitignore
    # Python
    venv/
    __pycache__/
    *.pyc
    *.pyo
    *.pyd
    .Python
    build/
    develop-eggs/
    dist/
    downloads/
    eggs/
    .eggs/
    lib/
    lib64/
    parts/
    sdist/
    var/
    wheels/
    pip-wheel-metadata/
    share/python-wheels/
    *.egg-info/
    .installed.cfg
    *.egg
    MANIFEST
    *.manifest
    *.spec
    pip-log.txt
    pip-delete-this-directory.txt
    htmlcov/
    .tox/
    .nox/
    .coverage
    .coverage.*
    .cache
    nosetests.xml
    coverage.xml
    *.cover
    *.log
    .mypy_cache/
    .dmypy.json
    dmypy.json
    .hypothesis/
    target/ # Cho Rust nếu có dùng (ví dụ Spacy)

    # Environment variables
    backend/.env
    .env.*

    # SQLite
    backend/db.sqlite3 # Không nên commit database đã train nếu nó lớn, hoặc train lại trên server
                       # Tuy nhiên, nếu nhỏ và muốn có sẵn dữ liệu, bạn có thể commit
                       # Với Railway, filesystem là ephemeral, nên DB sẽ mất nếu restart/redeploy
                       # -> Cần giải pháp database ổn định hơn (Postgres, MySQL trên Railway)
                       # Hoặc chấp nhận train lại mỗi lần deploy (nếu nhanh)

    # IDE / Editor specific
    .vscode/
    .idea/
    *.sublime-project
    *.sublime-workspace

    # OS specific
    .DS_Store
    Thumbs.db
    ```
    **Quan trọng về `backend/db.sqlite3`:**
    *   Nếu bạn commit file `db.sqlite3`, ChatterBot sẽ có sẵn dữ liệu khi deploy.
    *   Tuy nhiên, trên Railway (và nhiều PaaS khác), filesystem là *ephemeral*. Nghĩa là mỗi lần deploy lại hoặc restart, file này có thể bị mất hoặc reset.
    *   **Giải pháp tốt hơn:**
        1.  Sử dụng một database service do Railway cung cấp (ví dụ: PostgreSQL) và cấu hình `SQLStorageAdapter` của ChatterBot để kết nối tới đó.
        2.  Chạy script huấn luyện ChatterBot như một phần của quá trình build hoặc khi ứng dụng khởi động lần đầu (nếu quá trình huấn luyện nhanh).
        3.  Đối với demo này, việc train lại khi khởi động (như code `main.py` đang làm nếu `db.sqlite3` không tồn tại hoặc nhỏ) là chấp nhận được.

---

### Bước 6: Deploy lên Railway

1.  **Khởi tạo Git repository:**
    ```bash
    cd gemini_chatterbot_homework
    git init
    git add .
    git commit -m "Initial commit: Basic Gemini and ChatterBot webchat"
    ```

2.  **Tạo project trên Railway:**
    *   Đăng nhập Railway.
    *   Nhấp "New Project".
    *   Chọn "Deploy from GitHub repo".
    *   Kết nối tài khoản GitHub của bạn và chọn repository `gemini_chatterbot_homework`.
    *   Railway sẽ tự động phát hiện `Procfile` (hoặc bạn có thể cần cấu hình Build Command và Start Command).
        *   **Build Command:** Thường Railway sẽ tự động chạy `pip install -r backend/requirements.txt`.
        *   **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` (đã có trong `Procfile`).

3.  **Cấu hình Environment Variables trên Railway:**
    *   Trong project của bạn trên Railway, vào tab "Variables".
    *   Thêm biến `GEMINI_API_KEY` với giá trị là API key của bạn.
    *   Thêm biến `PYTHON_VERSION` (nếu cần, ví dụ: `3.10` hoặc `3.11`).

4.  **Deploy:**
    *   Railway sẽ tự động build và deploy khi bạn push code lên GitHub (nhánh main/master).
    *   Sau khi deploy thành công, Railway sẽ cung cấp cho bạn một URL dạng `your-project-name.up.railway.app`.

5.  **Cập nhật API_URL trong `frontend/script.js`:**
    Khi bạn đã có URL public từ Railway, hãy cập nhật biến `API_URL` trong `frontend/script.js`:
    ```javascript
    // const API_URL = 'http://localhost:8000/api/chat';
    const API_URL = 'https://your-project-name.up.railway.app/api/chat'; // THAY THẾ URL NÀY
    ```
    Sau đó, commit và push lại thay đổi này lên GitHub để Railway deploy lại.

    **Cách phục vụ Frontend từ FastAPI (Tùy chọn nâng cao):**
    Thay vì deploy frontend riêng, bạn có thể cấu hình FastAPI để phục vụ các file tĩnh (HTML, CSS, JS). Điều này giúp đơn giản hóa việc deploy chỉ còn 1 service.
    Trong `backend/main.py`:
    ```python
    from fastapi.staticfiles import StaticFiles

    # ... (các import khác)

    app = FastAPI()

    # ... (CORS middleware)

    # --- API Endpoints ---
    # @app.post("/api/chat", ...)
    # @app.get("/")

    # --- Phục vụ file tĩnh cho Frontend ---
    # Đặt các file frontend (index.html, style.css, script.js)
    # vào một thư mục con, ví dụ `backend/static_frontend`
    # và copy các file từ `frontend/` vào đó.
    # app.mount("/", StaticFiles(directory="backend/static_frontend", html=True), name="static")
    ```
    Nếu làm theo cách này, bạn chỉ cần deploy thư mục `backend`. Khi người dùng truy cập vào URL gốc của Railway app, `index.html` sẽ được phục vụ.

---

### Bước 7: Tùy chỉnh và Cải thiện

1.  **Huấn luyện ChatterBot kỹ hơn:**
    *   Tạo các file corpus tùy chỉnh (định dạng YAML) cho từng môn học hoặc chủ đề cụ thể.
    *   Ví dụ: `data/toan.yml`, `data/ly.yml`, `data/van.yml`.
    *   Sử dụng `ChatterBotCorpusTrainer` để train từ các file này.
    *   Tham khảo tài liệu của ChatterBot về cách tạo corpus.
2.  **Cải thiện Prompt cho Gemini:**
    *   Thử nghiệm với các prompt khác nhau để Gemini hiểu rõ hơn vai trò và đưa ra câu trả lời phù hợp nhất cho việc hỗ trợ bài tập.
    *   Có thể thêm ví dụ (few-shot prompting) vào prompt.
3.  **Logic kết hợp Gemini và ChatterBot:**
    *   Hiện tại, logic là: Gemini -> (nếu thất bại/không tốt) -> ChatterBot.
    *   Bạn có thể thêm logic phức tạp hơn:
        *   Nếu câu hỏi chứa từ khóa cụ thể (ví dụ: "chào", "bạn là ai") -> ưu tiên ChatterBot.
        *   Đánh giá chất lượng câu trả lời của Gemini, nếu thấp -> thử ChatterBot.
4.  **Quản lý Lịch sử Chat:**
    *   Lưu trữ lịch sử chat (cho từng `user_id`) để Gemini có ngữ cảnh tốt hơn cho các câu hỏi tiếp theo. Gemini API hỗ trợ chat session.
5.  **Giao diện Người dùng (UI/UX):**
    *   Thêm hiệu ứng "đang gõ...". (Đã thêm trong ví dụ JS)
    *   Hiển thị avatar cho user và bot.
    *   Cho phép copy code/công thức từ câu trả lời của bot.
6.  **Xử lý lỗi tốt hơn:**
    *   Thông báo lỗi thân thiện hơn cho người dùng.
7.  **Database ổn định cho ChatterBot trên Railway:**
    *   Như đã đề cập, nếu muốn dữ liệu ChatterBot tồn tại qua các lần deploy, hãy sử dụng một dịch vụ database (ví dụ: PostgreSQL add-on của Railway) và cấu hình `SQLStorageAdapter` tương ứng.

---

Chúc bạn thành công với dự án webchat AI của mình! Đây là một dự án rất thú vị và có nhiều tiềm năng để phát triển thêm.


Hãy thêm tính năng upload file, ảnh của ứng dụng, 1 số tính năng khác, như lịch sử

Dùng supabase để xây dựng backend và lưu trữ