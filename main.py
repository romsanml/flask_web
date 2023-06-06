from flask import Flask, render_template, request
# import openai
from requests import ConnectionError, ReadTimeout, Timeout
# from openkey import api_key

# openai.api_key = api_key

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def main():
    input_dict = request.form.to_dict()
    try:
        input_text = input_dict['input_text']
    except KeyError:
        input_text = ''
        output_text = ''
        return render_template('index.html', input_message=input_text, message=output_text)
    try:
        # response = openai.Completion.create(
        #     model="text-davinci-003",
        #     prompt=input_text,
        #     temperature=0.7,
        #     max_tokens=2048,
        #     top_p=0.9,
        #     frequency_penalty=0.5,
        #     presence_penalty=0.5
        # )
        # output_text = response['choices'][0]['text']
        output_text = input_text

    except ConnectionError:
        output_text = 'Ошибка соединения. Попробуйте ещё раз.'

    except ReadTimeout:
        output_text = 'Длительное ожидание ответа. Попробуйте ещё раз.'

    except Timeout:
        output_text = 'Длительная обработка. Попробуйте ещё раз.'

    # except openai.error.OpenAIError:
    #     output_text = 'Сервер перегружен. Попробуйте повторить запрос позже.'

    return render_template('index.html', input_message=input_text, message=output_text)


if __name__ == '__main__':
    app.run(debug=False)
