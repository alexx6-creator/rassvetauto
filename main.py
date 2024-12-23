from flask import Flask, request, jsonify, send_from_directory
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json

app = Flask(__name__)

# Путь к файлу базы данных
DATABASE_FILE = 'users.json'

# Функция загрузки базы данных
def load_database():
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w') as file:
            json.dump({}, file)
    with open(DATABASE_FILE, 'r') as file:
        return json.load(file)

# Функция сохранения базы данных
def save_database(data):
    with open(DATABASE_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# Функция отправки email
def send_email(recipient, subject, body):
    sender_email = 'rassvetauto13@gmail.com'
    sender_password = 'zsel zgmj yldc egyx'

    if not sender_email or not sender_password:
        raise ValueError("MAIL_USERNAME и MAIL_PASSWORD должны быть установлены в переменных окружения.")
    # Создание сообщения
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject

    # Тело сообщения
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Установка соединения с SMTP-сервером
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
    except Exception as e:
        raise RuntimeError(f"Ошибка отправки email: {str(e)}")

@app.route('/index')
def mine():
    return send_from_directory('static', 'index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    if not username or not email:
        return jsonify({"error": "Пожалуйста, укажите имя пользователя и email."}), 400

    users = load_database()

    if email in users:
        return jsonify({"error": "Этот email уже зарегистрирован."}), 400

    # Сохраняем пользователя в базу данных
    users[email] = {"username": username, "confirmed": False}
    save_database(users)

    # Генерация подтверждающей ссылки
    confirm_url = f"http://127.0.0.1:5000/confirm?email={email}"

    # Отправка email
    try:
        subject = "Подтверждение регистрации"
        body = f"Здравствуйте, {username}!\n\nПожалуйста, подтвердите свою почту перейдя по ссылке: {confirm_url}"
        send_email(email, subject, body)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Регистрация успешна! Проверьте ваш email для подтверждения."}), 200

@app.route('/confirm', methods=['GET'])
def confirm_email():
    email = request.args.get('email')

    if not email:
        return jsonify({"error": "Отсутствует email."}), 400

    users = load_database()

    if email not in users:
        return jsonify({"error": "Неверный или отсутствующий email."}), 400

    users[email]['confirmed'] = True
    save_database(users)

    return jsonify({"message": f"Спасибо, {users[email]['username']}! Ваша почта подтверждена."}), 200

if __name__ == '__main__':
    app.run(host='192.168.79.236', port=5000, debug=True)
