import ast, astunparse

class Visit(ast.NodeVisitor):
  def __init__(self):

    ast.NodeVisitor.__init__(self)
    self.s = set()
    # Имя для первой переменной
    self.name = 'a'
    self.assign = False # Флаг для изменения имени переменной в visit_Name
    self.subscript = False # Флаг для НЕ изменения имени переменной в visit_Name, если мы меняем значение в массиве
    # Английский алфавит, чтобы не плодить длинные имена из одинаковых букв
    self.alpha = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    self.ind = 0 # На какой букве алфавита находимся
    # Массив с контекстами для функций, глобальная область в self.hashes[0] (в массиве хранятся словари с названиями переменных)
    self.hashes = [dict()]
    self.ind_hash = 0 # На каком контексте находимся сейчас
    
    
  

  def visit_Name(self, node):
    '''
    Переопределенная функция из ast.NodeVisitor

    В этой функции будем менять названия.
    '''

    # Заменяем уже переименнованные названия переменных
    if node.id in self.hashes[self.ind_hash]:
      node.id = self.hashes[self.ind_hash][node.id]

    # Меняем название переменной
    if self.assign and not self.subscript:
      self.hashes[self.ind_hash][node.id] = self.name
      node.id = self.name
    self.assign = False
    self.subscript = False
    # Добавляем в общий словарь всех названий
    self.s.add(node.id)


  def generic_visit(self, node):
    # Если объявлена новая функция, добавляем новый контекст, связанный с этой функцией
    if type(node).__name__ == 'FunctionDef':
      self.hashes.append(self.hashes[0])
      self.ind_hash = len(self.hashes) - 1
    
    # Если просто меняем значения массива, не даем массиву новую переменную
    if type(node).__name__ == 'Subscript':
      self.subscript = True

    # Если видим, что вводится новая переменная, говорим, что её нужно поменять в visit_Name
    if type(node).__name__ == 'Assign':
      # Если длина нового имени уже больше 15, переходим на новую букву
      if len(self.name) >= 40:
        self.ind += 1
        self.name = self.alpha[self.ind]
      else:
        self.name += self.alpha[self.ind]
      self.assign = True
    # Если видим комментарий или docstring, убираем его.
    if type(node).__name__ == 'Expr':
      node.value = ast.Constant(value='', kind=None)
    ast.NodeVisitor.generic_visit(self, node)

def normalize_text(text):
    v = Visit()
    try:
        tree = ast.parse(text)
    except Exception as e: # Файл мог оказаться не компилируемым, в этом случае оставляем его без изменений.
        # print('Один из файлов не компилируется!')
        # print('Текст файла оставлен в прежнем виде.')
        return text
    v.visit(tree)
    return astunparse.unparse(tree)