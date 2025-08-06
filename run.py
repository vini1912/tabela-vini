from flask import Flask, redirect, render_template, request
import os
import sqlite3 

app = Flask(__name__)

UPLOAD = 'static/assets'
app.config['UPLOAD'] = UPLOAD

app.config['dados_login'] = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():    
    usuario = request.form['usuario']
    senha = request.form['senha']

    conexao = sqlite3.connect('models/agenda.db')
    cursor = conexao.cursor()

    sql = "SELECT * from tb_login WHERE usuario=? AND senha=?"
    cursor.execute(sql, (usuario, senha))

    login_usuario = cursor.fetchone()

    if login_usuario:
        app.config['dados_login'] = login_usuario
        return redirect('/cadastro')
    
    return redirect('/')

@app.route('/logout')
def logout():
    app.config['dados_login'] = []
    return redirect('/')
    
@app.route("/cadastro")
def cadastro():
    if not app.config['dados_login']:
        return redirect('/')

    return render_template("cadastro.html", usuario=app.config['dados_login'])

@app.route('/enviar', methods=['POST'])
def enviar():
    nome = request.form['nome']
    email = request.form['email']
    telefone = request.form['telefone']

    conexao = sqlite3.connect('models/agenda.db')
    cursor = conexao.cursor()

    imagem = request.files['imagem']
    nome_imagem = None
    if imagem:
        extensao = imagem.filename.split('.')[-1]
        nome_imagem = f"{nome.strip().lower().replace(' ', '_')}.{extensao}"
        caminho_imagem = os.path.join(app.config['UPLOAD'], nome_imagem)
        imagem.save(caminho_imagem)

    with sqlite3.connect('models/agenda.db') as conexao:
        cursor = conexao.cursor()

    sql = 'INSERT INTO tb_pessoas (nome, email, telefone, imagem) VALUES (?, ?, ?, ?)'
    cursor.execute(sql, (nome, email, telefone, nome_imagem))

    conexao.commit()
    conexao.close

    return redirect('/cadastro')

@app.route('/consulta')
def consulta():
    if not app.config['dados_login']:
        return redirect('/')
    
    conexao = sqlite3.connect('models/agenda.db')
    cursor = conexao.cursor()

    sql = 'SELECT * FROM tb_pessoas'
    cursor.execute(sql)
    pessoas = cursor.fetchall()

    conexao.close()

    return render_template('consulta.html', pessoas=pessoas, usuario=app.config['dados_login'])

@app.route('/excluir/<int:id>', methods=['GET'])
def excluir(id):
    conexao = sqlite3.connect('models/agenda.db')
    cursor = conexao.cursor()

    sql = 'DELETE FROM tb_pessoas WHERE pessoas_id = ?'
    cursor.execute(sql, (id,))

    conexao.commit()
    conexao.close()

    return redirect('/consulta')

@app.route('/ver/<int:id>', methods=['GET', 'POST'])
def ver(id):
    conexao = sqlite3.connect('models/agenda.db')
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM tb_pessoas WHERE pessoas_id = ?", (id,))
    pessoa = cursor.fetchone()
    conexao.close()
    return render_template('ver.html', pessoa=pessoa)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conexao = sqlite3.connect('models/agenda.db')
    cursor = conexao.cursor()
 
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
 
        sql = "UPDATE tb_pessoas SET nome = ?, email = ?, telefone = ? WHERE pessoas_id = ?"
        cursor.execute(sql, (nome, email, telefone, id))
 
        conexao.commit()
        conexao.close()
 
        return redirect('/consulta')
 
    else:
        cursor.execute("SELECT * FROM tb_pessoas WHERE pessoas_id = ?", (id,))
        pessoa = cursor.fetchone()
        conexao.close()
 
        return render_template('editar.html', pessoa=pessoa)


if __name__ == '__main__':
    app.run(host= '0.0.0.0', port=80, debug=True)