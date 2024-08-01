import sqlite3

conexao = sqlite3.connect('sistemaAcademia.db')
cursor = conexao.cursor()
"""
cursor.execute('''
                CREATE TABLE IF NOT EXISTS turmas
                    (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    modalidade TEXT,
                    horarioInicial TEXT,
                    horarioFinal TEXT,
                    sala TEXT,
                    FOREIGN KEY (sala) REFERENCES salas(sala) ON DELETE SET NULL,
                    FOREIGN KEY (modalidade) REFERENCES modalidades(modalidade) ON DELETE SET NULL
                    )
                ''')
cursor.execute('''
                CREATE TABLE IF NOT EXISTS salas
                    (
                    sala TEXT PRIMARY KEY
                    )
                ''')
cursor.execute('''
                CREATE TABLE IF NOT EXISTS modalidades 
                    (
                    modalidade TEXT PRIMARY KEY
                    )
                ''')
cursor.execute('''
                CREATE TABLE IF NOT EXISTS clientes
                    (
                    nome TEXT,
                    usuario TEXT PRIMARY KEY,
                    senha TEXT,
                    sexo TEXT,
                    nascimento TEXT,
                    apelido TEXT
                    )
                ''')
cursor.execute('''
                CREATE TABLE IF NOT EXISTS turmasxalunos 
                    (
                    turma TEXT,
                    aluno TEXT,
                    FOREIGN KEY (turma) REFERENCES turmas(id) ON DELETE SET NULL,
                    FOREIGN KEY (aluno) REFERENCES clientes(usuario) ON DELETE SET NULL
                    )
                ''')
cursor.execute('''
                CREATE TABLE IF NOT EXISTS turmasxdias 
                    (
                    turma TEXT,
                    dia TEXT,
                    FOREIGN KEY (turma) REFERENCES turmas(id) ON DELETE SET NULL
                    )
                ''')
cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin
                    (
                    usuario TEXT PRIMARY KEY,
                    senha TEXT,
                    nome TEXT,
                    apelido TEXT
                    )
                ''')
"""
conexao.commit()
conexao.close()