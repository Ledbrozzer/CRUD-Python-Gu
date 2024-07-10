#Aplicativo TO-DO criado com Flet.
#Algumas notas:
 #   1. Este é um aplicativo completo => UI + função de banco de dados
  #  2. Vídeo ligeiramente mais longo, mas com mais explicações
   # 3. O banco de dados é local com sqlite3
#"""

# módulos
import flet
from flet import *
from datetime import datetime
import sqlite3

# Ok, então a parte da UI está pronta, agora para a parte final, podemos implementar um banco de dados para armazenar as tarefas
# podemos criar uma classe para isso
class Database:
    def ConnectToDatabase():
        try:
            db = sqlite3.connect("todo.db")
            c = db.cursor()
            c.execute('CREATE TABLE if not exists tasks (id INTEGER PRIMARY KEY, Task VARCHAR(255) NOT NULL, Date VARCHAR(255) NOT NULL)')
            return db
        except Exception as e:
            print(e)
            return None

    def ReadDatabase(db):
        c = db.cursor()
        # certifique-se de nomear as colunas e não usar SELECT * FROM...
        c.execute("SELECT Task, Date FROM tasks")
        records = c.fetchall()
        return records

    def InsertDatabase(db, values):
        c = db.cursor()
        # também certifique-se de usar ? para as entradas por motivos de segurança
        c.execute("INSERT INTO tasks (Task, Date) VALUES (?,?)", values)
        db.commit()

    def DeleteDatabase(db, value):
        c = db.cursor()
        # nota rápida: aqui estamos assumindo que não há duas descrições de tarefas iguais e, como resultado, estamos excluindo com base na tarefa.
        # um aplicativo ideal não faria isso, mas excluiria com base no ID imutável do banco de dados. mas para o propósito do tutorial e da duração, faremos dessa maneira...
        c.execute("DELETE FROM tasks WHERE Task=?", value)
        db.commit()

    def UpdateDatabase(db, values):
        c = db.cursor()
        c.execute("UPDATE tasks SET Task=? WHERE Task=?", values)
        db.commit()

# agora que temos todas as funções CRUD, podemos começar a usá-las com o aplicativo...

# Vamos criar a classe do formulário primeiro para que possamos obter alguns dados
class FormContainer(UserControl):
    # neste ponto, podemos passar uma função do main() para expandir/minimizar o formulário
    def __init__(self, func):
        self.func = func
        super().__init__()

    def build(self):
        return Container(
            width=280,
            height=80,
            bgcolor="bluegrey500",
            opacity=0, # mudar mais tarde => altere isso para 0 e reverta quando chamado
            border_radius=40,
            margin=margin.only(left=-20, right=-20),
            animate=animation.Animation(400, "decelerate"),
            animate_opacity=200,
            padding=padding.only(top=45, bottom=45),
            content=Column(
                horizontal_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    TextField(
                        height=48,
                        width=255,
                        filled=True,
                        text_size=12,
                        color="black",
                        border_color="transparent",
                        hint_text="Descrição...",
                        hint_style=TextStyle(size=11, color="black"),
                    ),
                    IconButton(
                        content=Text("Adicionar Tarefa"),
                        width=180,
                        height=44,
                        on_click=self.func, # passar função aqui
                        style=ButtonStyle(
                            bgcolor={"": 'black'},
                            shape={
                                "": RoundedRectangleBorder(radius=8),
                            },
                        ),
                    ),
                ],
            ),
        )

# Agora, precisamos de uma classe para gerar uma tarefa quando o usuário adicionar uma
class CreateTask(UserControl):
    def __init__(self, task: str, date: str, func1, func2):
        # criar dois argumentos para podermos passar a função de excluir e a função de editar quando criarmos uma instância disso
        self.task = task
        self.date = date
        self.func1 = func1
        self.func2 = func2
        super().__init__()

    def TaskDeleteEdit(self, name, color, func):
        return IconButton(
            icon=name,
            width=30,
            icon_size=18,
            icon_color=color,
            opacity=0,
            animate_opacity=200,
            # para usá-lo, precisamos mantê-lo em nossos iconbuttons de exclusão e edição
            on_click=lambda e: func(self.GetContainerInstance())
        )

    # precisamos de uma última coisa aqui, e essa é a própria instância.
    # precisamos do identificador da instância para que possamos excluir quando necessário
    def GetContainerInstance(self):
        return self # retornamos a própria instância

    def ShowIcons(self, e):
        if e.data == "true":
            # estes são os índices de cada ícone
            (
                e.control.content.controls[1].controls[0].opacity,
                e.control.content.controls[1].controls[1].opacity,
            ) = (1, 1)
            e.control.content.update()
        else:
            (
                e.control.content.controls[1].controls[0].opacity,
                e.control.content.controls[1].controls[1].opacity,
            ) = (0, 0)
            e.control.content.update()

    def build(self):
        return Container(
            width=280,
            height=60,
            border=border.all(0.85, "white54"),
            border_radius=8,
            # vamos mostrar os ícones quando passarmos o mouse sobre eles...
            on_hover=lambda e: self.ShowIcons(e),
            clip_behavior=ClipBehavior.HARD_EDGE,
            padding=10,
            content=Row(
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    Column(
                        spacing=1,
                        alignment=MainAxisAlignment.CENTER,
                        controls=[
                            Text(value=self.task, size=10),
                            Text(value=self.date, size=9, color="white54"),
                        ],
                    ),
                    # Ícones de Excluir e Editar
                    Row(
                        spacing=0,
                        alignment=MainAxisAlignment.CENTER,
                        controls=[
                            # certifique-se de passar os argumentos aqui primeiro!!
                            self.TaskDeleteEdit(icons.DELETE_ROUNDED, "red500", self.func1),
                            self.TaskDeleteEdit(icons.EDIT_ROUNDED, "white70", self.func2),
                        ],
                    ),
                ],
            ),
        )

def main(page: Page):
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    def AddTaskScreen(e):
        # agora, toda vez que o usuário adicionar uma tarefa, precisamos buscar os dados e exibí-los na coluna principal...
        # há 2 dados que precisamos: a tarefa + a data
        dateTime = datetime.now().strftime("%b %d, %Y %I:%M")

        # podemos usar o db aqui para começar...
        # primeiro, abrir uma conexão com o banco de dados
        db = Database.ConnectToDatabase() # isso retorna o db
        Database.InsertDatabase(db, (form.content.controls[0].value, dateTime))
        # temos ambos os valores, uma a data e hora e outra a tarefa do usuário
        # finalmente feche a conexão
        db.close()

        # também poderíamos colocar as funções db dentro da declaração if...

        # agora lembre-se que definimos o contêiner do formulário como variável form. podemos usar isso agora para ver se há algum conteúdo no campo de texto
        if form.content.controls[0].value: # isso verifica o valor do campo de texto
            _main_column_.controls.append(
                # aqui, podemos criar uma instância da classe CreateTask...
                CreateTask(
                    # agora, leva dois argumentos
                    form.content.controls[0].value, # descrição da tarefa...
                    dateTime,
                    # agora, a instância leva mais dois argumentos quando chamada...
                    DeleteFunction,
                    UpdateFunction,
                ),
            )
            _main_column_.update()

            # podemos lembrar da função de mostrar/ocultar o formulário aqui
            CreateToDoTask(e)
        else:
            db.close() # certifique-se de que fecha mesmo que não haja entrada do usuário
            pass

    def DeleteFunction(e):
        # agora a exclusão da tarefa dentro do BD
        db = Database.ConnectToDatabase()
        Database.DeleteDatabase(
            db, (e.controls[0].content.controls[0].controls[0].value,)
        )
        # o e.control... é o valor da própria instância.
        # passamos como (valor), porque precisa ser do tipo de dado tupla
        db.close()
        # exclusão funcionando!

        # quando queremos excluir, lembre-se de que essas instâncias estão em uma lista => isso significa que podemos simplesmente removê-las quando quisermos
        # vamos mostrar o que é e...
        # então a instância é passada como e
        _main_column_.controls.remove(e) # e é a própria instância
        _main_column_.update()

    def UpdateFunction(e):
        # a atualização é um pouco mais complicada...
        # queremos atualizar a partir do formulário, então precisamos passar o que o usuário tinha da instância de volta para o formulário, depois mudar as funções e passar de volta novamente...
        form.height, form.opacity = 200, 1 # mostrar o formulário
        (
            form.content.controls[0].value,
            form.content.controls[1].content.value,
            form.content.controls[1].on_click,
        ) = (
            e.controls[0].content.controls[0].controls[0].value,
            "Atualizar",
            lambda ev: FinalizeUpdate(ev, e),
        )
        form.update()

        # depois que o usuário editar, precisamos enviar os dados corretos de volta

    def FinalizeUpdate(ev, task_instance):
        # agora finalmente, podemos atualizar o banco de dados também
        db = Database.ConnectToDatabase()
        Database.UpdateDatabase(
            db,
            (
                form.content.controls[0].value,
                task_instance.controls[0].content.controls[0].controls[0].value,
            ),
        )
        db.close()

        # Podemos simplesmente reverter o valor de cima...
        task_instance.controls[0].content.controls[0].controls[0].value = form.content.controls[0].value
        task_instance.controls[0].content.update()
        # Para que possamos esconder o contêiner...
        CreateToDoTask(ev)

    # função para mostrar/ocultar o contêiner do formulário
    def CreateToDoTask(e):
        # quando clicamos no ícone de botão ADD...
        if form.height != 200:
            form.height, form.opacity = 200, 1
            form.update()
        else:
            form.height, form.opacity = 80, 0
            # também podemos remover os valores do campo de texto...
            form.content.controls[0].value = None
            form.content.controls[1].content.value = "Adicionar Texto"
            form.content.controls[1].on_click = lambda ev: AddTaskScreen(ev)
            form.update()

    _main_column_ = Column(
        scroll='hidden',
        expand=True,
        alignment=MainAxisAlignment.START,
        controls=[
            Row(
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    # Alguns elementos de título...
                    Text("Itens a Fazer", size=18, weight="bold"),
                    IconButton(
                        icons.ADD_CIRCLE_ROUNDED,
                        icon_size=18,
                        on_click=lambda e: CreateToDoTask(e),
                    ),
                ],
            ),
            Divider(height=8, color="white24")
        ],
    )

    # configurar um fundo e contêiner principal
    # A UI geral copiará a de um aplicativo móvel
    page.add(
        # este é apenas um contêiner de fundo
        Container(
            width=1500,
            height=800,
            margin=-10,
            bgcolor="bluegrey900",
            alignment=alignment.center,
            content=Row(
                alignment=MainAxisAlignment.CENTER,
                vertical_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    # Contêiner principal
                    Container(
                        width=280,
                        height=600,
                        bgcolor="#0f0f0f",
                        border_radius=40,
                        border=border.all(0.5, "white"),
                        padding=padding.only(top=35, left=20, right=20),
                        clip_behavior=ClipBehavior.HARD_EDGE, # recortar conteúdos ao contêiner
                        content=Column(
                            alignment=MainAxisAlignment.CENTER,
                            expand=True,
                            controls=[
                                # Coluna principal aqui...
                                _main_column_,
                                # Classe do formulário aqui...
                                # passar o argumento para a classe do formulário aqui
                                FormContainer(lambda e: AddTaskScreen(e)),
                            ],
                        ),
                    )
                ],
            ),
        )
    )
    page.update()

    # o índice do contêiner do formulário é o seguinte. Podemos definir o índice do elemento longo como uma variável para que possa ser chamado de forma mais rápida e fácil.
    form = page.controls[0].content.controls[0].content.controls[1].controls[0]
    # agora podemos chamar form sempre que quisermos fazer algo com ele...

    # agora, para exibi-lo, precisamos ler o banco de dados
    # outra nota: Flet continua atualizando quando chamamos as funções do banco de dados, isso pode ser do meu código ou do próprio Flet, mas deve ser resolvido...
    # abrir conexão
    db = Database.ConnectToDatabase()
    # agora lembre-se de que a função ReadDatabase() retorna os registros...
    # nota: o retorno é do tipo de dado tupla!!
    # nota: podemos querer exibir os registros em ordem inversa, ou seja, os novos registros primeiro, seguidos pelos mais antigos...
    # usar [::-1] inverte a tupla.
    # usar [:-1] inverte uma lista.
    for task in Database.ReadDatabase(db)[::-1]:
        # vamos ver se as tarefas estão sendo salvas...
        # vamos adicioná-las à tela agora
        _main_column_.controls.append(
            # mesmo processo de antes: criamos uma instância desta classe...
            CreateTask(
                task[0], # primeiro item da tupla retornada
                task[1],
                DeleteFunction,
                UpdateFunction
            )
        )
    _main_column_.update()

if __name__ == "__main__":
    flet.app(target=main)

# então outras mudanças podem ser feitas, mas as fundações estão funcionando bem...
#C:\Users\josem\AppData\Roaming\Python\Python312\Scripts\normalizer.exe
#echo %PATH%