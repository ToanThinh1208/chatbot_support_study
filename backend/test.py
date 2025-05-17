from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

trainer.train(custom_training_data)  # Sử dụng dữ liệu bạn đã cung cấp
response = chatbot.get_response("What is the derivative of cos(x)?")
print(response.text if response else "No response")