from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

def calcIdade(s):
    dataAtual = datetime.now()
    ano = dataAtual.year
    mes = dataAtual.month
    dia = dataAtual.day
    diaAluno = int(s[8::])
    mesAluno = int(s[5:7])
    anoAluno = int(s[0:4])
    if mesAluno < mes:
        idade = ano - anoAluno
        return(idade)
    elif mesAluno > mes:
        idade = ano - anoAluno - 1
        return(idade)
    else:
        if diaAluno <= dia:
            idade = ano - anoAluno
            return(idade)
        else:
            idade = ano - anoAluno - 1
            return(idade)

app = Flask(__name__)
app.secret_key = 'SECRET_KEY'

user = False
admin = False
sucesso = False

#pagina de login
@app.route("/")
@app.route("/login")
def mostrarLogin():
    #4 linhas abaixo tiram da sessão informações do formulário de cadastro caso tenham.
    # Isso é feito aqui pois da pg de cadastro para qualquer outra página é necessário passar pela pg de login 
    session.pop("apelidoC",None)
    session.pop('usuario', None)
    session.pop('senha',None)
    session.pop('confirma',None)
    #voltando sucesso para False caso precise, pois cadastro foi realizado com sucesso
    global sucesso
    sucesso = False
    # Caso já tenha alguem logado (adm ou user), deve se redirecionar para a página correta (adm ou inicio)
    if admin:
        return(redirect("/adm"))
    elif user:
        return redirect("/inicio")
    else:
        return render_template("login.html")
@app.route("/login",methods=["POST"])
def logar():
    #pegando dados do formulario
    usuario = request.form.get("usuario")
    senha = request.form.get("senha")
    conexao = sqlite3.connect('sistemaAcademia.db')
    cursor = conexao.cursor()
    #verificando dados
    cursor.execute("SELECT usuario FROM clientes WHERE usuario=?",(usuario,))
    testeUsuario = cursor.fetchone()
    #usuario não encontrado na tabela de clientes
    if testeUsuario == None:
        #antes de retornar erro verificamos se o usuario é um adm
        cursor.execute("SELECT usuario FROM admin WHERE usuario=?",(usuario,))
        testeUsuario = cursor.fetchone()
        #usuario não encontrado denovo
        if testeUsuario == None:
            conexao.close()
            erro = "Usuário ou senha incorretos."
            return render_template("login.html",erro=erro)
        #usuario era adm
        else:
            cursor.execute("SELECT senha FROM admin WHERE usuario=?",(usuario,))
            testeSenha = cursor.fetchone()
            #Senha correta
            if testeSenha[0] == senha:
                #colocando usuario adm na sessão para saber quem logou
                cursor.execute("SELECT usuario FROM admin WHERE usuario=?",(usuario,))
                cpfLogado = cursor.fetchone()[0]
                session['logado'] = cpfLogado
                conexao.close()
                #redirecionando para página de adm
                global admin
                admin = True
                return redirect("/adm")
            #Senha incorreta
            else:
                erro = "Usuário ou senha incorretos."
                conexao.close()
                return render_template("login.html",erro=erro)
    #usuario encontrado na tabela de clientes
    else:
        cursor.execute("SELECT senha FROM clientes WHERE usuario=?",(usuario,))
        testeSenha = cursor.fetchone()
        #Senha correta
        if testeSenha[0] == senha:
            #colocando cpf do usuario na sessão para saber quem logou
            cursor.execute("SELECT usuario FROM clientes WHERE usuario=?",(usuario,))
            cpfLogado = cursor.fetchone()[0]
            session['logado'] = cpfLogado
            conexao.close()
            #redirecionando para página de user
            global user
            user = True
            return redirect("/inicio")
        #Senha incorreta
        else:
            erro = "Usuário ou senha incorretos."
            conexao.close()
            return render_template("login.html",erro=erro)

#pagina de cadastro
@app.route("/cadastro")
def mostrarCadastro():
    # Caso tenha alguém logado(user o adm), deve se redirecionar para a página correta (adm ou inicio)
    if admin:
        return(redirect("/adm"))
    elif user:
        return redirect("/inicio")
    else:
        return render_template("cadastro.html")  
@app.route("/cadastro",methods=["POST","GET"])
def cadastrar():
    #pegando dados do formulario
    apelido = request.form.get("apelido")
    usuario = request.form.get("usuario")
    senha = request.form.get("senha")
    confirma = request.form.get("confirmaSenha")
    #colocando dados coletados na sessão para apos algum erro dados não sumirem dos campos preenchidos
    session['apelidoC'] = apelido
    session['usuario'] = usuario
    session['senha'] = senha
    session['confirma'] = confirma
    #Registrando novos clientes
    conexao = sqlite3.connect('sistemaAcademia.db')
    cursor = conexao.cursor()
    #Verificando requisitos de cadastro:
    #conferindo se cpf foi já foi cadastrado
    cursor.execute("SELECT usuario FROM clientes WHERE usuario=?",(usuario,))
    testeCPF = cursor.fetchone()
    if testeCPF == None:
        erro = "CPF não matriculado."
        conexao.close()
        return render_template("cadastro.html",erro=erro)
    else:
        #conferindo cardinalidades
        if len(apelido) >= 2 and len(senha) >= 6 and confirma == senha:
            #conferindo se cpf já possui uma conta
            cursor.execute("SELECT senha FROM clientes WHERE usuario=?",(usuario,))
            testeSenha = cursor.fetchone()
            #cpf não possuia conta
            if testeSenha[0] == "semconta":
                cursor.execute("UPDATE clientes SET apelido=?,senha=? WHERE usuario=? ",(apelido,senha,usuario,))
                #True sendo atribuido a sucesso para exibir página de sucesso
                global sucesso
                sucesso = True
                conexao.commit()
                conexao.close()
                return redirect('/sucesso')
            else:
                #cpf possuia conta
                erro = "Este CPF já possui uma conta."
                conexao.close()
                return render_template("cadastro.html",erro=erro)  
        else:
            #erro de cardinalidades
            erro = "Preencha os campos corretamente."
            conexao.close()
            return render_template("cadastro.html",erro=erro)

#página de sucesso de cadastro
@app.route("/sucesso")
#somente se sucesso for True será exibida página de sucesso
def sucesso():
    if sucesso:
        return render_template("sucesso.html")
    else:
        # se não, tem os 3 casos. Página de inicio, adm ou login
        if user:
            return redirect("/inicio")
        elif admin:
            return redirect("/adm")
        else:
            return redirect("/login")

#pagina de inicio do aluno
@app.route("/inicio")
def inicio():
    #Se o usuario tiver logado com sucesso
    if user:
        cpfLogado = session['logado']
        conexao = sqlite3.connect('sistemaAcademia.db')
        cursor = conexao.cursor()
        cursor.execute("SELECT apelido FROM clientes WHERE usuario=?",(cpfLogado,))
        apelido = cursor.fetchone()[0]
        conexao.close()
        return render_template("inicio.html",nome=apelido)
    # se não redirecionar para ou login ou adm
    elif admin:
        return redirect("/adm")
    else:
        return redirect("/login")
    
#página de turmas do aluno
@app.route("/inicio/turmas")
def alunoTurmas():
    #Se o usuario tiver logado
    if user:
        #pegando informções das turmas do aluno
        cpfLogado = session['logado']
        conexao = sqlite3.connect('sistemaAcademia.db')
        cursor = conexao.cursor()
        cursor.execute("SELECT turma FROM turmasxalunos WHERE aluno=?",(cpfLogado,))
        turmasDoAluno = cursor.fetchall()
        turmas = []
        for i in turmasDoAluno:
            cursor.execute("SELECT * FROM turmas WHERE id=?",(i[0],))
            turma = cursor.fetchone()
            turmas.append(turma)
        conexao.close()
        return render_template("alunoTurmas.html",turmas=turmas)
    # se não redirecionar para ou login ou adm
    elif admin:
        return redirect("/adm")
    else:
        return redirect("/login")

#página de entrar em turma do aluno
@app.route("/inicio/turmas/entrar")
def turmasEntrar():
    #Se o usuario tiver logado
    if user:
        #mandando informação das turmas existente para a página
        conexao = sqlite3.connect('sistemaAcademia.db')
        cursor = conexao.cursor()
        cursor.execute("SELECT id FROM turmas")
        turmasID = cursor.fetchall()
        cursor.execute("SELECT * FROM turmas")
        turmas = cursor.fetchall()
        conexao.close()
        return render_template("entrarTurmas.html",turmas=turmas,turmasID=turmasID)
    # se não redirecionar para ou login ou adm
    elif admin:
        return redirect("/adm")
    else:
        return redirect("/login")
@app.route("/inicio/turmas/entrar",methods=['POST'])
def entrarTurmas():
    turma = request.form.get("turma")
    cpfLogado = session['logado']
    #pegando informações das turmas do aluno e em geral para mandar para a página
    conexao = sqlite3.connect('sistemaAcademia.db')
    cursor = conexao.cursor()
    cursor.execute("SELECT id FROM turmas")
    turmasID = cursor.fetchall()
    cursor.execute("SELECT * FROM turmas")
    turmas = cursor.fetchall()
    #entrando na turma
    #pegando turmas que o aluno faz parte para verificar
    cursor.execute("SELECT turma FROM turmasxalunos WHERE aluno=?",(cpfLogado,))
    turmasDoAluno = cursor.fetchall()
    for i in turmasDoAluno:
        if turma == i[0]:
            erro = "Você já está matriculado nessa turma"
            conexao.close()
            return(render_template("entrarTurmas.html",erro=erro,turmasID=turmasID,turmas=turmas))
    #entrando de fato
    cursor.execute("INSERT INTO turmasxalunos (turma,aluno) VALUES (?,?)",(turma,cpfLogado))
    conexao.commit()
    conexao.close()
    mensagem = "Entrou na turma com sucesso"
    return(render_template("entrarTurmas.html",mensagem=mensagem,turmasID=turmasID,turmas=turmas))

#Página de sair de turma do aluno
@app.route("/inicio/turmas/sair")
def turmasSair():
    #Se o usuario tiver logado
    if user:
        #mandando id das turmas que o aluno faz parte para a página
        cpfLogado = session['logado']
        conexao = sqlite3.connect('sistemaAcademia.db')
        cursor = conexao.cursor()
        cursor.execute("SELECT turma FROM turmasxalunos WHERE aluno=?",(cpfLogado,))
        turmas = cursor.fetchall()
        conexao.close()
        return render_template("sairTurma.html",turmas=turmas)
    # se não redirecionar para ou login ou adm
    elif admin:
        return redirect("/adm")
    else:
        return redirect("/login")
@app.route("/inicio/turmas/sair",methods=['POST'])
def sairTurma():
    turma = request.form.get("turma")
    cpfLogado = session['logado']
    conexao = sqlite3.connect('sistemaAcademia.db')
    cursor = conexao.cursor()
    #saindo da turma
    cursor.execute("DELETE FROM turmasxalunos WHERE turma=? AND aluno=?",(turma,cpfLogado,))
    #pegando lista de turmas do aluno
    cursor.execute("SELECT turma FROM turmasxalunos WHERE aluno=?",(cpfLogado,))
    turmas = cursor.fetchall()
    conexao.commit()
    conexao.close()
    mensagem = "Saiu da turma com sucesso"
    return(render_template("sairTurma.html",mensagem=mensagem,turmas=turmas))

#pagina de gerenciamento da conta do aluno
@app.route("/inicio/conta")
def conta():
    #Se o usuario tiver logado
    if user:
        return render_template("conta.html")
    # se não redirecionar para ou login ou adm
    elif admin:
        return redirect("/adm")
    else:
        return redirect("/login")

#pagina de mudar senha do aluno
@app.route("/inicio/conta/mudarSenha")
def mostrarTrocaSenha():
    #Se o usuario tiver logado com sucesso
    if user:
        return render_template("mudarSenha.html")
    # se não redirecionar para ou login ou adm
    elif admin:
        return redirect("/adm")
    else:
        return redirect("/login")
@app.route("/inicio/conta/mudarSenha",methods=['POST'])
def mudarSenha():
    cpf = request.form.get("usuario")
    senhaAntiga = request.form.get("senhaAntiga")
    senhaNova = request.form.get("senhaNova")
    confirma = request.form.get("confirmaSenha")
    conexao = sqlite3.connect('sistemaAcademia.db')
    cursor = conexao.cursor()
    #verificando dados
    cursor.execute("SELECT usuario FROM clientes WHERE usuario=?",(cpf,))
    testeUsuario = cursor.fetchone()
    #usuario/cpf não encontrado
    if testeUsuario == None:
        conexao.close()
        erro = "Usuário ou senha antiga incorretos."
        return render_template("mudarSenha.html",erro=erro)
    #usuario encontrado
    else:
        cursor.execute("SELECT senha FROM clientes WHERE usuario=?",(cpf,))
        testeSenha = cursor.fetchone()
        #Senha antiga correta
        if testeSenha[0] == senhaAntiga:
            #testando cardinalidade da nova senha
            if len(senhaNova) >= 6 and confirma == senhaNova:
                #tudo certo
                cursor.execute("UPDATE clientes SET senha=? WHERE usuario=? ",(senhaNova,cpf,))
                conexao.commit()
                conexao.close()
                mensagem = "Senha alterada com sucesso"
                return render_template("mudarSenha.html",mensagem=mensagem)
            #erro de cardinalidade
            else:
                erro = "Preencha os campos corretamente."
                conexao.close()
                return render_template("mudarSenha.html",erro=erro)
        #Senha antiga incorreta
        else:
            erro = "Usuário ou senha antiga incorretos."
            conexao.close()
            return render_template("mudarSenha.html",erro=erro)

#pagina de mudar apelido do aluno
@app.route("/inicio/conta/mudarApelido")
def mostrarTrocaApelido():
    #Se o usuario tiver logado com sucesso
    if user:
        return render_template("mudarApelido.html")
    # se não redirecionar para ou login ou adm
    elif admin:
        return redirect("/adm")
    else:
        return redirect("/login")
@app.route("/inicio/conta/mudarApelido",methods=['POST'])
def mudarApelido():
    cpf = request.form.get("usuario")
    novoApelido = request.form.get("novoApelido")
    senha= request.form.get("senha")
    conexao = sqlite3.connect('sistemaAcademia.db')
    cursor = conexao.cursor()
    #verificando dados
    cursor.execute("SELECT usuario FROM clientes WHERE usuario=?",(cpf,))
    testeUsuario = cursor.fetchone()
    #usuario/cpf não encontrado
    if testeUsuario == None:
        conexao.close()
        erro = "Usuário ou senha incorretos."
        return render_template("mudarApelido.html",erro=erro)
    #usuario encontrado
    else:
        cursor.execute("SELECT senha FROM clientes WHERE usuario=?",(cpf,))
        testeSenha = cursor.fetchone()
        #Senha correta
        if testeSenha[0] == senha:
            #tudo certo
            cursor.execute("UPDATE clientes SET apelido=? WHERE usuario=? ",(novoApelido,cpf,))
            conexao.commit()
            conexao.close()
            mensagem = "Apelido alterado com sucesso"
            return render_template("mudarApelido.html",mensagem=mensagem)
        #Senha incorreta
        else:
            erro = "Usuário ou senha incorretos."
            conexao.close()
            return render_template("mudarApelido.html",erro=erro)

#log out
@app.route("/sair")
def sair():
    #sai tanto da página de usuário como de administrador
    global admin
    admin = False
    global user
    user = False
    return redirect("/login")

#página do administrador
@app.route("/adm")
def adm():
    # se o adm estiver logado
    if admin:
        cpfLogado = session['logado']
        conexao = sqlite3.connect('sistemaAcademia.db')
        cursor = conexao.cursor()
        cursor.execute("SELECT apelido FROM admin WHERE usuario=?",(cpfLogado,))
        apelido = cursor.fetchone()[0]
        conexao.close()
        return render_template("adm.html",nome=apelido)
    # se não redirecionar para inicio ou login
    elif user:
        return(redirect("/inicio"))
    else:
        return redirect("/login")
    
#página de gerenciameno de alunos
@app.route("/adm/alunos")
def mostrarAlunos():
    # se adm tiver logado, acesso é permitido
    if admin:
        conexao = sqlite3.connect('sistemaAcademia.db')
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM clientes")
        clientes = cursor.fetchall()
        conexao.close()
        return render_template("admAlunos.html",clientes=clientes)
    #se não redirecionar para login ou inicio
    elif user:
        return redirect("/inicio")
    else:
        return redirect("/login")

#página gerenciamento das salas
@app.route("/adm/salas")
def mostrarSalas():
    # se adm tiver logado, acesso é permitido
    if admin:
        conexao = sqlite3.connect('sistemaAcademia.db')
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM salas")
        salas = cursor.fetchall()
        conexao.close()
        return render_template("admSalas.html",salas=salas)
    #se não redirecionar para login ou inicio
    elif user:
        return redirect("/inicio")
    else:
        return redirect("/login")

#página de gerenciamento das modalidades
@app.route("/adm/modalidades")
def mostrarModalidades():
    # se adm tiver logado, acesso é permitido
    if admin:
        conexao = sqlite3.connect('sistemaAcademia.db')
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM modalidades")
        modalidades = cursor.fetchall()
        conexao.close()
        return render_template("admModalidades.html",modalidades=modalidades)
    #se não redirecionar para login ou inicio
    elif user:
        return redirect("/inicio")
    else:
        return redirect("/login")

#página de gerenciamento das turmas
@app.route("/adm/turmas")
def mostrarTurmas():
    # se adm tiver logado, acesso é permitido
    if admin:
        conexao = sqlite3.connect('sistemaAcademia.db')
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM turmas")
        turmas = cursor.fetchall()
        conexao.close()
        return render_template("admTurmas.html",turmas=turmas)
    #se não redirecionar para login ou inicio
    elif user:
        return redirect("/inicio")
    else:
        return redirect("/login")

#página de matricula de novos alunos
@app.route("/adm/alunos/matricula")
def mostrarMatricula():
    # se adm tiver logado, acesso é permitido
    if admin:
        return render_template("matricula.html")
    #se não redirecionar para login ou inicio
    elif user:
        return redirect("/inicio")
    else:
        return redirect("/login")
@app.route("/adm/alunos/matricula", methods=['POST'])
def matricular():
    #pegando dados do formulario
    usuario = request.form.get("usuario")
    nome = request.form.get("nome")
    sexo = request.form.get("sexo")
    nascimento = request.form.get("nascimento")
    #Registrando novos clientes
    conexao = sqlite3.connect('sistemaAcademia.db')
    cursor = conexao.cursor()
    #Verificando requisitos para matricular:
    #conferindo se usuario já existe
    cursor.execute("SELECT usuario FROM clientes WHERE usuario=?",(usuario,))
    teste = cursor.fetchone()
    #usuario não existe
    if teste == None:
        novoUsuario = (usuario,nome,"semconta",sexo,nascimento)
        cursor.execute("INSERT INTO clientes (usuario,nome,senha,sexo,nascimento) VALUES (?,?,?,?,?)",novoUsuario)
        conexao.commit()
        conexao.close()
        mensagem = "Aluno matriculado com sucesso!"
        return render_template("matricula.html",mensagem=mensagem)
    #usuario já existe
    else:
        erro = "usuario já está matriculado"
        conexao.close()
        return render_template("matricula.html",erro=erro)

#página de registro de salas
@app.route("/adm/salas/registrar")
def mostrarRegistroSalas():
    # se adm tiver logado, acesso é permitido
    if admin:
        return render_template("registroSalas.html")
    #se não redirecionar para login ou inicio
    elif user:
        return redirect("/inicio")
    else:
        return redirect("/login")
@app.route("/adm/salas/registrar", methods=['POST'])
def registrarSala():
    #pegando dados do formulario
    sala = request.form.get("sala")
    #Registrando nova sala
    conexao = sqlite3.connect('sistemaAcademia.db')
    cursor = conexao.cursor()
    #verificando se sala já está registrada
    cursor.execute("SELECT sala FROM salas WHERE sala=?",(sala,))
    teste = cursor.fetchone()
    #sala não está registrada
    if teste == None:
        cursor.execute("INSERT INTO salas (sala) VALUES (?)",(sala,))
        conexao.commit()
        conexao.close()
        mensagem = "Sala registrada com sucesso!"
        return render_template("registroSalas.html",mensagem=mensagem)
    #sala já está registrada
    else:
        erro = "Essa sala já foi registrada"
        conexao.close()
        return render_template("registroSalas.html",erro=erro)

#página de registro de modalidades
@app.route("/adm/modalidades/registrar")
def mostrarRegistroModalidades():
    # se adm tiver logado, acesso é permitido
    if admin:
        return render_template("registroModalidades.html")
    #se não redirecionar para login ou inicio
    elif user:
        return redirect("/inicio")
    else:
        return redirect("/login")
@app.route("/adm/modalidades/registrar", methods=['POST'])
def registrarModalidade():
    #pegando dados do formulario
    modalidade = request.form.get("modalidade")
    #Registrando nova sala
    conexao = sqlite3.connect('sistemaAcademia.db')
    cursor = conexao.cursor()
    #verificando se sala já está registrada
    cursor.execute("SELECT modalidade FROM modalidades WHERE modalidade=?",(modalidade,))
    teste = cursor.fetchone()
    #modalidade não está registrada
    if teste == None:
        cursor.execute("INSERT INTO modalidades (modalidade) VALUES (?)",(modalidade,))
        conexao.commit()
        conexao.close()
        mensagem = "Modalidade registrada com sucesso!"
        return render_template("registroModalidades.html",mensagem=mensagem)
    #modalidade já está registrada
    else:
        erro = "Essa modalidade já foi registrada"
        conexao.close()
        return render_template("registroModalidades.html",erro=erro)
    
#página de registro de turmas
@app.route("/adm/turmas/registrar")
def mostrarRegistroTurmas():
    # se adm tiver logado, acesso é permitido
    if admin:
        #mandando para a página as informações de modalidades e salas do banco de dados
        conexao = sqlite3.connect('sistemaAcademia.db')
        cursor = conexao.cursor() 
        cursor.execute("SELECT modalidade FROM modalidades")
        modalidades = cursor.fetchall()
        cursor.execute("SELECT sala FROM salas")
        salas = cursor.fetchall()
        conexao.close()
        return render_template("registroTurmas.html",modalidades=modalidades,salas=salas)
    #se não redirecionar para login ou inicio
    elif user:
        return redirect("/inicio")
    else:
        return redirect("/login")
@app.route("/adm/turmas/registrar", methods=['POST'])
def registrarTurmas():
    #pegando dados do formulario
    modalidade = request.form.get("modalidade")
    horaInicial = request.form.get("horaInicial")
    horaFinal = request.form.get("horaFinal")
    sala = request.form.get("sala")
    #Registrando nova sala
    conexao = sqlite3.connect('sistemaAcademia.db')
    cursor = conexao.cursor()
    #verificando se turma já existe
    cursor.execute("SELECT * FROM turmas WHERE modalidade=? AND horarioInicial=? AND horarioFinal=? AND sala=?",(modalidade,horaInicial,horaFinal,sala))
    teste = cursor.fetchone()
    #Turma não existe
    if teste == None:
        cursor.execute("INSERT INTO turmas (modalidade,horarioInicial,horarioFinal,sala) VALUES (?,?,?,?)",(modalidade,horaInicial,horaFinal,sala))
        cursor.execute("SELECT modalidade FROM modalidades")
        modalidades = cursor.fetchall()
        cursor.execute("SELECT sala FROM salas")
        salas = cursor.fetchall()
        conexao.commit()
        conexao.close()
        mensagem = "Turma criada com sucesso!"
        return render_template("registroTurmas.html",mensagem=mensagem,modalidades=modalidades,salas=salas)
    #Turma já existe
    else:
        erro = "Uma turma com essas informações já existe"
        cursor.execute("SELECT modalidade FROM modalidades")
        modalidades = cursor.fetchall()
        cursor.execute("SELECT sala FROM salas")
        salas = cursor.fetchall()
        conexao.close()
        return render_template("registroTurmas.html",erro=erro,modalidades=modalidades,salas=salas)

#página de remover aluno
@app.route("/adm/alunos/remover")
def mostrarRemocaoA():
    # se adm tiver logado, acesso é permitido
    if admin:
        return render_template("removerAluno.html")
    #se não redirecionar para login ou inicio
    elif user:
        return redirect("/inicio")
    else:
        return redirect("/login")
@app.route("/adm/alunos/remover", methods=['POST'])
def removerAluno():
    #pegando dados do formulario
    cpf = request.form.get("cpf")
    #Removendo aluno
    conexao = sqlite3.connect('sistemaAcademia.db')
    cursor = conexao.cursor()
    #Verificando se cpf consta no banco de dados
    cursor.execute("SELECT usuario FROM clientes WHERE usuario=?",(cpf,))
    teste = cursor.fetchone()
    #cpf não existe
    if teste == None:
        erro = "cpf não consta no banco de dados"
        conexao.close()
        return render_template("removerAluno.html",erro=erro)
    #cpf encontrado
    else:
        cursor.execute("DELETE FROM clientes WHERE usuario=?",(cpf,))
        #deletando também da tabela alunosxturmas
        cursor.execute("DELETE FROM turmasxalunos WHERE aluno=?",(cpf,))
        conexao.commit()
        conexao.close()
        mensagem = "Aluno removido com sucesso!"
        return render_template("removerAluno.html",mensagem=mensagem)

#página de remover sala
@app.route("/adm/salas/remover")
def mostrarRemocaoS():
    # se adm tiver logado, acesso é permitido
    if admin:
        #mandando pra pagina informações das salas
        conexao = sqlite3.connect('sistemaAcademia.db')
        cursor = conexao.cursor()
        cursor.execute("SELECT sala FROM salas")
        salas = cursor.fetchall()
        conexao.close()
        return render_template("removerSala.html",salas=salas)
    elif user:
        return redirect("/inicio")
    else:
        return redirect("/login")
@app.route("/adm/salas/remover", methods=['POST'])
def removerSala():
    #pegando dados do formulario
    sala = request.form.get("sala")
    #Antes de remover a sala tem que remove-la da tabela turmas se ela tiver nela
    conexao = sqlite3.connect('sistemaAcademia.db')
    cursor = conexao.cursor()
    cursor.execute("UPDATE turmas SET sala=NULL WHERE sala=?",(sala,))
    #removendo sala e mandando informações atualizadas pra página
    cursor.execute("DELETE FROM salas WHERE sala=?",(sala,))
    cursor.execute("SELECT sala FROM salas")
    salas = cursor.fetchall()
    conexao.commit()
    conexao.close()
    mensagem = "Sala removida com sucesso!"
    return render_template("removerSala.html",mensagem=mensagem,salas=salas)

#página de remover modalidade
@app.route("/adm/modalidades/remover")
def mostrarRemocaoM():
    # se adm tiver logado, acesso é permitido
    if admin:
        #mandando pra pagina informações das modalidades
        conexao = sqlite3.connect('sistemaAcademia.db')
        cursor = conexao.cursor()
        cursor.execute("SELECT modalidade FROM modalidades")
        modalidades = cursor.fetchall()
        conexao.close()
        return render_template("removerModalidade.html",modalidades=modalidades)
    elif user:
        return redirect("/inicio")
    else:
        return redirect("/login")
@app.route("/adm/modalidades/remover", methods=['POST'])
def removerModalidade():
    #pegando dados do formulario
    modalidade = request.form.get("modalidade")
    conexao = sqlite3.connect('sistemaAcademia.db')
    cursor = conexao.cursor()
    #Removendo modalidade
    cursor.execute("DELETE FROM modalidades WHERE modalidade=?",(modalidade,))
    #removendo turmas que possuiam essa modalidade
    cursor.execute("SELECT id FROM turmas WHERE modalidade=?",(modalidade,))
    turmas = cursor.fetchall()
    for turma in turmas:
        #Removendo linha da tabela turmasxalunos onde tem turma excluída
        cursor.execute("DELETE FROM turmasxalunos WHERE turma=?",(turma[0],))
        #Removendo linha da tabela turmasxdias onde tem turma excluída
        cursor.execute("DELETE FROM turmasxdias WHERE turma=?",(turma[0],))
        #Removendo turmas
        cursor.execute("DELETE FROM turmas WHERE id=?",(turma[0],))
    #mandando pra pagina informações das modalidades
    cursor.execute("SELECT modalidade FROM modalidades")
    modalidades = cursor.fetchall()
    conexao.commit()
    conexao.close()
    mensagem = "Modalidade removida com sucesso!"
    return render_template("removerModalidade.html",mensagem=mensagem,modalidades=modalidades)

#página de remover turma
@app.route("/adm/turmas/remover")
def mostrarRemocaoT():
    # se adm tiver logado, acesso é permitido
    if admin:
        #mandando pra pagina informações das turmas
        conexao = sqlite3.connect('sistemaAcademia.db')
        cursor = conexao.cursor()
        cursor.execute("SELECT id FROM turmas")
        turmas = cursor.fetchall()
        conexao.close()
        return render_template("removerTurma.html",turmas=turmas)
    elif user:
        return redirect("/inicio")
    else:
        return redirect("/login")
@app.route("/adm/turmas/remover", methods=['POST'])
def removerTurma():
    #pegando dados do formulario
    turma = request.form.get("turma")
    conexao = sqlite3.connect('sistemaAcademia.db')
    cursor = conexao.cursor()
    #Removendo linha da tabela turmasxalunos onde tem turma excluída
    cursor.execute("DELETE FROM turmasxalunos WHERE turma=?",(turma,))
    #Removendo linha da tabela turmasxdias onde tem turma excluída
    cursor.execute("DELETE FROM turmasxdias WHERE turma=?",(turma,))
    #Removendo turma
    cursor.execute("DELETE FROM turmas WHERE id=?",(turma,))
    #pegando informação das turmas existentes para mandar para a página
    cursor.execute("SELECT id FROM turmas")
    turmas = cursor.fetchall()
    conexao.commit()
    conexao.close()
    mensagem = "Turma removida com sucesso!"
    return render_template("removerTurma.html",mensagem=mensagem,turmas=turmas)

#página de gráficos
@app.route("/adm/graficos")
def graficos():
    # se adm tiver logado, acesso é permitido
    if admin:
        conexao = sqlite3.connect('sistemaAcademia.db')
        cursor = conexao.cursor()
        #informações de quantidade de cada sexo
        cursor.execute("SELECT sexo FROM clientes")
        sexos = cursor.fetchall()
        masculino = 0
        feminino = 0
        for pessoa in sexos:
            if pessoa[0] == "masculino":
                masculino += 1
            if pessoa[0] == "feminino":
                feminino += 1
        totalSexo = masculino+feminino
        sexoNomes = ["masculino","feminino"]
        sexoDados = [masculino/totalSexo,feminino/totalSexo]
        #informações de quantidade das idades
        cursor.execute("SELECT nascimento FROM clientes")
        nascimentos = cursor.fetchall()
        menor18 = 0
        d18a29 = 0
        d30a39 = 0
        d40a49 = 0
        d50a60 = 0
        maior60 = 0
        for cliente in nascimentos:
            idade = calcIdade(cliente[0])
            if idade < 18:
                menor18 += 1
            elif idade < 30:
                d18a29 += 1
            elif idade < 40:
                d30a39 += 1
            elif idade < 50:
                d40a49 += 1
            elif idade <= 60:
                d50a60 += 1
            else:
                maior60 += 1
        idadeNomes = ["menor de 18","de 18 a 29","de 30 a 39","de 40 a 49","de 50 a 60","mais de 60"]
        idadeDados = [menor18,d18a29,d30a39,d40a49,d50a60,maior60]
        #informação de alunos por modalidades
        cursor.execute("SELECT modalidade FROM modalidades")
        modalidades = cursor.fetchall()
        modalidadeNomes = []
        for m in modalidades:
            modalidadeNomes.append(m[0])
        modalidadeDados = []
        for nome in modalidadeNomes:
            cursor.execute("SELECT id FROM turmas WHERE modalidade=?",(nome,))
            idsModalidade = cursor.fetchall()
            numAlunos = 0
            for ids in idsModalidade:
                cursor.execute("SELECT * FROM turmasxalunos WHERE turma=?",(str(ids[0]),))
                alunos = cursor.fetchall()
                for a in alunos:
                    numAlunos +=1
            modalidadeDados.append(numAlunos)       
        conexao.close()
        return render_template("admGraficos.html",sexoNomes=sexoNomes,sexoDados=sexoDados,idadeNomes=idadeNomes,idadeDados=idadeDados,modalidadeNomes=modalidadeNomes,modalidadeDados=modalidadeDados)
    elif user:
        return redirect("/inicio")
    else:
        return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)