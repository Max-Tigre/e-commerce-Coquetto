from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        data_nascimento = request.form['data_nascimento']
        idade = request.form['idade']

        try:
            # Primeiro, tenta converter a data para o formato esperado
            data_valida = datetime.strptime(data_nascimento, '%d/%m/%Y')
        except ValueError:
            try:
                # Se falhar, tenta o formato YYYY-MM-DD (comum em formulários HTML5)
                data_valida = datetime.strptime(data_nascimento, '%Y-%m-%d')
            except ValueError:
                # Caso nenhum dos formatos funcione, exibe a mensagem de erro
                flash("Data de nascimento inválida. Use o formato DD/MM/AAAA.")
                return redirect(url_for('cadastro'))

        # Se a data estiver correta, prossegue com o restante do código
        flash("Cadastro realizado com sucesso!")
        return redirect(url_for('cadastro'))

    return render_template("forms.html")

app.run(debug=True)
