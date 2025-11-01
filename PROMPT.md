Quero criar una página web para um sistema de alugueis. Em Python e Java.
Ela deve ter as seguintes paginas:
1 – Login.
2 – Um menu persistente com as rotas para as demais paginas.
3 – Dashboard:
	Deve mostrar os seguintes dados: Renda do mês(ultimo mês da BD), Renda acumulada do ano vigente(de janeiro ao ultimo mês da BD), variação percentual do ultimo mês e o anterior, numero de imóveis disponíveis. Um gráfico com os valores dos alugueis mês a mês do ultimo ano da BD e um gráfico com o numero de imóveis disponíveis e alugados.
4 – Proprietarios:
	Deve mostrar uma tabela com os dados de todos os proprietários cadastrados na BD. Esta tabela de ter um formato exportável a excel.
	Deve ter um botão para cadastrar um novo proprietário, se abre uma nova linha na tabela com os demais priprietarios(como uma linha nova de uma tabela de excel), deve terá a dois botões de ações para editar e excluir um proprietário.
4 – Proprietarios:
	Deve mostrar uma tabela com os dados de todos os proprietários cadastrados na BD. Esta tabela de ter um formato exportável a excel.
	Deve ter um botão para cadastrar um novo proprietário, se abre uma nova linha na tabela com os demais proprietários (como uma linha nova de uma tabela de excel), deve terá a dois botões de ações para editar e excluir um proprietário.
5 – Imoveis:
	Deve mostrar uma tabela com os dados de todos os imoveis cadastrados na BD. Esta tabela de ter um formato exportável a excel.
	Deve ter um botão para cadastrar um novo imovel, se abre uma nova linha na tabela com os demais imóveis (como uma linha nova de uma tabela de excel), deve terá a dois botões de ações para editar e excluir um imovel.
6 – Participaçoes:
	Deve ter um combo para selecionar que conjunto de participações mostrar, por padrão mostra o ultimo conjunto cadastrado.
	Deve mostrar uma tabela com os dados do ultimo conjunto de participações cadastradas na BD. Esta tabela de ter um formato exportável a excel.
	A tabela de participações deve ter  o seguinte formato:
	Prop. 1	Prop. 2	...	Prop. N
Imovel 1	Partic(I1,P1)	Partic(I1,P2)	...	Partic(I1,Pn)
Imovel 2	Partic(I2,P1)	Partic(I2,P2)	...	Partic(I2,Pn)
Imovel n	Partic(In,P1)	Partic(In,P2)	...	Partic(In,Pn)
	Deve ter um botão de açao para editar as participações de um imóvel.
7 – Alugueis:
	Deve ter um combo para selecionar o ano e outro para o mês do conjuntos de alugueis que se deve mostrar , por padrão deve mostra o ultimo conjunto cadastrado ou seja do ultimo ano cadastrado e do ultimo mês cadastrado.
A tabela de algueis deve ter  o seguinte formato:
	Prop. 1	Prop. 2	...	Prop. N
Imovel 1	Aluguel(I1,P1)	Aluguel(I1,P2)	...	Aluguel(I1,Pn)
Imovel 2	Aluguel(I2,P1)	Aluguel(I2,P2)	...	Aluguel(I2,Pn)
Imovel n	Aluguel(In,P1)	Aluguel(In,P2)	...	Aluguel(In,Pn)

8 – Relatorios
	Deve ter um combo para selecionar o ano, outro para o mês e outro para os proprietarios do conjuntos de alugueis e Darfs que se deve mostrar , por padrão deve mostra o ultimo conjunto cadastrado ou seja do ultimo ano cadastrado e do ultimo mês cadastrado de todos os proprietarios.
A tabela deve ter este formato:
Proprietario	Periodo	Aluguel	Darf	Aluguel – Darf
Prop.1	10/2025	Aluguel(P1,mm/aaaa)	Darf(P1,mm/aaaa)	Al-D
Prop.2	mm/aaaa	Aluguel(P2,mm/aaaa)	Darf(P2,mm/aaaa)	Al-D
Prop.n	mm/aaaa	Aluguel(Pn,mm/aaaa)	Darf(Pn,mm/aaaa)	Al-D

9 – Extra
10 – DARF
11 – Importar

