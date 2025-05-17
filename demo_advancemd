Tuyệt vời! Việc tích hợp Supabase sẽ mang lại nhiều lợi ích, đặc biệt là về lưu trữ dữ liệu có cấu trúc (lịch sử chat, thông tin file), xác thực người dùng, và lưu trữ file.

Dưới đây là kế hoạch chi tiết được cập nhật, tích hợp Supabase làm backend chính, sử dụng Edge Functions của Supabase (Deno/TypeScript) cho logic API, và vẫn giữ Gemini làm AI core. ChatterBot sẽ được xem xét như một fallback có thể chạy trên một service riêng (ví dụ Railway như kế hoạch cũ) nếu cần thiết, hoặc chúng ta có thể tìm cách đơn giản hóa phần fallback.

## Tài liệu Hướng dẫn Xây dựng Webchat AI Hỗ trợ Bài tập (với Supabase)

**Mục tiêu:** Tạo một webchat AI nâng cao, nơi người dùng có thể đặt câu hỏi, tải lên file/ảnh liên quan đến bài tập, xem lại lịch sử chat và nhận được câu trả lời từ Gemini API. Supabase sẽ quản lý backend, dữ liệu và lưu trữ file.

**Công nghệ sử dụng:**

*   **Frontend:** HTML, CSS, JavaScript (hiện đại), Bootstrap 5 (hoặc Tailwind CSS/framework khác)
*   **Backend:** Supabase (PostgreSQL, Auth, Storage, Edge Functions - Deno/TypeScript)
*   **AI Core:** Google Gemini API (bao gồm Gemini Vision cho xử lý ảnh)
*   **Chatbot Framework (Tùy chỉnh/Fallback - Tùy chọn):** ChatterBot (có thể deploy riêng trên Railway nếu cần)
*   **Deployment:**
    *   Frontend: Vercel, Netlify, GitHub Pages, hoặc Supabase Storage.
    *   Supabase Edge Functions: Tích hợp sẵn.
    *   ChatterBot (nếu dùng): Railway.app.

---

### Bước 1: Chuẩn bị

1.  **Tài khoản Google AI Studio & API Key:**
    *   Truy cập [Google AI Studio](https://aistudio.google.com/).
    *   Tạo API Key cho Gemini. Lưu lại key này cẩn thận.
2.  **Tài khoản Supabase:**
    *   Đăng ký tài khoản trên [Supabase.io](https://supabase.io/).
    *   Tạo một Project mới. Lưu lại **Project URL** và **anon public key**. Bạn cũng sẽ cần **service_role key** cho một số hoạt động backend.
3.  **Cài đặt Supabase CLI:**
    ```bash
    npm install supabase --save-dev # Hoặc global: npm install -g supabase
    # Đăng nhập
    supabase login
    ```
4.  **Cài đặt Deno:** Supabase Edge Functions sử dụng Deno. Cài đặt từ [deno.land](https://deno.land/).
5.  **Cài đặt Python (Nếu vẫn muốn dùng ChatterBot):** Đảm bảo bạn đã cài đặt Python 3.8 trở lên.
6.  **Tài khoản Railway (Nếu dùng ChatterBot trên Railway):** Đăng ký tài khoản trên [Railway.app](https://railway.app/).
7.  **IDE/Text Editor:** VS Code (khuyến khích với Deno extension), PyCharm, etc.
8.  **Git:** Cài đặt Git.

---

### Bước 2: Cấu trúc Thư mục Dự án (Cập nhật)

```
gemini_supabase_homework/
├── supabase/                    # Cấu hình và Edge Functions của Supabase
│   ├── functions/               # Thư mục chứa các Edge Functions
│   │   └── chat_handler/        # Ví dụ một Edge Function
│   │       └── index.ts
│   │   └── (các functions khác...)
│   └── migrations/              # SQL migrations cho database schema
│   └── config.toml              # Cấu hình project Supabase local
├── frontend/                    # Thư mục chứa code HTML, CSS, JS
│   ├── index.html
│   ├── style.css
│   └── script.js
│   └── (assets, images...)
├── chatterbot_fallback/ (TÙY CHỌN - nếu dùng ChatterBot trên Railway)
│   ├── main.py
│   ├── requirements.txt
│   ├── Procfile
│   └── .env
├── .gitignore
└── README.md
```

---

### Bước 3: Thiết lập Supabase Project và Database

1.  **Khởi tạo Supabase trong dự án local:**
    ```bash
    cd gemini_supabase_homework
    supabase init # Tạo thư mục supabase/
    supabase login # Nếu chưa làm
    supabase link --project-ref YOUR_PROJECT_ID # YOUR_PROJECT_ID lấy từ URL dashboard Supabase
    supabase start # Khởi động Supabase stack local (Docker cần chạy)
    ```

2.  **Thiết kế Database Schema:**
    Trong Supabase Studio (Dashboard của project trên Supabase.io) hoặc bằng cách tạo file migration:
    *   **Bảng `users`:** Supabase Auth tự quản lý, nhưng bạn có thể thêm cột `metadata` nếu cần.
    *   **Bảng `chat_sessions` (Tùy chọn, để nhóm tin nhắn):**
        *   `id` (uuid, primary key, default: `uuid_generate_v4()`)
        *   `user_id` (uuid, foreign key to `auth.users.id`)
        *   `created_at` (timestamp with time zone, default: `now()`)
        *   `session_title` (text, optional)
    *   **Bảng `messages` (Lịch sử chat):**
        *   `id` (uuid, primary key, default: `uuid_generate_v4()`)
        *   `session_id` (uuid, foreign key to `chat_sessions.id`)
        *   `user_id` (uuid, foreign key to `auth.users.id`) // Để dễ query tin nhắn của user
        *   `content` (text, not null)
        *   `sender` (text, 'user' or 'ai', not null)
        *   `source_ai` (text, 'gemini', 'chatterbot', 'gemini-vision', null)
        *   `file_url` (text, nullable, link đến file trong Supabase Storage nếu có)
        *   `metadata` (jsonb, nullable, chứa thêm thông tin nếu cần)
        *   `created_at` (timestamp with time zone, default: `now()`)

    Tạo file migration (ví dụ: `supabase/migrations/YYYYMMDDHHMMSS_create_chat_tables.sql`):
    ```sql
    -- Bảng chat_sessions
    CREATE TABLE public.chat_sessions (
        id uuid NOT NULL DEFAULT extensions.uuid_generate_v4(),
        user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
        session_title TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        PRIMARY KEY (id)
    );
    -- Cho phép RLS và tạo policies sau

    -- Bảng messages
    CREATE TABLE public.messages (
        id uuid NOT NULL DEFAULT extensions.uuid_generate_v4(),
        session_id uuid NOT NULL REFERENCES public.chat_sessions(id) ON DELETE CASCADE,
        user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE, -- Denormalize for easier RLS/querying
        content TEXT NOT NULL,
        sender TEXT NOT NULL CHECK (sender IN ('user', 'ai')),
        source_ai TEXT CHECK (source_ai IN ('gemini', 'chatterbot', 'gemini-vision')),
        file_url TEXT,
        metadata JSONB,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        PRIMARY KEY (id)
    );
    -- Cho phép RLS và tạo policies sau

    -- Kích hoạt Realtime cho bảng messages
    ALTER PUBLICATION supabase_realtime ADD TABLE public.messages;

    -- Policies (Ví dụ cơ bản - CẦN TINH CHỈNH CẨN THẬN CHO PRODUCTION)
    -- Chat Sessions
    ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;
    CREATE POLICY "Users can see their own sessions."
      ON public.chat_sessions FOR SELECT
      USING (auth.uid() = user_id);
    CREATE POLICY "Users can create their own sessions."
      ON public.chat_sessions FOR INSERT
      WITH CHECK (auth.uid() = user_id);
    CREATE POLICY "Users can update their own sessions."
      ON public.chat_sessions FOR UPDATE
      USING (auth.uid() = user_id);

    -- Messages
    ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;
    CREATE POLICY "Users can see their own messages."
      ON public.messages FOR SELECT
      USING (auth.uid() = user_id);
    CREATE POLICY "Users can insert their own messages."
      ON public.messages FOR INSERT
      WITH CHECK (auth.uid() = user_id AND sender = 'user'); -- User chỉ có thể gửi tin nhắn 'user'
    -- AI (Edge Function) sẽ cần quyền để insert tin nhắn 'ai' (sử dụng service_role key)
    ```
    Chạy migration: `supabase db push` (nếu dùng local dev) hoặc dán SQL vào SQL Editor trên Supabase.

3.  **Cấu hình Supabase Storage:**
    *   Trong Supabase Studio > Storage.
    *   Tạo một Bucket mới, ví dụ `homework_files`.
    *   Thiết lập Policies cho Bucket:
        *   Người dùng đã xác thực có thể upload file.
        *   File có thể được đọc public nếu cần, hoặc chỉ bởi người dùng sở hữu (phức tạp hơn).
        *   Ví dụ policy cho phép user đã login upload:
            ```sql
            -- Trong Storage > Policies cho bucket 'homework_files'
            -- Cho phép người dùng đã xác thực upload (INSERT)
            CREATE POLICY "Authenticated users can upload files"
            FOR INSERT
            TO authenticated
            WITH CHECK (bucket_id = 'homework_files');

            -- Cho phép người dùng đã xác thực đọc file của chính họ (SELECT)
            -- Điều này cần bạn lưu `auth.uid()` vào metadata của file khi upload, hoặc dùng tên file/path chứa user_id.
            -- Ví dụ đơn giản hơn: Cho phép đọc nếu user đã login và biết URL (cần security by obscurity hoặc URL có token)
            CREATE POLICY "Authenticated users can read files"
            FOR SELECT
            TO authenticated
            USING (bucket_id = 'homework_files');
            ```

---

### Bước 4: Xây dựng Backend với Supabase Edge Functions (TypeScript/Deno)

1.  **Tạo Edge Function:**
    ```bash
    supabase functions new chat_handler
    ```
    Điều này sẽ tạo `supabase/functions/chat_handler/index.ts`.

2.  **Cài đặt biến môi trường cho Edge Functions:**
    Trong Supabase Dashboard > Project Settings > Edge Functions, thêm `GEMINI_API_KEY`.
    Khi phát triển local, tạo file `supabase/.env.local` (được .gitignore):
    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    SUPABASE_SERVICE_ROLE_KEY="YOUR_SUPABASE_SERVICE_ROLE_KEY"
    CHATTERBOT_FALLBACK_URL="http://localhost:8001/api/chatterbot" # Nếu dùng ChatterBot fallback
    ```

3.  **Viết code `supabase/functions/chat_handler/index.ts`:**

    ```typescript
    import { serve } from 'https://deno.land/std@0.177.0/http/server.ts'
    import { corsHeaders } from '../_shared/cors.ts' // File shared cho CORS headers
    import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
    import { GoogleGenerativeAI, HarmCategory, HarmBlockThreshold } from 'npm:@google/generative-ai@0.1.3' // Cập nhật phiên bản nếu cần

    // --- Gemini AI Setup ---
    const GEMINI_API_KEY = Deno.env.get("GEMINI_API_KEY");
    if (!GEMINI_API_KEY) {
      console.error("GEMINI_API_KEY is not set.");
    }
    const genAI = new GoogleGenerativeAI(GEMINI_API_KEY!);
    const geminiModel = genAI.getGenerativeModel({ model: "gemini-pro" }); // Text only
    const geminiVisionModel = genAI.getGenerativeModel({ model: "gemini-pro-vision" }); // For images/files

    // --- Helper function to convert image URL/data to Gemini Part ---
    async function urlToGenerativePart(url: string, mimeType: string): Promise<{inlineData: {data: string, mimeType: string}}> {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`Failed to fetch image: ${response.statusText}`);
      const imageBuffer = await response.arrayBuffer();
      const PImageBase64 = base64.fromByteArray(new Uint8Array(imageBuffer)); // Cần import base64
      return {
        inlineData: {
          data: PImageBase64,
          mimeType,
        },
      };
    }
    // (Cần import thư viện base64, ví dụ: import * as base64 from "https://deno.land/std@0.200.0/encoding/base64.ts"; )


    serve(async (req: Request) => {
      // Handle CORS preflight requests
      if (req.method === 'OPTIONS') {
        return new Response('ok', { headers: corsHeaders })
      }

      try {
        const supabaseClientAdmin = createClient( // Dùng service role key để ghi log AI messages
            Deno.env.get('SUPABASE_URL') ?? '',
            Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
        );

        const { message, user_id, session_id, file_url, file_mime_type } = await req.json();

        if (!user_id || !session_id) {
            return new Response(JSON.stringify({ error: "User ID and Session ID are required." }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' },
                status: 400,
            });
        }

        // 1. Lưu tin nhắn của người dùng vào DB
        const { error: userMsgError } = await supabaseClientAdmin.from('messages').insert({
            session_id: session_id,
            user_id: user_id,
            content: message,
            sender: 'user',
            file_url: file_url || null
        });
        if (userMsgError) throw userMsgError;

        let aiReply = "Xin lỗi, tôi chưa thể xử lý yêu cầu này.";
        let aiSource = "error";

        // 2. Xử lý với Gemini
        try {
            let prompt = `Bạn là một trợ lý AI thông minh và thân thiện, chuyên hỗ trợ giải đáp các câu hỏi liên quan đến bài tập cho học sinh.
            Hãy trả lời câu hỏi sau một cách rõ ràng, dễ hiểu và chính xác. Nếu không biết, hãy nói là bạn không biết. Không bịa đặt thông tin.
            Câu hỏi của học sinh: ${message}`;

            if (file_url && file_mime_type && GEMINI_API_KEY) { // Có file đính kèm
                const imagePart = await urlToGenerativePart(file_url, file_mime_type); // Cần triển khai hàm này
                prompt += "\n\n(Học sinh đã đính kèm một file/hình ảnh. Hãy xem xét nó nếu liên quan đến câu hỏi.)";
                const result = await geminiVisionModel.generateContent([prompt, imagePart]);
                aiReply = result.response.text();
                aiSource = "gemini-vision";
            } else if (GEMINI_API_KEY) { // Chỉ có text
                const result = await geminiModel.generateContent(prompt);
                aiReply = result.response.text();
                aiSource = "gemini";
            }

            if (!aiReply || aiReply.trim().length < 5) { // Nếu Gemini không trả lời tốt
                throw new Error("Gemini response not suitable");
            }

        } catch (geminiError) {
            console.error("Gemini API error:", geminiError.message);
            // Thử Fallback (ví dụ ChatterBot nếu có)
            const chatterbotFallbackUrl = Deno.env.get("CHATTERBOT_FALLBACK_URL");
            if (chatterbotFallbackUrl) {
                try {
                    const fallbackResponse = await fetch(chatterbotFallbackUrl, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: message })
                    });
                    if (fallbackResponse.ok) {
                        const fallbackData = await fallbackResponse.json();
                        aiReply = fallbackData.reply;
                        aiSource = "chatterbot";
                    } else {
                        console.warn("ChatterBot fallback failed:", fallbackResponse.status);
                    }
                } catch (fallbackErr) {
                    console.error("Error calling ChatterBot fallback:", fallbackErr.message);
                }
            }
            // Nếu fallback cũng thất bại, aiReply vẫn là giá trị mặc định ban đầu
        }

        // 3. Lưu tin nhắn của AI vào DB
        const { error: aiMsgError } = await supabaseClientAdmin.from('messages').insert({
            session_id: session_id,
            user_id: user_id, // Gán user_id để dễ query và RLS
            content: aiReply,
            sender: 'ai',
            source_ai: aiSource
        });
        if (aiMsgError) throw aiMsgError;

        return new Response(JSON.stringify({ reply: aiReply, source: aiSource }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 200,
        });

      } catch (error) {
        console.error("Handler error:", error.message);
        return new Response(JSON.stringify({ error: error.message }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 500,
        });
      }
    });

    // Tạo file supabase/functions/_shared/cors.ts
    // export const corsHeaders = {
    //   'Access-Control-Allow-Origin': '*', // Hoặc domain cụ thể của frontend
    //   'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
    // };
    ```
    **Lưu ý về `urlToGenerativePart`:** Bạn cần triển khai hàm này để tải file từ Supabase Storage URL và chuyển đổi nó sang định dạng base64 mà Gemini Vision API yêu cầu. Bạn sẽ cần một thư viện để xử lý base64 trong Deno, ví dụ `https://deno.land/std/encoding/base64.ts`.

4.  **Triển khai và Test Edge Function local:**
    ```bash
    supabase functions serve --env-file ./supabase/.env.local --no-verify-jwt # --no-verify-jwt để test dễ hơn, bỏ khi deploy
    ```
    Test bằng Postman hoặc `curl` đến `http://localhost:54321/functions/v1/chat_handler`.

---

### Bước 4.5: (Tùy chọn) Backend cho ChatterBot Fallback (Python/FastAPI trên Railway)

Nếu bạn vẫn muốn ChatterBot làm fallback:
1.  Sử dụng lại code từ kế hoạch ban đầu cho `chatterbot_fallback/main.py` và `requirements.txt`.
2.  Sửa đổi endpoint của FastAPI (ví dụ `/api/chatterbot`) để chỉ nhận tin nhắn và trả lời, không cần logic phức tạp về Gemini.
3.  Deploy lên Railway, và lấy URL của service đó để đặt vào biến `CHATTERBOT_FALLBACK_URL` trong Supabase.

---

### Bước 5: Xây dựng Frontend (HTML, CSS, JavaScript)

1.  **Cài đặt `supabase-js`:**
    ```html
    <!-- Trong index.html -->
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    ```

2.  **`frontend/script.js` (Cập nhật):**

    ```javascript
    // --- Supabase Client Setup ---
    const SUPABASE_URL = 'YOUR_SUPABASE_URL'; // Lấy từ Supabase Dashboard
    const SUPABASE_ANON_KEY = 'YOUR_SUPABASE_ANON_KEY'; // Lấy từ Supabase Dashboard
    const supabase = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

    const chatBox = document.getElementById('chatBox');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const fileInput = document.getElementById('fileInput'); // Thêm input file
    const loginButton = document.getElementById('loginButton');
    const logoutButton = document.getElementById('logoutButton');
    const authUi = document.getElementById('authUi'); // Div chứa login/logout
    const chatUi = document.getElementById('chatUi'); // Div chứa chat
    const sessionList = document.getElementById('sessionList'); // Để hiển thị danh sách session

    // URL của Supabase Edge Function
    const API_URL = `${SUPABASE_URL}/functions/v1/chat_handler`;

    let currentUser = null;
    let currentSessionId = null;

    // --- Authentication ---
    async function handleAuth() {
        const { data: { session }, error } = await supabase.auth.getSession();
        if (session) {
            currentUser = session.user;
            authUi.style.display = 'none';
            chatUi.style.display = 'flex'; // Hoặc block, tùy layout
            logoutButton.style.display = 'block';
            loadUserSessions();
            // Nếu không có session nào, tạo một session mới
            if (!currentSessionId) {
                 await createNewSession("New Chat");
            }
        } else {
            authUi.style.display = 'block';
            chatUi.style.display = 'none';
            logoutButton.style.display = 'none';
        }
    }

    loginButton.addEventListener('click', async () => {
        const { error } = await supabase.auth.signInWithOAuth({
            provider: 'google', // Hoặc 'github', 'azure' etc.
            // options: { redirectTo: window.location.href } // Để quay lại trang sau khi login
        });
        if (error) console.error("Login error:", error.message);
    });

    logoutButton.addEventListener('click', async () => {
        const { error } = await supabase.auth.signOut();
        if (error) console.error("Logout error:", error.message);
        else {
            currentUser = null;
            currentSessionId = null;
            chatBox.innerHTML = ''; // Xóa tin nhắn cũ
            sessionList.innerHTML = '';
            handleAuth();
        }
    });

    supabase.auth.onAuthStateChange((_event, session) => {
        currentUser = session?.user ?? null;
        handleAuth();
    });


    // --- Chat Sessions ---
    async function loadUserSessions() {
        if (!currentUser) return;
        sessionList.innerHTML = '<h6>Chat History</h6>'; // Reset list
        const { data: sessions, error } = await supabase
            .from('chat_sessions')
            .select('id, session_title, created_at')
            .eq('user_id', currentUser.id)
            .order('created_at', { ascending: false });

        if (error) {
            console.error("Error loading sessions:", error);
            return;
        }

        if (sessions && sessions.length > 0) {
            sessions.forEach(session => {
                const li = document.createElement('li');
                li.className = 'list-group-item list-group-item-action';
                li.textContent = session.session_title || new Date(session.created_at).toLocaleDateString();
                li.dataset.sessionId = session.id;
                li.addEventListener('click', () => loadMessagesForSession(session.id));
                sessionList.appendChild(li);
            });
            // Tự động chọn session mới nhất
            if (!currentSessionId && sessions[0]) {
                loadMessagesForSession(sessions[0].id);
            }
        } else {
            // Nếu không có session, tạo một session mới
            await createNewSession("My First Chat");
        }
    }

    async function createNewSession(title = "New Chat") {
        if (!currentUser) return;
        const { data, error } = await supabase
            .from('chat_sessions')
            .insert({ user_id: currentUser.id, session_title: title })
            .select()
            .single();

        if (error) {
            console.error("Error creating new session:", error);
            return;
        }
        if (data) {
            currentSessionId = data.id;
            chatBox.innerHTML = ''; // Xóa tin nhắn cũ
            addMessageToChat(`Chào bạn! Tôi có thể giúp gì cho bạn trong phiên "${title}" này?`, 'bot');
            await loadUserSessions(); // Tải lại danh sách session để hiển thị session mới
            // Đánh dấu session mới là active trong UI (nếu cần)
             const activeSessionElement = sessionList.querySelector(`[data-session-id="${currentSessionId}"]`);
            if (activeSessionElement) {
                // Bỏ active class khỏi các session khác
                sessionList.querySelectorAll('li').forEach(li => li.classList.remove('active'));
                activeSessionElement.classList.add('active');
            }
        }
    }
    // Thêm nút "New Chat"
    document.getElementById('newChatButton')?.addEventListener('click', () => createNewSession(`Chat ${new Date().toLocaleTimeString()}`));


    async function loadMessagesForSession(sessionId) {
        if (!currentUser) return;
        currentSessionId = sessionId;
        chatBox.innerHTML = ''; // Xóa tin nhắn hiện tại

        // Đánh dấu session được chọn là active
        sessionList.querySelectorAll('li').forEach(li => {
            if (li.dataset.sessionId === sessionId) li.classList.add('active');
            else li.classList.remove('active');
        });


        const { data: messages, error } = await supabase
            .from('messages')
            .select('*')
            .eq('session_id', sessionId)
            .order('created_at', { ascending: true });

        if (error) {
            console.error("Error loading messages:", error);
            return;
        }
        messages.forEach(msg => addMessageToChat(msg.content, msg.sender, msg.source_ai, msg.file_url));
    }


    // --- File Upload ---
    async function uploadFile(file) {
        if (!currentUser || !file) return null;
        const fileName = `${currentUser.id}/${Date.now()}_${file.name}`;
        const { data, error } = await supabase.storage
            .from('homework_files') // Tên bucket của bạn
            .upload(fileName, file);

        if (error) {
            console.error('Error uploading file:', error);
            addMessageToChat(`Lỗi upload file: ${error.message}`, 'bot', 'error');
            return null;
        }
        // Lấy public URL (hoặc signed URL nếu bucket private)
        const { data: { publicUrl } } = supabase.storage.from('homework_files').getPublicUrl(data.path);
        return publicUrl;
    }


    // --- Messaging --- (Giữ nguyên phần addMessageToChat, show/removeTypingIndicator)
    function addMessageToChat(message, sender, source = '', fileUrl = null) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        // ... (giống code cũ) ...
        p.textContent = message;
        // Nếu có fileUrl và là tin nhắn của người dùng, hiển thị ảnh/link
        if (fileUrl && sender === 'user') {
            const fileElement = document.createElement('div');
            fileElement.className = 'mt-2';
            if (message.toLowerCase().includes('ảnh') || /\.(jpeg|jpg|gif|png)$/i.test(fileUrl)) {
                const img = document.createElement('img');
                img.src = fileUrl;
                img.style.maxWidth = '200px';
                img.style.maxHeight = '200px';
                img.className = 'img-thumbnail';
                fileElement.appendChild(img);
            } else {
                const link = document.createElement('a');
                link.href = fileUrl;
                link.textContent = "Tệp đính kèm";
                link.target = "_blank";
                fileElement.appendChild(link);
            }
            messageDiv.appendChild(fileElement);
        }

        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }


    async function sendMessage() {
        if (!currentUser || !currentSessionId) {
            addMessageToChat("Vui lòng đăng nhập và chọn hoặc tạo một phiên chat.", 'bot', 'error');
            return;
        }

        const messageText = userInput.value.trim();
        const file = fileInput.files[0];

        if (messageText === '' && !file) return;

        addMessageToChat(messageText || (file ? `Đã gửi file: ${file.name}` : "Đang gửi..."), 'user', '', file ? URL.createObjectURL(file) : null); // Hiển thị tạm ảnh/file
        userInput.value = '';
        fileInput.value = ''; // Clear file input
        showTypingIndicator();

        let uploadedFileUrl = null;
        let fileMimeType = null;
        if (file) {
            uploadedFileUrl = await uploadFile(file);
            if (!uploadedFileUrl) {
                removeTypingIndicator();
                return; // Lỗi upload đã được hiển thị
            }
            fileMimeType = file.type;
        }

        try {
            const token = (await supabase.auth.getSession())?.data.session?.access_token;
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`, // Gửi JWT token
                },
                body: JSON.stringify({
                    message: messageText,
                    user_id: currentUser.id,
                    session_id: currentSessionId,
                    file_url: uploadedFileUrl,
                    file_mime_type: fileMimeType
                }),
            });
            // ... (phần xử lý response giống code cũ) ...
             removeTypingIndicator();

            if (!response.ok) {
                let errorMsg = `Lỗi: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMsg = errorData.error || errorMsg;
                } catch (e) { /* không làm gì */ }
                addMessageToChat(`Lỗi từ server: ${errorMsg}`, 'bot', 'error');
                return;
            }

            const data = await response.json();
            // Tin nhắn AI đã được lưu bởi Edge Function, không cần addMessageToChat ở đây nữa nếu dùng Realtime
            // addMessageToChat(data.reply, 'bot', data.source);

        } catch (error) {
            // ... (giống code cũ) ...
            removeTypingIndicator();
            console.error('Error sending message:', error);
            addMessageToChat('Không thể kết nối tới server. Vui lòng thử lại.', 'bot', 'error');
        }
    }

    // --- Realtime (Lắng nghe tin nhắn mới) ---
    function subscribeToNewMessages() {
        if (!currentSessionId) return null;

        return supabase
            .channel(`messages_session_${currentSessionId}`) // Channel duy nhất cho mỗi session
            .on('postgres_changes',
                { event: 'INSERT', schema: 'public', table: 'messages', filter: `session_id=eq.${currentSessionId}` },
                (payload) => {
                    const newMessage = payload.new;
                    // Chỉ thêm tin nhắn AI, vì tin nhắn user đã được thêm ngay khi gửi
                    if (newMessage.sender === 'ai' && newMessage.session_id === currentSessionId) {
                         // Xóa typing indicator nếu có, trước khi thêm tin nhắn mới
                        removeTypingIndicator();
                        addMessageToChat(newMessage.content, newMessage.sender, newMessage.source_ai, newMessage.file_url);
                    }
                }
            )
            .subscribe((status, err) => {
                if (status === 'SUBSCRIBED') {
                    console.log(`Subscribed to new messages for session ${currentSessionId}`);
                }
                if (status === 'CHANNEL_ERROR' || status === 'TIMED_OUT') {
                    console.error(`Subscription error for session ${currentSessionId}:`, err);
                    // Có thể thử subscribe lại sau một khoảng thời gian
                }
            });
    }

    let messageSubscription = null;
    // Override loadMessagesForSession để quản lý subscription
    async function loadMessagesForSession(sessionId) { // đã khai báo ở trên, đây là sửa đổi
        if (!currentUser) return;

        // Hủy subscription cũ nếu có
        if (messageSubscription) {
            supabase.removeChannel(messageSubscription);
            messageSubscription = null;
            console.log("Unsubscribed from old session messages.");
        }

        currentSessionId = sessionId;
        chatBox.innerHTML = '';

        sessionList.querySelectorAll('li').forEach(li => {
            li.classList.toggle('active', li.dataset.sessionId === sessionId);
        });

        const { data: messages, error } = await supabase
            .from('messages')
            .select('*')
            .eq('session_id', sessionId)
            .order('created_at', { ascending: true });

        if (error) {
            console.error("Error loading messages:", error);
            return;
        }
        messages.forEach(msg => addMessageToChat(msg.content, msg.sender, msg.source_ai, msg.file_url));

        // Bắt đầu subscription mới cho session này
        messageSubscription = subscribeToNewMessages();
    }


    // --- Init ---
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
    handleAuth(); // Kiểm tra trạng thái đăng nhập khi tải trang
    ```
3.  **`frontend/index.html` (Cập nhật):**
    *   Thêm `<input type="file" id="fileInput">`.
    *   Thêm các nút và UI cho Login/Logout (`<div id="authUi">`, `<button id="loginButton">`, `<button id="logoutButton">`).
    *   Thêm khu vực hiển thị danh sách session (`<ul id="sessionList" class="list-group"></ul>`) và nút tạo session mới (`<button id="newChatButton">`).
    *   Bố cục lại để có cột trái cho session, cột phải cho chat.

    ```html
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Webchat Hỗ trợ Bài tập (Supabase)</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <link rel="stylesheet" href="style.css">
    </head>
    <body>
        <div class="container-fluid mt-3">
            <div id="authUi" class="text-center" style="display: none;">
                <h3>Đăng nhập để bắt đầu</h3>
                <button id="loginButton" class="btn btn-primary"><i class="fab fa-google"></i> Đăng nhập với Google</button>
            </div>

            <div id="chatUi" class="row" style="display: none; height: 90vh;">
                <!-- Cột trái: Lịch sử chat và nút logout -->
                <div class="col-md-3 border-end d-flex flex-column p-2">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h5>Chat Sessions</h5>
                        <button id="newChatButton" class="btn btn-sm btn-success" title="New Chat">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                    <ul id="sessionList" class="list-group list-group-flush overflow-auto flex-grow-1">
                        <!-- Sessions will be loaded here -->
                    </ul>
                    <button id="logoutButton" class="btn btn-danger mt-auto">
                        <i class="fas fa-sign-out-alt"></i> Đăng xuất
                    </button>
                </div>

                <!-- Cột phải: Khung chat chính -->
                <div class="col-md-9 d-flex flex-column">
                    <div class="chat-container card flex-grow-1">
                        <div class="card-header bg-primary text-white">
                            <h4><i class="fas fa-brain"></i> AI Homework Helper</h4>
                        </div>
                        <div class="card-body chat-box" id="chatBox">
                            <!-- Tin nhắn sẽ được thêm vào đây -->
                        </div>
                        <div class="card-footer chat-input-area">
                            <div class="input-group">
                                <input type="file" id="fileInput" class="form-control" style="max-width: 50px;" title="Đính kèm file">
                                <input type="text" id="userInput" class="form-control" placeholder="Nhập câu hỏi của bạn..." aria-label="User input">
                                <button class="btn btn-primary" id="sendButton">
                                    <i class="fas fa-paper-plane"></i> Gửi
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
        <script src="script.js"></script>
    </body>
    </html>
    ```
4.  **`frontend/style.css` (Cập nhật/Thêm):**
    *   Style cho `sessionList`, `fileInput`.
    *   Đảm bảo layout 2 cột hoạt động tốt.
    ```css
    /* ... (các style cũ) ... */
    #chatUi {
        /* height: calc(100vh - 60px); /* Ví dụ */ */
    }

    #sessionList .list-group-item {
        cursor: pointer;
    }
    #sessionList .list-group-item.active {
        background-color: #0d6efd;
        color: white;
        border-color: #0d6efd;
    }

    .chat-container {
        display: flex;
        flex-direction: column;
        height: 100%; /* Để card-body và chat-box chiếm hết không gian */
    }

    .chat-box {
        flex-grow: 1; /* Để chat-box mở rộng */
        /* height đã có, bỏ để flex-grow hoạt động */
    }

    #fileInput {
        padding-top: 0.65rem; /* Căn chỉnh với input text */
    }
    ```

---

### Bước 6: Deployment

1.  **Supabase:**
    *   Push các thay đổi schema (nếu có): `supabase db push` (sau khi link project).
    *   Deploy Edge Functions:
        ```bash
        supabase functions deploy chat_handler --project-ref YOUR_PROJECT_ID --no-verify-jwt # Bỏ --no-verify-jwt cho production
        ```
    *   Thiết lập Environment Variables (`GEMINI_API_KEY`, `CHATTERBOT_FALLBACK_URL`) trên Supabase Dashboard.

2.  **Frontend:**
    *   Build (nếu dùng framework JS phức tạp) và deploy lên Vercel, Netlify, GitHub Pages, hoặc kéo thả vào Supabase Storage (tạo bucket riêng cho frontend).
    *   Đảm bảo `SUPABASE_URL` và `SUPABASE_ANON_KEY` trong `script.js` là của project Supabase đã deploy.
    *   Cấu hình CORS cho Edge Function trên Supabase Dashboard nếu cần (`Access-Control-Allow-Origin` trỏ đến domain frontend của bạn). Mặc định file `_shared/cors.ts` đã cho phép `*`.

3.  **ChatterBot Fallback (Nếu dùng):**
    *   Deploy thư mục `chatterbot_fallback` lên Railway như kế hoạch ban đầu.
    *   Lấy URL public và cập nhật biến `CHATTERBOT_FALLBACK_URL` trong Supabase.

---

### Bước 7: Các tính năng mới và cải thiện đã thêm

1.  **Upload File/Ảnh:**
    *   Người dùng có thể chọn file từ `input type="file"`.
    *   File được upload lên Supabase Storage.
    *   URL của file được gửi đến Edge Function, sau đó đến Gemini Vision API.
    *   Frontend hiển thị ảnh/link file đã upload.
2.  **Lịch sử Chat (Chat Sessions):**
    *   Mỗi cuộc hội thoại được lưu thành một `session` trong bảng `chat_sessions`.
    *   Tin nhắn thuộc về `session` đó, lưu trong bảng `messages`.
    *   Frontend hiển thị danh sách các `session` cũ, người dùng có thể chọn để xem lại.
    *   Nút "New Chat" để tạo session mới.
3.  **Xác thực Người dùng:**
    *   Sử dụng Supabase Auth (ví dụ: Google OAuth).
    *   Chỉ người dùng đã đăng nhập mới có thể chat và xem lịch sử của mình.
    *   RLS (Row Level Security) trên Supabase DB đảm bảo người dùng chỉ truy cập dữ liệu của họ.
4.  **Realtime Messages:**
    *   Sử dụng Supabase Realtime để tin nhắn mới (đặc biệt là từ AI) tự động xuất hiện trên các client đang mở session đó mà không cần refresh.

---

### Bước 8: Các Cải tiến Khác (Tiềm năng)

1.  **Streaming Phản hồi từ Gemini:** Gemini API hỗ trợ streaming. Cập nhật Edge Function và Frontend để hiển thị từng phần của câu trả lời AI thay vì chờ toàn bộ, cải thiện trải nghiệm người dùng.
2.  **Contextual Chat History cho Gemini:** Gửi một phần lịch sử chat gần đây trong session hiện tại cho Gemini để AI có ngữ cảnh tốt hơn.
3.  **Cải thiện UI/UX:**
    *   Thông báo rõ ràng hơn khi upload file, xử lý file.
    *   Cho phép đổi tên session.
    *   Tìm kiếm trong lịch sử chat.
4.  **Quản lý API Key và Secret an toàn hơn:**
    *   Sử dụng Supabase Secrets cho các key nhạy cảm.
    *   Đảm bảo RLS được cấu hình chặt chẽ.
5.  **Xử lý lỗi chi tiết hơn:** Cả ở frontend và backend.
6.  **Giới hạn số lượng file/kích thước file upload.**
7.  **Thay thế ChatterBot:** Nếu ChatterBot quá cồng kềnh, có thể xem xét:
    *   Sử dụng các mẫu câu trả lời đơn giản được lưu trong DB Supabase cho các câu hỏi thường gặp.
    *   Một hệ thống dựa trên từ khóa đơn giản hơn, viết bằng TypeScript trong Edge Function.

Kế hoạch này đã phức tạp hơn đáng kể, nhưng tích hợp Supabase mang lại một nền tảng mạnh mẽ và dễ mở rộng cho ứng dụng của bạn! Chúc bạn thành công!.