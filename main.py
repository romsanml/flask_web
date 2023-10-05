from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import openai
from requests import ConnectionError, ReadTimeout, Timeout
from openkey import api_key, users_dict, secret_key

openai.api_key = api_key

app = Flask(__name__)
app.jinja_env.auto_reload = True
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = secret_key

login_manager = LoginManager(app)

users = users_dict


@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')


# Класс User, который реализует UserMixin
class User(UserMixin):
    def __init__(self, user_name):
        self.id = user_name


# Функция, которая загружает пользователя на основе его user_id
@login_manager.user_loader
def load_user(username):
    return User(username)


# Маршрут для обработки данных формы входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Проверка соответствия пары логин-пароль в хранилище пользователей
        if username in users and users[username] == password:
            # Успешный вход в личный кабинет
            user = User(username)
            login_user(user)
            flash('Вход выполнен успешно!', 'success')
            return redirect(url_for('dashboard'))
        else:
            # Неверная пара логин-пароль, перенаправлять на страницу входа
            flash('Неверные данные для входа!', 'error')
            return render_template('login.html')
    else:
        return render_template('login.html')


# Маршрут для отображения личного кабинета
@app.route('/dashboard', methods=['POST', 'GET'])
@login_required
def dashboard():
    input_dict = request.form.to_dict()
    try:
        prompt_text = input_dict['prompt_text']
        input_text = input_dict['input_text']
    except KeyError:
        prompt_text = ''
        input_text = ''
        output_text = ''
        return render_template('dashboard.html', prompt=prompt_text, input_message=input_text, message=output_text)
    try:
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo-16k',
            messages=[
                {"role": "system", "content": prompt_text},
                {"role": "user", "content": input_text}
            ],
            temperature=1.0,
            max_tokens=8000,
            top_p=0.9,
            frequency_penalty=0.5,
            presence_penalty=0.5
        )
        output_text = response['choices'][0]['message']['content']
        # output_text = input_text

    except ConnectionError:
        output_text = 'Ошибка соединения. Попробуйте ещё раз.'

    except ReadTimeout:
        output_text = 'Длительное ожидание ответа. Попробуйте ещё раз.'

    except Timeout:
        output_text = 'Длительная обработка. Попробуйте ещё раз.'

    except openai.error.OpenAIError:
        output_text = 'Сервер перегружен. Попробуйте повторить запрос позже.'

    return render_template('dashboard.html', prompt=prompt_text, input_message=input_text, message=output_text)


# Маршрут для выхода
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли!', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
