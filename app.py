from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Cliente, Produto
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import os  

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clientes.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'sua_chave_secreta'

app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        data_nascimento_str = request.form['data_nascimento']
        
        data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
        hoje = date.today()
        idade = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))

        if idade < 18:
            flash('Idade mínima para cadastro é 18 anos.', 'error') 
            return render_template('create.html') 

        novo_cliente = Cliente(
            nome=nome, 
            email=email, 
            senha=generate_password_hash(senha), 
            data_nascimento=data_nascimento
        )
        db.session.add(novo_cliente)
        db.session.commit()
        return redirect(url_for('index')) 
    
    return render_template('create.html')

@app.route('/produtos', methods=['GET', 'POST'])
def produtos():
    if request.method == 'POST':
        nome = request.form['nome']
        preco = float(request.form['preco'])
        descricao = request.form['descricao']
        quantidade = int(request.form['quantidade_estoque'])
        imagem = request.form['imagem']  

        if len(nome) < 3:
            flash('O nome deve ter pelo menos 3 caracteres.', 'error')
        elif preco <= 0:
            flash('O preço deve ser maior que 0.', 'error')
        elif quantidade < 0:
            flash('A quantidade deve ser um número inteiro maior ou igual a 0.', 'error')
        else:
            novo_produto = Produto(
                nome=nome,
                preco=preco,
                descricao=descricao,
                quantidade_estoque=quantidade,
                imagem=imagem
            )
            db.session.add(novo_produto)
            db.session.commit()
            return redirect(url_for('produtos'))

    produtos = Produto.query.all()
    return render_template('produtos.html', produtos=produtos)

@app.route('/produtos/create', methods=['GET', 'POST'])
def create_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        preco = float(request.form['preco'])
        descricao = request.form['descricao']
        quantidade_estoque = int(request.form['quantidade_estoque'])
        imagem = request.form['imagem']

        novo_produto = Produto(
            nome=nome, 
            preco=preco, 
            descricao=descricao, 
            quantidade_estoque=quantidade_estoque,
            imagem=imagem
        )
        db.session.add(novo_produto)
        db.session.commit()
        return redirect(url_for('produtos')) 

    return render_template('create_produto.html') 

@app.route('/produtos/edit/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    produto = Produto.query.get(id)
    if request.method == 'POST':
        produto.nome = request.form['nome']
        produto.preco = float(request.form['preco'])
        produto.descricao = request.form['descricao']
        produto.quantidade_estoque = int(request.form['quantidade_estoque'])
        produto.imagem = request.form['imagem']
        db.session.commit()
        return redirect(url_for('produtos'))
    return render_template('edit_produto.html', produto=produto)

@app.route('/produtos/delete/<int:id>')
def deletar_produto(id):
    produto = Produto.query.get(id)
    db.session.delete(produto)
    db.session.commit()
    return redirect(url_for('produtos'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email and password:
            cliente = Cliente.query.filter_by(email=email).first()
            if cliente and check_password_hash(cliente.senha, password):
                return redirect(url_for('loja'))
            else:
                error_message = "Email ou senha incorretos."
        else:
            error_message = "Faltam dados no formulário."

    return render_template('login.html', error_message=error_message)

@app.route('/loja')
def loja():
    produtos = Produto.query.all()  
    return render_template('loja.html', produtos=produtos)  

@app.route('/clientes')
def index():
    clientes = Cliente.query.all() 
    return render_template('index.html', clientes=clientes)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    cliente = Cliente.query.get(id)
    if request.method == 'POST':
        cliente.nome = request.form['nome']
        cliente.email = request.form['email']
        cliente.data_nascimento = request.form['data_nascimento']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', cliente=cliente)

@app.route('/delete/<int:id>')
def delete(id):
    cliente = Cliente.query.get(id)
    db.session.delete(cliente)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/comprar/<int:id>', methods=['GET', 'POST'])
def comprar_produto(id):
    produto = Produto.query.get_or_404(id)  
    if request.method == 'POST':
        quantidade_comprada = int(request.form['quantidade'])  

        if quantidade_comprada <= produto.quantidade_estoque:
            produto.quantidade_estoque -= quantidade_comprada  
            db.session.commit() 
            flash('Compra realizada com sucesso!', 'success')
            return redirect(url_for('loja'))
        else:
            flash('Quantidade insuficiente em estoque.', 'error')

    return render_template('comprar_produto.html', produto=produto)

if __name__ == '__main__':
    app.run(debug=True)
