# import thư viện
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Để cho phép FE gọi BE
from pydantic import BaseModel
import google.generativeai as genai
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer
from dotenv import load_dotenv

load_dotenv() # Tải biến môi trường từ file .env

#Cấu hình Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("GEMINI_API_KEY is not set in the environment variables.")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY) # Thiết lập API key cho Gemini
gemini_model = genai.GenerativeModel("gemini-2.0-flash") # Chọn mô hình Gemini

# Cấu hình ChatterBot
# Tạo một instance ChatBot mới
# storage_adapter: Chỉ định cách lưu trữ dữ liệu (ví dụ: SQL, JSON). Mặc định là JSONFileStorageAdapter.
# logic_adapters: Danh sách các bộ điều hợp logic mà bot sẽ sử dụng để chọn phản hồi.
#                 'chatterbot.logic.BestMatch' là một lựa chọn phổ biến.
#                 'chatterbot.logic.MathematicalEvaluation' cho phép tính toán cơ bản.
# preprocessors: Các bước tiền xử lý văn bản đầu vào.

chatbot = ChatBot(
    "HomeworkHelper",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    database_uri="sqlite:///database.sqlite3", # Đường dẫn đến cơ sở dữ liệu SQLite
    logic_adapters=[
        {
        "import_path":"chatterbot.logic.BestMatch", # Chọn phản hồi tốt nhất từ danh sách các phản hồi có 
        #"import_path":"chatterbot.logic.TimeLogicAdapter", # Cho phép bot trả lời các câu hỏi liên quan đến thời gian
        #"import_path":"chatterbot.logic.UnitConversion", # Cho phép bot chuyển đổi các đơn vị tốt nghiệp
        #"import_path":"chatterbot.logic.SpecificResponseAdapter", # Cho phép bot trả lời các câu hỏi tốt nghiệp
        #"import_path":"chatterbot.logic.MathematicalEvaluation", # Cho phép bot thực hiện các phép toán cơ bản
        "default_response": "Xin lỗi, tôi không hiểu câu hỏi của bạn.",
        "maximum_similarity_threshold": 0.90, # Ngưỡng tương đồng tối đa cho phản hồi
        },
        
        
    ],
    preprocessors=[
        'chatterbot.preprocessors.clean_whitespace'# Tiền xử lý văn bản đầu vào bằng cách loại bỏ khoảng trắng thừa
    ],


    read_only=True # Chỉ đọc dữ liệu từ cơ sở dữ liệu
  
)

# --- Huấn luyện ChatterBot (chỉ chạy một lần hoặc khi cần cập nhật) ---
# Bạn có thể tạo một script riêng để huấn luyện, hoặc bỏ phần này đi nếu chỉ dựa vào Gemini
# Kiểm tra xem database đã có dữ liệu chưa để tránh train lại mỗi lần khởi động
# Điều này đơn giản, trong thực tế có thể cần cơ chế phức tạp hơn

NEEDS_TRAINING = False # Mặc định là không cần train lại
DB_PATH = 'backend/db.sqlite3' # Hoặc đường dẫn tới file DB của bạn

if not os.path.exists("backend/db.sqlite3") or os.path.getsize("backend/db.sqlite3") < 10000:
    # Nếu file không tồn tại hoặc rỗng, cần train lại
    print("Đang huấn luyện lại ChatterBot...")
    trainer_corpus = ChatterBotCorpusTrainer(chatbot)
    trainer_corpus.train("chatterbot.corpus.english",
                         "chatterbot.corpus.english.conversations" # Huấn luyện với tập dữ liệu tiếng Anh
                        #"chatterbot.corpus.vietnamese",
                        #"chatterbot.corpus.vietnamese.conversations", # Huấn luyện với tập dữ liệu tiếng Việt
                        )

    custom_training_data = [
        # --- Higher Mathematics ---
        "What is the derivative of cos(x)?", "The derivative of cos(x) is -sin(x).",
        "Explain the concept of integration.", "Integration is the process of finding the area under a curve.",
        "What is a matrix?", "In mathematics, a matrix is a rectangular array or table of numbers, symbols, or expressions, arranged in rows and columns.",

        # --- Physics ---
        "What is the speed of light in a vacuum?", "The speed of light in a vacuum is approximately 299,792,458 meters per second.",
        "What is Ohm's law?", "Ohm's law states that the current through a conductor between two points is directly proportional to the voltage across the two points.",
        "Explain the concept of wave interference.", "Wave interference occurs when two or more waves overlap in space, resulting in a new wave pattern.",

        # --- Chemistry ---
        "What is a covalent bond?", "A covalent bond is a chemical bond that involves the sharing of electron pairs between atoms.",
        "What are acids and bases?", "Acids are substances that donate protons or accept electron pairs, while bases are substances that accept protons or donate electron pairs.",

        # --- Programming (Python) ---
        "What is a function in Python?", "In Python, a function is a block of organized, reusable code that performs a single, related action.",
        "Explain the difference between a list and a tuple in Python.", "A list is mutable (changeable), while a tuple is immutable (unchangeable).",

        # --- Economics ---
        "What is inflation?", "Inflation is the rate at which the general level of prices for goods and services is rising, and, consequently, the purchasing power of currency is falling.",
        "What is the role of a central bank?", "The primary role of a central bank is to manage a nation's currency and monetary policy.",

        # --- Philosophy ---
        "What is ethics?", "Ethics is a branch of philosophy that involves systematizing, defending, and recommending concepts of right and wrong conduct.",
        "What is metaphysics?", "Metaphysics is a branch of philosophy concerned with the fundamental nature of reality and being.",

        # --- Linguistics ---
        "What is phonetics?", "Phonetics is a branch of linguistics that focuses on the production and perception of speech sounds."
    ]   
    
    trainer_list = ListTrainer(chatbot) # Khoi tao ListTrainer
    trainer_list.train(custom_training_data) # Huấn luyện với dữ liệu tùy chỉnh
    print("Huấn luyện xong!")
else:
    print("Cơ sở dữ liệu đã có dữ liệu, không cần huấn luyện lại ChatterBot.")
# --- Kết thúc phần huấn luyện ChatterBot ---

# Tạo FastAPI app
app = FastAPI()

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Cho phép tất cả origins (thay đổi thành domain cụ thể khi deploy production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Định nghĩa model cho request body
class ChatRequest(BaseModel):
    message : str # Nội dung tin nhắn từ người dùng
    user_id : str = "default_user" # ID người dùng, có thể thay đổi theo yêu cầu, quản lý lịch sử chat

class ChatResponse(BaseModel):
    reply : str
    source : str # gemini hoặc chatterbot

# Định nghĩa route cho API
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    user_message = request.message
    
    # Kiểm tra xem message có rỗng không
    if user_message.strip() == "":
        raise HTTPException(status_code=400, detail="Message không được để trống.")
    # Gọi Gemini API
    default_response = "Xin lỗi, tôi không hiểu câu hỏi của bạn."
    try:
        if user_message != "":
            chatbot_response = chatbot.get_response(user_message)
            if chatbot_response.text != default_response:
                print(f"ChatterBot trả lời: {chatbot_response.text}")
                return ChatResponse(reply=chatbot_response.text, source="chatterbot")
            else:
                print("ChatterBot không trả lời được, chuyển sang Gemini.")
                raise Exception("ChatterBot không trả lời được.")
        else:
            print(f"ChatterBot gặp lỗi: {e}")
            raise Exception("ChatterBot không trả lời được.")

    except Exception as e:
        # Xây dựng prompt cho Gemini 
        prompt = f"""Bạn là một trợ lý AI thông minh và thân thiện, chuyên hỗ trợ giải đáp các câu hỏi liên quan 
        đến bài tập hoặc nghiên cứu cho học sinh. Hãy trả lời một cách dễ hiểu, rõ ràng và chính xác. 
        Nếu không biết hãy nói là bạn không biết. 
        Không bịa đặt thông tin.
        Câu hỏi của tôi là: {user_message}
        Câu trả lời của bạn: """

        gemini_response = gemini_model.generate_content(prompt)

        if gemini_response.text and len(gemini_response.text.strip()) > 10: # Kiểm tra độ dài phản hồi
            print(f"Gemini trả lời: {gemini_response.text}")
            return ChatResponse(reply=gemini_response.text, source="gemini")
        else:
            # Nếu Gemini không trả lời được, chuyển sang ChatterBot
            print("Gemini không trả lời được, chuyển sang ChatterBot.")
            raise Exception("Gemini không trả lời được.") # Chuyển sang ChatterBot
    except Exception as e:
        print(f"Gemini gặp lỗi: {e}")
        return ChatResponse(reply="Xin lỗi, tôi không thể trả lời câu hỏi này.", source="error")


# Chạy ứng dụng
@app.get("/")
async def root():
    return {"message": "Chào mừng bạn đến với API trợ lý học tập của chúng tôi!"}
# Chạy ứng dụng bằng uvicorn
# Nếu bạn muốn chạy ứng dụng, hãy sử dụng lệnh sau trong terminal:
# uvicorn main:app --reload

