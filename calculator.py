# write your code here

from string import ascii_letters
from collections import deque


class SyntacticalAnalyzer:
    """
    The name of a variable (identifier) can contain only Latin letters.
A variable can have a name consisting of more than one letter.
The case is also important; for example, n is not the same as N.
The value can be an integer number or a value of another variable.
Addition and subtraction operations are allowed.
Commands begin with a slash and can be: /exit and /help
    """
    _digits_tags: str = '1234567890'
    _commands = ['/exit', '/help']
    left_part: str = None
    expression_stack: list = []
    operator_priority: dict = {
        '(': 0,
        '+': 2,
        '-': 2,
        '*': 3,
        '/': 3,
        '^': 4,
        ')': 0
    }
    rpn_stack: deque = deque()

    @staticmethod
    def check_ascii(name):
        for letter in name:
            if letter not in ascii_letters:
                return False
        return True

    @property
    def checked_string(self) -> str:
        return self.__checked_string

    @checked_string.setter
    def checked_string(self, value: str):
        self.__checked_string = value

    @property
    def check_result(self):
        return self.res

    def __init__(self):
        self.__checked_string: str = ''
        self._state: str = 'assignment operator'
        # правила обхода цепочки проверок
        self.chain_rules: dict = dict(skip=False,
                                      off=False
                                      )
        # статус проверки
        self._status = dict(checker='',
                            error=None,
                            check_res=False,
                            )
        # объект, передаваемый в класс-обёртку
        self.res = dict(error=None,
                        state=None,
                        command=None,
                        left=None,
                        rpn_expression=None
                        )
        # список проверочных функций
        self._check_chain: list = [self.check_not_empty,
                                   self.check_command_tag,
                                   self.check_command_incorrectness,
                                   self.check_equality_tag,
                                   self.check_left_part,
                                   self.check_right_part,
                                   self.to_rpn
                                   ]

    def notify(self, checker: str, check_res: bool):
        """
        Передаёт в объект self._status имя функции и результат её работы
        @param checker: имя переданной функции
        @type checker: str
        @param check_res: результат работы переданной функции
        @type check_res: bool
        @return: None
        """
        self._status['checker'] = checker
        self._status['check_res'] = check_res

    def check_status_handler(self):
        """
        Считывает изменённый объект self._status, устанавливает self._state
        и изменяет объект self.chain_rules
        @return: None
        """

        if self._status['checker'] == 'check_not_empty' and not self._status['check_res']:
            self._status['error'] = 'empty'
            self._state = 'empty'
        if self._status['checker'] == 'check_command_tag':
            if self._status['check_res']:
                self._state = 'command'
            else:
                self.chain_rules['skip'] = True

        if self._status['checker'] == 'check_command_incorrectness':
            if not self._status['check_res']:
                self._status['error'] = self.add_command()
                self.chain_rules['off'] = True
            else:
                self.chain_rules['off'] = True
        if self._status['checker'] == 'check_equality_tag':
            if not self._status['check_res']:
                self._state = 'expression'
                self.chain_rules['skip'] = True

        if self._status['checker'] == 'check_left_part':
            if not self._status['check_res']:
                self._status['error'] = 'Invalid identifier'

        if self._status['checker'] == 'check_right_part':
            if not self._status['check_res']:
                if self._state == 'assignment operator':
                    self._status['error'] = 'Invalid assignment'
                    self.chain_rules['skip'] = True
                else:
                    self._status['error'] = 'Invalid identifier'
                    self.chain_rules['skip'] = True
        if self._status['checker'] == 'to_rpn':
            if not self._status['check_res']:
                if self._state == 'assignment operator':
                    self._status['error'] = 'Invalid assignment'
                else:
                    self._status['error'] = 'Invalid expression'

    def perform_res(self):
        """
        Проверяет self._state и self._status. Заполняет словарь self.res
        @return: None
        """
        self.res['state'] = self._state
        if self._state == 'empty':
            self.res['error'] = 'empty'
            self.chain_rules['off'] = True
        if self._state == 'command':
            if self._status['error'] is None:
                self.res['command'] = self.add_command()
            else:
                self.res['error'] = self._status['error']
        if self._state == 'assignment operator':
            if self._status['error'] is None:
                self.res['left'] = self.left_part
                self.res['rpn_expression'] = self.rpn_stack
            else:
                self.res['error'] = self._status['error']
        if self._state == 'expression':
            if self._status['error'] is None:
                self.res['rpn_expression'] = self.rpn_stack
            else:
                self.res['error'] = self._status['error']

    def clear_init_fields(self):
        """
        Очищает все поля конструктора перед проверкой новой строки
        @return: None
        """
        self._state = 'assignment operator'
        self._status['checker'] = ''
        self._status['error'] = None
        self._status['check_res'] = False
        self.chain_rules['skip'] = False
        self.chain_rules['off'] = False

        for key, value in self.res.items():
            if type(value) != dict:
                self.res[key] = None
        self.expression_stack = []

    def run_check_chain(self):
        """
        Запускает цепочку проверок строки. Читает объекты self.chain_rules и
        self._status, если свойство skip == True, пропускает следующую проверку,
        если свойство off == True или одна из проверок завершилась
        с ошибкой, завершает свою работу
        @return: None
        """
        j = -1
        self.clear_init_fields()

        for i, check in enumerate(self._check_chain):
            if j == i:
                self.chain_rules['skip'] = False
            if self.chain_rules['skip']:
                j = i + 1 if i + 1 < len(self._check_chain) else -1
                continue
            self.run_check(check)
            self.check_status_handler()
            if self._status['error'] is not None:
                break
            if self.chain_rules['off']:
                break
        self.perform_res()

    def run_check(self, check_func):
        """
        @type check_func: function
        """
        result = check_func()
        self.notify(check_func.__name__, result)

    def check_not_empty(self):
        return self.checked_string != ''

    def check_command_tag(self):
        return self.checked_string.startswith('/')

    def check_command_incorrectness(self):
        return self.checked_string in self._commands

    def add_command(self) -> str:
        for _command in self._commands:
            if self.checked_string == _command:
                return _command
        return 'Unknown command'

    def check_equality_tag(self) -> bool:
        return '=' in self.checked_string

    def is_variable(self, name: str) -> bool:
        return all([len(name) >= 1, self.check_ascii(name)])

    def check_left_part(self):
        if self._state == 'assignment operator':
            self.left_part = self.checked_string.split('=')[0].strip()
            return self.is_variable(self.left_part)

    @staticmethod
    def get_fragment_params(value: str, end):
        out_str = ''
        pos = 0
        sym = value[0]
        while sym not in end:
            out_str += sym
            try:
                pos += 1
                sym = value[pos]
            except IndexError:
                return out_str, None
        return out_str, pos

    @staticmethod
    def is_operator(item: str):
        item_list: list = item.strip().split(' ')
        my_str = ''.join(item_list)
        if my_str[0] in '+-':
            for el in my_str:
                if el not in '+-':
                    return False
        if my_str[0] in '/*^':
            if len(my_str) > 1:
                return False
        return True

    @staticmethod
    def is_digit(item: str):
        if item[0] == '0':
            if len(item) != 1:
                return False
            return True
        for el in item:
            if el not in '1234567890':
                return False
        return True

    @staticmethod
    def is_left_parenthesis(item: str):
        for el in item:
            if el not in '(':
                return False
        return True

    @staticmethod
    def is_right_parenthesis(item: str):
        for el in item:
            if el not in ')':
                return False
        return True

    @staticmethod
    def get_first(value: str):
        return value[0] if value else None

    @staticmethod
    def get_tag(letter: str):
        if letter in ascii_letters:
            return 'variable'
        if letter in '-+/*^':
            return 'operator'
        if letter in '1234567890':
            return 'digit'
        if letter in '()':
            return 'left parenthesis' if letter == '(' else 'right parenthesis'

    @staticmethod
    def get_end_tag(tag: str) -> str:
        if tag == 'variable':
            return ' )+-/*^'
        if tag == 'operator':
            return '(0123456789' + ascii_letters
        if tag == 'digit':
            return ' )+-/*^'
        if tag == 'left parenthesis':
            return ' 0123456789' + ascii_letters + '+-'
        if tag == 'right parenthesis':
            return ' +-/*^'

    @staticmethod
    def transform_operator(el: str):
        if '-' in el or '+' in el:
            minus_cnt = el.count('-')
            if minus_cnt:
                return '-' if minus_cnt % 2 != 0 else '+'
            return '+'
        return el

    @staticmethod
    def transform_parenthesis(el: str):
        return list(el)

    def transform_element(self, el: str, tag: str):
        if tag == 'operator':
            return self.transform_operator(el)
        if tag in ['left parenthesis', 'right parenthesis']:
            return self.transform_parenthesis(el.rstrip())
        return el.rstrip()

    @staticmethod
    def add_el(container: list, el):
        if type(el) == list:
            container += el
        else:
            container.append(el.rstrip())

    def check_right_part(self):
        next_pos = 0
        if self._state == 'assignment operator':
            input_str = self.checked_string.split('=', 1)[1].strip()
        else:
            input_str = self.checked_string.strip()
        if not input_str:
            return False
        while True:
            current: str = input_str[next_pos:]
            sym: str = self.get_first(current)
            name = self.get_tag(sym)
            end_tag = self.get_end_tag(name)
            el, offset = self.get_fragment_params(value=current, end=end_tag)

            conditions = [
                self.is_variable(el),
                self.is_operator(el),
                self.is_digit(el),
                self.is_left_parenthesis(el),
                self.is_right_parenthesis(el)
            ]
            if not any(conditions):
                return False
            el = self.transform_element(el=el, tag=name)
            if not self.expression_stack or self.expression_stack[-1] == '(':
                if el in '+-':
                    self.expression_stack.append('0')
            self.add_el(self.expression_stack, el)
            if offset is None:
                return True
            temp = current[offset:]
            offset += temp.find(temp.lstrip())
            next_pos += offset

    def to_rpn(self):
        f = False
        operators: list = []
        for item in self.expression_stack:
            if self.is_digit(item) or self.is_variable(item):
                self.rpn_stack.append(item)
            else:
                if not operators:
                    operators.append(item)
                else:
                    if item == '(' or self.operator_priority[item] > self.operator_priority[operators[-1]]:
                        operators.append(item)
                    else:
                        if not operators:
                            return False
                        while operators:
                            operator = operators.pop()
                            if operator == '(':
                                f = True
                                break
                            self.rpn_stack.append(operator)
                        if item == ')' and not f:
                            return False
                        if item != ')':
                            operators.append(item)

        if operators:
            if '(' in operators:
                return False
            else:
                while operators:
                    self.rpn_stack.append(operators.pop())
        return True

    # End of class SyntacticalAnalyzer


class Interpreter:
    bye_string = 'Bye!'
    help_string = 'The program calculates expressions using addition, subtraction, multiplication, integer division' \
                  ' and exponentiation over a set of integers, and also uses variables.'

    def __init__(self, obj):
        self.variables: dict = {}
        self.obj = obj
        self.error: str = None
        self.res: int = None
        self.rpn_stack: deque = deque()

    def execute(self):
        if not self.analysis_handler():
            return False
        return True

    def analysis_handler(self):
        """
        Читает self.obj.
        @return:
        """
        self.rpn_stack = deque()
        self.res = None
        self.error = None
        if self.obj['state'] == 'empty':
            pass
        if self.obj['state'] == 'command':
            if not self.command_handler(self.obj['command']):
                return False
        if self.obj['state'] == 'expression':
            if not self.expression_handler():
                print(self.error)
            else:
                print(self.res)

        if self.obj['state'] == 'assignment operator':
            if not self.assignment_handler():
                print(self.error)
        return True

    def command_handler(self, param: str) -> bool:
        if param == '/exit':
            print(self.bye_string)
            return False
        if param == '/help':
            print(self.help_string)
            return True

    def expression_handler(self):
        if not self.check_variables():
            return False
        self.res = self.get_expression_result()
        return True

    @staticmethod
    def calculate_this(one, two, sign):
        one, two = [int(x) for x in [one, two]]
        if sign == '+':
            return one + two
        if sign == '-':
            return one - two
        if sign == '*':
            return one * two
        if sign == '/':
            return one // two
        if sign == '^':
            return one ** two

        def get_expression_result(self):
        result_stack: list = []

        while self.rpn_stack:
            item = self.rpn_stack.popleft()
            try:
                result_stack.append(int(item))
            except ValueError:
                second, first = result_stack.pop(), result_stack.pop()
                result_stack.append(self.calculate_this(first, second, item))

        return result_stack[0]

    def assignment_handler(self):
        if not self.expression_handler():
            return False
        left = self.obj['left']
        self.variables[left] = self.res
        return True

    def check_variables(self):
        self.rpn_stack = self.obj['rpn_expression']
        for i, item in enumerate(self.rpn_stack):
            if item in self.variables:
                self.rpn_stack[i] = self.variables[item]
            else:
                if item[0] in ascii_letters:
                    return False
        return True


class SmartCalculator:
    """
    The name of a variable (identifier) can contain only Latin letters.
A variable can have a name consisting of more than one letter.
The case is also important; for example, n is not the same as N.
The value can be an integer number or a value of another variable.
It should be possible to set a new value to an existing variable.
To print the value of a variable you should just type its name.
    """
    _analyzer_methods = ['run_check_chain']
    _interpreter_methods = ['execute', 'analysis_handler']

    def __init__(self):
        self._analyzer: SyntacticalAnalyzer = SyntacticalAnalyzer()
        self.analyzer_result: dict = self._analyzer.check_result
        self._interpreter: Interpreter = Interpreter(self.analyzer_result)

    def __getattr__(self, item):
        for item in self._analyzer_methods + self._interpreter_methods:
            if item in self._analyzer_methods:
                return getattr(self._analyzer, item)
            if item in self._interpreter_methods:
                return getattr(self._interpreter, item)

    def run(self):
        while True:
            self._analyzer.checked_string = input().strip()
            self._analyzer.run_check_chain()
            if self._analyzer.res['error'] is not None and self._analyzer.res['error'] != 'empty':
                print(self._analyzer.res['error'])
            else:
                if not self._interpreter.execute():
                    return None


calculator = SmartCalculator()
calculator.run()
