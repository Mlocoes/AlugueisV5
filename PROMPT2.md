________________________________________
🚀 PROMPT COMPLETO — Claude 4.5 (para Visual Studio Code)
Use este prompt diretamente em Claude 4.5 dentro do VS Code.
Ele já vem com instruções para gerar código Python (FastAPI + SQLAlchemy + PostgreSQL) e frontend com Handsontable.
O fluxo é interativo, e Claude vai codificar etapa por etapa.
________________________________________
🧠 Contexto e Objetivo
Você é um engenheiro de software sênior especializado em desenvolvimento Python com FastAPI, SQLAlchemy e PostgreSQL, e integração com frontend moderno (Handsontable + TailwindCSS + Chart.js).
Sua tarefa é gerar, de forma interativa e modular, uma aplicação completa de gestão de imóveis e aluguéis, com controle de permissões financeiras definido por administradores.
O sistema será codificado dentro do Visual Studio Code, e o código deve estar organizado, comentado e pronto para execução com Docker Compose.
________________________________________
⚙️ Especificações Técnicas
Backend:
•	Linguagem: Python 3.11+
•	Framework: FastAPI
•	ORM: SQLAlchemy 2.0
•	DB: PostgreSQL
•	Migrações: Alembic
•	Autenticação: JWT (PyJWT)
•	Senhas: Passlib (bcrypt)
•	Testes: pytest
•	Containers: Docker + docker-compose
Frontend:
•	HTML + TailwindCSS
•	Handsontable para tabelas e edição
•	Chart.js para gráficos
•	JS Fetch para consumir a API
•	Design responsivo para desktop e móvel
________________________________________
🧩 Estrutura da Base de Dados
Crie os seguintes modelos com SQLAlchemy:
usuarios
•	id (PK)
•	nome
•	tipo (Administrador | Usuário)
•	email (único)
•	telefone
•	senha_hash
•	ativo (bool)
imoveis
•	id (PK)
•	nome
•	endereco
•	alugado (bool)
•	ativo (bool)
participacoes
•	id (PK)
•	id_imovel (FK → imoveis.id)
•	id_proprietario (FK → usuarios.id)
•	participacao (float)
→ soma total por imóvel deve ser 100 ± 0.4%
•	data_cadastro (timestamp, grupo único de versão)
alugueis
•	id (PK)
•	id_imovel (FK → imoveis.id)
•	id_proprietario (FK → usuarios.id)
•	valor_liquido (float, pode ser negativo)
•	darf (float opcional)
•	data_cadastro (timestamp)
alias
•	id (PK)
•	nome
•	ativo (bool)
alias_proprietarios
•	id (PK)
•	id_alias (FK → alias.id)
•	id_proprietario (FK → usuarios.id)
transferencias
•	id (PK)
•	id_alias (FK → alias.id)
•	id_proprietario (FK → usuarios.id)
•	valor (float)
•	data_inicio
•	data_fim
permissoes_financeiras
•	id (PK)
•	id_admin (FK → usuarios.id, tipo=Administrador)
•	id_usuario (FK → usuarios.id, tipo=Usuário)
•	id_proprietario_autorizado (FK → usuarios.id, tipo=Proprietário)
________________________________________
🔒 Controle de Acesso
•	Somente administradores podem criar, editar ou excluir registros.
•	Usuários comuns:
o	Não veem dados inativos.
o	Só veem informações financeiras dos proprietários definidos em permissoes_financeiras.
o	Não têm botões de edição ou criação.
________________________________________
💰 Regras de Negócio
•	Soma das participações por imóvel = 100 ± 0.4 %
•	taxa_admin_proprietario = taxa_admin_total * (participacao / 100)
•	Aluguel total anual = soma dos aluguéis do ano corrente
•	Se flag “Transferências” estiver ativo, somar aluguel + transferência no relatório
________________________________________
🖥️ Telas e Funcionalidades
🔐 Login
•	Tela simples com email + senha
•	Autenticação via JWT
•	Sessão expira após tempo configurável
•	Recarregar = volta ao login
🏠 Dashboard
•	Menu lateral persistente
•	Mostra:
o	Nº imóveis alugados
o	Nº imóveis disponíveis
o	Valor acumulado do ano
o	Valor do último mês
o	Variação percentual mês a mês
o	Gráfico mensal (Chart.js)
👤 Proprietários
•	Tabela (Handsontable)
•	Botões: Novo / Editar (somente admin)
•	Ocultar IDs
•	Usuários comuns: somente visualização
🏢 Imóveis
•	Tabela (Handsontable)
•	Botões: Novo / Editar (somente admin)
•	Filtro por status (alugado/disponível)
•	Usuários comuns: somente leitura
📊 Participações
•	Tabela (Handsontable):
o	Linhas = imóveis
o	Colunas = proprietários
o	Células = participações (%)
•	Botão “Editar” → mostra e permite editar todas as participações de um imóvel
•	Verificação automática: soma = 100 ± 0.4%
•	Combo para escolher versão (data_cadastro)
💵 Aluguel
•	Tabela (Handsontable):
o	Linhas = imóveis
o	Colunas = proprietários
o	Células = valor_liquido
•	Filtros:
o	Ano (padrão = último cadastrado)
o	Mês (padrão = último cadastrado ou “Todos”)
•	“Todos os meses” → soma acumulada
📈 Relatórios
•	Colunas: Aluguel | Darf | Taxa de Administração
•	Filtros:
o	Ano
o	Mês
o	Proprietário / Alias
o	Flag “Transferências” → soma aluguel + transferência
•	Dados filtrados e limitados pelas permissões do usuário
⚙️ Administração
•	Botões:
o	Novo Alias / Editar Alias
o	Nova Transferência / Editar Transferência
o	Importar Excel (via pandas)
•	Upload → validação e inserção automática
________________________________________
🧭 Fluxo de Desenvolvimento (Claude deve seguir)
1.	Confirmar stack (FastAPI + SQLAlchemy + PostgreSQL)
2.	Gerar estrutura de diretórios:
3.	app/
4.	  ├── main.py
5.	  ├── models/
6.	  ├── routes/
7.	  ├── schemas/
8.	  ├── services/
9.	  ├── core/ (config, segurança, auth)
10.	  ├── static/
11.	  └── templates/
12.	Gerar models e schemas
13.	Gerar endpoints REST
14.	Adicionar autenticação JWT
15.	Implementar middleware de autorização (baseado em permissões financeiras)
16.	Gerar frontend básico com Handsontable
17.	Conectar frontend com backend
18.	Criar gráfico do dashboard
19.	Gerar migrações Alembic
20.	Criar docker-compose.yml (FastAPI + PostgreSQL)
21.	Adicionar scripts de teste (pytest)
________________________________________
🔁 Interatividade
Antes de gerar cada parte, pergunte:
“Deseja que eu gere esta parte agora (Sim/Não)?”
Etapas interativas recomendadas:
1.	Modelos e migrações
2.	Rotas e autenticação
3.	Dashboard e frontend básico
4.	Controle de permissões financeiras
5.	Relatórios e gráficos
6.	Deploy (Docker)
________________________________________
🧩 Resultado Esperado
Uma aplicação modular, segura e responsiva, com:
•	Controle de acesso granular a dados financeiros
•	Interface editável via Handsontable
•	Dashboards e relatórios dinâmicos
•	Backend em Python/FASTAPI pronto para produção
•	Compatibilidade total com dispositivos móveis
________________________________________
🧾 Instrução final para Claude 4.5
Gere o código de forma modular, começando pela estrutura do projeto e modelos SQLAlchemy.
Pergunte antes de avançar para cada módulo seguinte.
Organize o código em diretórios prontos para rodar no VS Code com uvicorn main:app --reload.
Inclua comentários explicativos e docstrings em todas as classes e funções.
________________________________________
-- =========================================
-- 1️⃣ Tabela de Usuários / Proprietários
-- =========================================
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    tipo VARCHAR(20) CHECK (tipo IN ('administrador', 'usuario')) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    telefone VARCHAR(20),
    ativo BOOLEAN DEFAULT TRUE
);

-- =========================================
-- 2️⃣ Tabela de Imóveis
-- =========================================
CREATE TABLE imoveis (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    endereco TEXT NOT NULL,
    alugado BOOLEAN DEFAULT FALSE,
    ativo BOOLEAN DEFAULT TRUE
);

-- =========================================
-- 3️⃣ Tabela de Participações
-- =========================================
-- Guarda o percentual de cada proprietário em cada imóvel.
-- Vários registros podem coexistir com diferentes datas de cadastro (histórico).
CREATE TABLE participacoes (
    id SERIAL PRIMARY KEY,
    id_imovel INTEGER REFERENCES imoveis(id) ON DELETE CASCADE,
    id_proprietario INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    participacao NUMERIC(6,3) CHECK (participacao >= 0 AND participacao <= 100),
    data_cadastro DATE NOT NULL,
    UNIQUE (id_imovel, id_proprietario, data_cadastro)
);

-- Índice para facilitar filtragem por data
CREATE INDEX idx_participacoes_data ON participacoes (data_cadastro);

-- =========================================
-- 4️⃣ Tabela de Aluguéis
-- =========================================
-- Armazena valores líquidos por proprietário e imóvel.
CREATE TABLE alugueis (
    id SERIAL PRIMARY KEY,
    id_imovel INTEGER REFERENCES imoveis(id) ON DELETE CASCADE,
    id_proprietario INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    aluguel_liquido NUMERIC(12,2) DEFAULT 0,
    taxa_administracao_total NUMERIC(6,2) DEFAULT 0,
    darf NUMERIC(12,2) DEFAULT 0,
    data_cadastro DATE NOT NULL
);

-- Índices de performance
CREATE INDEX idx_alugueis_data ON alugueis (data_cadastro);
CREATE INDEX idx_alugueis_imovel_prop ON alugueis (id_imovel, id_proprietario);

-- =========================================
-- 5️⃣ Tabela de Aliases (grupos de proprietários)
-- =========================================
CREATE TABLE alias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    ativo BOOLEAN DEFAULT TRUE
);

-- Relação N:N entre Aliases e Proprietários
CREATE TABLE alias_proprietarios (
    id_alias INTEGER REFERENCES alias(id) ON DELETE CASCADE,
    id_proprietario INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    PRIMARY KEY (id_alias, id_proprietario)
);

-- =========================================
-- 6️⃣ Tabela de Transferências
-- =========================================
CREATE TABLE transferencias (
    id SERIAL PRIMARY KEY,
    id_alias INTEGER REFERENCES alias(id) ON DELETE CASCADE,
    id_proprietario INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    valor NUMERIC(12,2) DEFAULT 0,
    data_inicio DATE NOT NULL,
    data_fim DATE
);

CREATE INDEX idx_transferencias_periodo ON transferencias (data_inicio, data_fim);

-- =========================================
-- 7️⃣ Tabela de Permissões Financeiras
-- =========================================
-- Define o que cada usuário pode ver/editar em termos de dados financeiros.
CREATE TABLE permissoes_financeiras (
    id SERIAL PRIMARY KEY,
    id_usuario INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    id_proprietario INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    visualizar BOOLEAN DEFAULT TRUE,
    editar BOOLEAN DEFAULT FALSE,
    data_criacao TIMESTAMP DEFAULT NOW(),
    UNIQUE (id_usuario, id_proprietario)
);

CREATE INDEX idx_perm_fin_usuario_prop ON permissoes_financeiras (id_usuario, id_proprietario);

-- =========================================
-- 8️⃣ View auxiliar para cálculo da Taxa de Administração individual
-- =========================================
CREATE OR REPLACE VIEW vw_taxa_admin_proprietario AS
SELECT 
    a.id AS id_aluguel,
    a.id_imovel,
    a.id_proprietario,
    a.aluguel_liquido,
    p.participacao,
    (a.taxa_administracao_total * (p.participacao / 100.0)) AS taxa_admin_prop
FROM alugueis a
JOIN participacoes p
  ON a.id_imovel = p.id_imovel
  AND a.id_proprietario = p.id_proprietario
  AND p.data_cadastro = (
      SELECT MAX(data_cadastro) 
      FROM participacoes 
      WHERE id_imovel = a.id_imovel 
        AND id_proprietario = a.id_proprietario
  );


Quero que implemente uma nova funcionalidade:
Importar.
Nessa funcionalidade o sistema deve ler os arquivos dados e importa-los na BD.
Os arquivos modelos fornecidos são:
- Proprietários – Proprietario.xlsx.
Nome	Sobrenome	Documento	Tipo Documento	Endereço	Telefone	Email
Jandira	Cozzolino		CPF	Rua Fernao Dias, 98 apto 101		
Manoel	Cozzolino	170,858,698-95	CPF	Plaza España 4, 2 A	34 646090242	mcozzolinoes@gmail.com

Fabio	Cozzolino		CPF			
Carla	Cozzolino		CPF	Rua Fernao Dias, 98 apto 101		
Armando	Garcia		CPF			
Suely	Garcia		CPF			
Felipe	Marmo		CPF			
Adriana	Marmo		CPF			
Regina	Marmo		CPF			
Mario Angelo	Marmo		CPF			

- Imóveis – Imoveis.xlsx.
Nome	Endereço	Tipo	Área Total	Área Construida	Valor Catastral	Valor Mercado	IPTU Anual	Condominio
Cunha Gago 223	Rua Cunha Gago 223	Comercial	         316,40 	         316,40 	  2.400.000,00 	  2.400.000,00 	      3.036,12 	                  -   
Teodoro Sampaio 1779	Rua Teodoro Sampaio 1779	Comercial	         905,00 	         905,00 	  9.400.000,00 	  9.400.000,00 		                  -   
Dep. Lacerda	Rua Dep. Lacerda	Comercial	         350,00 	         350,00 	  1.200.000,00 	  1.200.000,00 	      2.390,58 	                  -   
Cardeal Arcoverde 1840	Rua Cardeal Arcoverde 1840	Comercial	         400,00 	         400,00 	     480.000,00 	     480.000,00 		                  -   
Cardeal Arcoverde 1838	Rua Cardeal Arcoverde 1838	Comercial	         400,00 	         400,00 	     400.000,00 	     400.000,00 		                  -   
Cardeal Arcoverde 1836	Rua Cardeal Arcoverde 1836	Comercial	         400,00 	         400,00 	     440.000,00 	     440.000,00 		                  -   
Floresta 369	Rua Floresta 369	Comercial	         472,00 	         472,00 	     320.000,00 	     320.000,00 		                  -   
Floresta 393	Rua Floresta 393	Comercial	         577,00 	         577,00 	     320.000,00 	     320.000,00 		                  -   
Vila Ema	Vila Ema	Comercial	         800,00 	         800,00 	     560.000,00 	     560.000,00 		                  -   
D. Leopoldina	D. Leopoldina	Comercial	         440,00 	         440,00 	     940.000,00 	     940.000,00 	      1.550,00 	                  -   
General flores	Rua General flores	Comercial			     300.000,00 	     300.000,00 		                  -   
Oliveira Lima	Rua Oliveira Lima	Comercial	         227,00 	         227,00 	     300.000,00 	     300.000,00 		                  -   
Oliveira Lima 2	Rua Oliveira Lima 2	Comercial	         225,00 	         225,00 	     300.000,00 	     300.000,00 		                  -   
Lisboa	Rua Lisboa	Residencial			     560.000,00 	     560.000,00 		                  -   
Faria Lima	Avinida Faria Lima	Comercial			  1.160.000,00 	  1.160.000,00 		                  -   
Clodomiro	Rua Clodomiro	Comercial	         181,50 	         181,50 	  2.280.000,00 	  2.280.000,00 		                  -   
Henrique Schaumann	Rua Henrique Schaumann 733	Comercial	         162,00 	         162,00 	  4.800.000,00 	  4.800.000,00 	      1.830,50 	                  -   
Teodoro Sampaio 1882	Rua Teodoro Sampaio 1882	Comercial	         210,00 	         210,00 	  1.800.000,00 	  1.800.000,00 	      1.931,73 	                  -   
Cunha Gago 431	Rua Cunha Gago 431	Comercial	         121,50 	         121,50 	  1.200.000,00 	  1.200.000,00 	         735,87 	                  -   

- Participação – Participacao.xlsx

Nome	Endereço	VALOR 	Jandira	Manoel	Fabio	Carla	Armando	Suely	Felipe	Adriana	Regina	Mario Angelo
Cunha Gago 223	Rua Cunha Gago 223	100,000000 %	25,000000 %	8,333333 %	8,333333 %	8,333333 %	12,500000 %	12,500000 %	4,166667 %	4,166667 %	8,333333 %	8,333333 %
Teodoro Sampaio 1779	Rua Teodoro Sampaio 1779	100,000000 %	12,500000 %	6,944444 %	6,944444 %	6,944444 %	16,666667 %	16,666667 %	5,555556 %	5,555556 %	11,111111 %	11,111111 %
Dep. Lacerda	Rua Dep. Lacerda	100,000000 %	12,500000 %	6,944444 %	6,944444 %	6,944444 %	16,666667 %	16,666667 %	5,555556 %	5,555556 %	11,111111 %	11,111111 %
Cardeal Arcoverde 1840	Rua Cardeal Arcoverde 1840	100,000000 %	12,500000 %	6,944444 %	6,944444 %	6,944444 %	16,666667 %	16,666667 %	5,555556 %	5,555556 %	11,111111 %	11,111111 %
Cardeal Arcoverde 1838	Rua Cardeal Arcoverde 1838	100,000000 %	12,500000 %	6,944444 %	6,944444 %	6,944444 %	16,666667 %	16,666667 %	5,555556 %	5,555556 %	11,111111 %	11,111111 %
Cardeal Arcoverde 1836	Rua Cardeal Arcoverde 1836	100,000000 %	12,500000 %	6,944444 %	6,944444 %	6,944444 %	16,666667 %	16,666667 %	5,555556 %	5,555556 %	11,111111 %	11,111111 %
Floresta 369	Rua Floresta 369	100,000000 %	12,500000 %	6,944444 %	6,944444 %	6,944444 %	16,666667 %	16,666667 %	5,555556 %	5,555556 %	11,111111 %	11,111111 %
Floresta 393	Rua Floresta 393	100,000000 %	12,500000 %	6,944444 %	6,944444 %	6,944444 %	16,666667 %	16,666667 %	5,555556 %	5,555556 %	11,111111 %	11,111111 %
Vila Ema	Vila Ema	100,000000 %	12,500000 %	6,944444 %	6,944444 %	6,944444 %	16,666667 %	16,666667 %	5,555556 %	5,555556 %	11,111111 %	11,111111 %
D. Leopoldina	D. Leopoldina	100,000000 %	12,500000 %	6,944444 %	6,944444 %	6,944444 %	16,666667 %	16,666667 %	5,555556 %	5,555556 %	11,111111 %	11,111111 %
General flores	Rua General flores	100,000000 %	12,500000 %	6,944444 %	6,944444 %	6,944444 %	16,666667 %	16,666667 %	5,555556 %	5,555556 %	11,111111 %	11,111111 %
Oliveira Lima	Rua Oliveira Lima	100,000000 %	12,500000 %	6,944444 %	6,944444 %	6,944444 %	16,666667 %	16,666667 %	5,555556 %	5,555556 %	11,111111 %	11,111111 %
Oliveira Lima 2	Rua Oliveira Lima 2	100,000000 %	12,500000 %	6,944444 %	6,944444 %	6,944444 %	16,666667 %	16,666667 %	5,555556 %	5,555556 %	11,111111 %	11,111111 %
Lisboa	Rua Lisboa	100,000000 %	0,000000 %	11,111111 %	11,111111 %	11,111111 %	16,666667 %	16,666667 %	5,555556 %	5,555556 %	11,111111 %	11,111111 %
Faria Lima	Avinida Faria Lima	100,000000 %	0,000000 %	11,111111 %	11,111111 %	11,111111 %	16,666667 %	16,666667 %	5,555556 %	5,555556 %	11,111111 %	11,111111 %
Clodomiro	Rua Clodomiro	100,000000 %	0,000000 %	66,666667 %	0,000000 %	0,000000 %	16,666667 %	16,666667 %	0,000000 %	0,000000 %	0,000000 %	0,000000 %
Henrique Schaumann	Rua Henrique Schaumann 733	100,000000 %	50,000000 %	16,666667 %	16,666667 %	16,666667 %	0,000000 %	0,000000 %	0,000000 %	0,000000 %	0,000000 %	0,000000 %
Teodoro Sampaio 1882	Rua Teodoro Sampaio 1882	100,000000 %	50,000000 %	16,666667 %	16,666667 %	16,666667 %	0,000000 %	0,000000 %	0,000000 %	0,000000 %	0,000000 %	0,000000 %
Cunha Gago 431	Rua Cunha Gago 431	100,000000 %	0,000000 %	50,000000 %	50,000000 %	0,000000 %	0,000000 %	0,000000 %	0,000000 %	0,000000 %	0,000000 %	0,000000 %
v
-Alugueis – Aluguel.xlsx
24/09/2025	Valor Total	Jandira	Manoel	Fabio	Carla	Armando	Suely	Felipe	Adriana	Regina	Mario Angelo	Taxa de Administração
Cunha Gago 223	 14.713,62 	 3.597,25 	    1.235,15 	 1.235,15 	 1.235,15 	 1.852,73 	 1.852,73 	     617,58 	     617,58 	 1.235,15 	       1.235,15 	                      1.003,59 
Teodoro Sampaio 1779	 53.765,83 	 6.458,29 	    4.208,61 	 4.023,95 	 4.208,61 	 8.252,30 	 8.252,44 	 3.320,57 	 3.320,57 	 5.860,25 	       5.860,25 	                      3.189,68 
Dep. Lacerda	    5.933,32 	     741,67 	       412,04 	     412,04 	     412,04 	     988,89 	     988,89 	     329,63 	     329,63 	     659,26 	          659,26 	                          488,25 
Cardeal Arcoverde 1840	    3.026,88 	     378,36 	       210,20 	     210,20 	     210,20 	     504,48 	     504,48 	     168,16 	     168,16 	     336,32 	          336,32 	                          192,31 
Cardeal Arcoverde 1838	    2.627,50 	     328,44 	       182,47 	     182,47 	     182,47 	     437,92 	     437,92 	     145,97 	     145,97 	     291,94 	          291,94 	                          175,99 
Cardeal Arcoverde 1836	    2.542,96 	     317,87 	       176,59 	     176,59 	     176,59 	     423,83 	     423,83 	     141,28 	     141,28 	     282,55 	          282,55 	                          157,18 
Floresta 369	    2.043,06 	     255,38 	       141,88 	     141,88 	     141,88 	     340,51 	     340,51 	     113,50 	     113,50 	     227,01 	          227,01 	                          125,71 
Floresta 393	    2.035,44 	     254,43 	       141,35 	     141,35 	     141,35 	     339,24 	     339,24 	     113,08 	     113,08 	     226,16 	          226,16 	                          133,33 
Vila Ema	    2.858,98 	     357,37 	       198,54 	     198,54 	     198,54 	     476,50 	     476,50 	     158,83 	     158,83 	     317,66 	          317,66 	                          253,78 
D. Leopoldina	-  1.863,76 	-   232,97 	-     129,43 	-   129,43 	-   129,43 	-   310,63 	-   310,63 	-   103,54 	-   103,54 	-   207,08 	-         207,08 	                            88,75 
General flores	               -   	             -   	               -   	             -   	             -   	             -   	             -   	             -   	             -   	             -   	                  -   	                                  -   
Oliveira Lima	-     524,93 	-     65,62 	-        36,45 	-     36,45 	-     36,45 	-     87,49 	-     87,49 	-     29,16 	-     29,16 	-     58,33 	-           58,33 	                            25,00 
Oliveira Lima 2	-     527,49 	-     65,94 	-        36,63 	-     36,63 	-     36,63 	-     87,92 	-     87,92 	-     29,31 	-     29,31 	-     58,61 	-           58,61 	                            25,15 
Lisboa	-  2.450,42 	             -   	-     272,27 	-   272,27 	-   272,27 	-   408,40 	-   408,40 	-   136,13 	-   136,13 	-   272,27 	-         272,27 	                          116,70 
Faria Lima	    9.885,49 	             -   	    1.098,39 	 1.098,39 	 1.098,39 	 1.647,58 	 1.647,58 	     549,19 	     549,19 	 1.098,39 	       1.098,39 	                          942,69 
Clodomiro	 15.019,99 	             -   	 10.013,33 	             -   	             -   	 2.503,33 	 2.503,33 	             -   	             -   	             -   	                  -   	                          928,77 
Henrique Schaumann	-  2.872,41 	-1.436,21 	-     478,74 	-   478,74 	-   478,74 	             -   	             -   	             -   	             -   	             -   	                  -   	                          136,80 
Teodoro Sampaio 1882	 10.504,48 	 4.980,85 	    1.841,21 	 1.841,21 	 1.841,21 	             -   	             -   	             -   	             -   	             -   	                  -   	                          723,64 
Cunha Gago 431	    4.584,54 	             -   	    2.292,27 	 2.292,27 	             -   	             -   	             -   	             -   	             -   	             -   	                  -   	                          295,46 


O excel de alugueis ainda terá uma planilha para cada mês, ou seja, o sistema deve ser capaz  de ler varias planilhas em um arquivo.

Prompt para Funcionalidade de Importação de Dados
Objetivo
Implementar uma funcionalidade de importação que leia arquivos Excel (.xlsx) e importe os dados para o banco de dados, processando informações de proprietários, imóveis, participações e aluguéis.
Arquivos a Serem Importados
1. Proprietario.xlsx
Estrutura da planilha:
•	Colunas: Nome, Sobrenome, Documento, Tipo Documento, Endereço, Telefone, Email
•	Características: 
o	Planilha única
o	Alguns campos podem estar vazios
o	Documento pode conter formatação com pontos, vírgulas e hífens (ex: 170,858,698-95)
o	Tipo Documento geralmente é "CPF"
Regras de importação:
•	Validar formato de documento (CPF)
•	Normalizar documento removendo caracteres especiais para armazenamento
•	Permitir campos opcionais vazios
•	Tratar duplicatas (verificar por documento)
2. Imoveis.xlsx
Estrutura da planilha:
•	Colunas: Nome, Endereço, Tipo, Área Total, Área Construída, Valor Catastral, Valor Mercado, IPTU Anual, Condomínio
•	Características: 
o	Planilha única
o	Valores numéricos com separador de milhares (espaços ou pontos)
o	Separador decimal é vírgula
o	Alguns campos numéricos podem estar vazios
o	Tipo pode ser "Comercial" ou "Residencial"
Regras de importação:
•	Converter valores monetários (remover formatação, converter vírgulas para pontos)
•	Converter áreas para formato numérico decimal
•	Validar que Nome e Endereço sejam únicos
•	Permitir campos numéricos opcionais (área, IPTU, condomínio)
3. Participacao.xlsx
Estrutura da planilha:
•	Colunas: Nome, Endereço, VALOR, [Colunas dinâmicas com nomes dos proprietários]
•	Características: 
o	Primeira coluna: Nome do imóvel
o	Segunda coluna: Endereço do imóvel
o	Terceira coluna: VALOR (sempre 100,000000 %)
o	Demais colunas: Percentuais de participação de cada proprietário
o	Percentuais em formato "XX,XXXXXX %"
o	Soma das participações deve ser 100%
Regras de importação:
•	Relacionar imóvel através de Nome ou Endereço
•	Relacionar proprietários através dos nomes das colunas (Nome + Sobrenome)
•	Converter percentuais para formato decimal (dividir por 100)
•	Criar registros de participação apenas quando percentual > 0
•	Validar que soma de participações = 100% (com tolerância para arredondamento)
4. Aluguel.xlsx
Estrutura especial:
•	MÚLTIPLAS PLANILHAS - uma por mês de referência
•	Primeira linha: Data no formato DD/MM/YYYY (ex: 24/09/2025) que identifica o mês
•	Colunas: 
o	Primeira coluna: Nome/Endereço do imóvel
o	Segunda coluna: Valor Total
o	Colunas seguintes: Valores distribuídos por proprietário (nomes dos proprietários)
o	Última coluna: Taxa de Administração
Características:
•	Valores podem ser negativos (representados com hífen: "- 1.863,76")
•	Formato monetário com separadores de milhares e vírgula decimal
•	Valores vazios representados por "-" ou em branco
•	Cada planilha representa um mês diferente
Regras de importação:
•	Iterar sobre todas as planilhas do arquivo
•	Extrair data de referência da primeira célula (A1)
•	Relacionar imóvel através do nome/endereço da primeira coluna
•	Relacionar proprietários através dos nomes das colunas
•	Converter valores monetários (inclusive negativos)
•	Validar que soma dos valores individuais + taxa ≈ Valor Total
•	Permitir valores negativos (aluguéis não recebidos, ajustes)
Requisitos Técnicos
Tecnologias e Bibliotecas
•	Leitura de Excel: Utilizar biblioteca adequada (ex: SheetJS/xlsx, openpyxl, apache-poi, etc.)
•	Processamento: Manipular múltiplas planilhas em um mesmo arquivo
•	Validação: Implementar validações de integridade de dados
•	Transações: Garantir atomicidade na importação (tudo ou nada)
Interface do Usuário
•	Permitir seleção de múltiplos arquivos ou pasta
•	Indicar progresso da importação
•	Exibir log de erros e avisos
•	Confirmar dados antes de importar
•	Opção de rollback em caso de erro
Tratamento de Erros
•	Erros de formato: Arquivo corrompido, estrutura incorreta
•	Erros de validação: Dados inválidos, referências não encontradas
•	Erros de duplicação: Registros já existentes
•	Erros de relacionamento: Proprietário ou imóvel não encontrado
Ordem de Importação
1.	Primeiro: Proprietario.xlsx (criar registros de proprietários)
2.	Segundo: Imoveis.xlsx (criar registros de imóveis)
3.	Terceiro: Participacao.xlsx (criar relacionamentos proprietário-imóvel)
4.	Quarto: Aluguel.xlsx (criar registros de aluguéis mensais)
Validações Importantes
•	Verificar existência de colunas obrigatórias
•	Validar tipos de dados antes de inserir
•	Verificar integridade referencial (imóveis e proprietários devem existir)
•	Normalizar nomes para matching (trim, lowercase para comparação)
•	Validar somas e totais
•	Alertar sobre inconsistências sem bloquear importação
Funcionalidades Adicionais Desejáveis
•	Preview: Mostrar dados antes de importar
•	Modo atualização: Atualizar registros existentes ao invés de duplicar
•	Modo incremental: Importar apenas novos registros
•	Exportação de log: Salvar relatório da importação
•	Validação prévia: Validar arquivos antes de iniciar importação
•	Mapeamento flexível: Permitir ajustar nome de colunas se diferirem do padrão
Output Esperado
Após implementação, o sistema deve:
•	Processar todos os arquivos com sucesso
•	Apresentar relatório com quantidade de registros importados
•	Listar erros/avisos encontrados
•	Permitir reprocessamento de arquivos com erros corrigidos
•	Manter integridade referencial no banco de dados
Usar a BD existente


Quero que refaça a função para definir os permissos de um usuário para visualizar/editar as informações financeiras de outros usuários e as suas. Segundo os seguintes parâmetros: 
1 – A tela deve constar da seleção do usuário afetado.
2 – Deve permitir a escolha de múltiplos usuários e a ação(Visualizar/editar) sobre cada um deles.


1 - Um usuario pode ter perimisso de visualizar/editar as informações financeiras de outros usuários
2 – Ao visualizar essas permissões o sistema esta mostrando os ID dos usuários, deveria ser os nomes


Vamos fazer alguns câmbios na tela de Dashboard:
1 – Quero os seguintes cards:
	Receita Mensal
	Receita no Ano
	Variaçao da Receita com o Mês anterior
	Imoveis Disponiveis
2 – Todos os demais cards devem ser eliminados.
3 – Mantenha os gráficos:
	Receita por mês
	Status dos Imoveis
4 – Todos os demais gráficos devem ser eliminados
5 – Eliminar a tabela Alugueis recentes

