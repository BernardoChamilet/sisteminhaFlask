Sistema de academia com registro de clientes, turmas, salas, modalidades e geração de gráficos.
Flask, html, css, javascript, charjs e sqlite3

TAREFAS PENDENTES:
1. Registrar dias da semana nas turmas e mostrar na página(Checkbox).
2. Verificar choque de horários na criação de turmas.
3. Adcionar tabela de professores. Fazer página pros professores. Fazer lista de chamada das turmas.
4. Opção de editar turmas, possibilitando mudar sala, horários e dias da semana. (dica de como fazer no html admTurmas) Mesma dica serve para excluir. Foto no google fotos ajuda com isso.
5. Gerar o máximo de gráficos que conseguir imaginar
6. Estudar front-end para melhor design
7. Usar o extends do jinja2 adequadamente em todas as páginas html

Algumas notas para caso não esteja entendendo os códigos:
1. O admin matricula os clientes e depois os clientes podem se cadastrar usando seu cpf.
2. Para restrição de acesso a rotas há basicamente uma comparação de três possíveis situações: adm estiver logado, usuario estiver logado e ninguém estiver logado.
3. A página de sucesso é uma página para ser exibida apenas depois de um cadastro bem sucedido, portanto não se assuste com a rota e/ou variável sucesso no código, pois foi uma grande cambiarra.