# ATIVIDADE PRÁTICA - reconhecedor de estruturas em C
from ply import *
import logging

class ErroSemantico(Exception):
    """Exceção para erros semânticos durante a análise"""
    def __init__(self, mensagem):
        self.mensagem = mensagem
        super().__init__(self.mensagem)

def verificar_variavel_redeclarada(nome_var, linha=0):
    """Verifica se uma variável já foi declarada e lança exceção se for o caso"""
    if nome_var in simbolos:
        #return True
        raise ErroSemantico(f"Erro semântico na linha {linha}: variável '{nome_var}' já declarada")
    return False

def verificar_variavel_usada(nome_var, linha=0):
    """Verifica se uma variável foi declarada antes de ser usada"""
    if nome_var not in simbolos:
        raise ErroSemantico(f"Erro semântico na linha {linha}: variável '{nome_var}' usada mas não declarada")
    return True



contexto = 0

def get_contexto():
    return contexto

# Tabela de simbolos
# {ID {valor, tipo, contexto}}
simbolos = {}

# Palavras reservadas <palavra>:<TOKEN>
reserved = {
    'if' : 'IF',
    'else' : 'ELSE',
    'int' : 'INT',
    'float' : 'FLOAT',
    'char': 'CHAR',
    'for': 'FOR',
    'while':'WHILE',
    'main': 'MAIN',
    'return': 'RETURN'
}

# Demais TOKENS
tokens = [
    'EQUALS', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POWER',
    'LPAREN', 'RPAREN', 'LT', 'LE', 'GT', 'GE', 'NE',
    'COMMA', 'SEMI', 'INTEGER', 'FLOATN', 'STRING',
    'ID', 'SEMICOLON', 'RBRACES', 'LBRACES'
] + list(reserved.values())

t_ignore = ' \t\n'

def t_REM(t):
    r'REM .*'
    return t

# Definição de Identificador com expressão regular r'<expressão>'
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t

t_EQUALS = r'='
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_POWER = r'\^'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_RBRACES = r'\}'
t_LBRACES = r'\{'
t_SEMICOLON = r'\;'
t_LT = r'<'
t_LE = r'<='
t_GT = r'>'
t_GE = r'>='
t_NE = r'!='
t_COMMA = r'\,'
t_SEMI = r';'
t_INTEGER = r'\d+'
t_FLOATN = r'((\d*\.\d+)(E[\+-]?\d+)?|([1-9]\d*E[\+-]?\d+))'
t_STRING = r'\".*?\"'

def t_error(t):
    print("Illegal character %s" % t.value[0])
    t.lexer.skip(1)

# Constroi o analisador léxico
lexer = lex.lex()
    
# Define-se os procedimentos associados as regras de
# produção da gramática (também é quando definimos a gramática)

#def p_<nome>(p):
#    '<não_terminal> : <TERMINAIS> <nao_terminais> ... ' 
#    <ações semânticas>
# -> ''' para regras com |

def p_inicial(p):
    '''inicial : INT MAIN LPAREN RPAREN bloco_principal SEMICOLON'''
    print("Reconheci INICIAL")
    print("\n=== Compilação concluída com sucesso ===")
    print("\nTabela de Símbolos:")
    for var, info in simbolos.items():
        print(f"  {var}: {info}")
    print("\n=== Fim da compilação ===")

def p_bloco_principal(p):
    '''bloco_principal : LBRACES corpo RBRACES'''
#    print("Reconheci Bloco Principal")
    
def p_corpo(p):
    '''corpo : comando corpo
             | comando'''
#    print("Reconheci corpo")

def p_comando(p):
    '''comando : declaracoes
               | bloco_while
               | bloco_if
               | bloco_for
               | expressao'''
#    print("Reconheci comando")

def p_expressao(p):
    '''expressao : atribuicao'''
#    print("Reconheci bloco expressao")

def p_declaracoes(p):
    '''declaracoes : tipos ID SEMICOLON 
                | tipos declaracoes_linha SEMICOLON
                | tipos ID EQUALS values SEMICOLON
                | tipos ID EQUALS ID SEMICOLON
                | tipos ID EQUALS operacao_aritmetica SEMICOLON
                | tipos ID SEMICOLON declaracoes
                | tipos declaracoes_linha SEMICOLON declaracoes
                | tipos ID EQUALS values SEMICOLON declaracoes
                | tipos ID EQUALS ID SEMICOLON declaracoes
                | tipos ID EQUALS operacao_aritmetica SEMICOLON declaracoes'''
    # Armazena o tipo para uso posterior
    print("Entrou no bloco de declaracoes")
    tipo = p[1]
    
    # Caso de declaração com múltiplas variáveis (tipos declaracoes_linha SEMICOLON)
    if len(p) >= 3 and p[2] is None:
        print(simbolos.keys())
        print(simbolos.items())
        for chave, valor in simbolos.items():
            # Verificando se o atributo em_linha é True
            if valor.get('em_linha') == True:
                # Atualizando o atributo tipo
                simbolos[chave]['tipo'] = tipo
                print(f"Atualizado tipo da variável '{chave}' para '{tipo}'")
        print('Declaracao realizada em linha')
    
    # Caso de declaração simples (tipos ID SEMICOLON)
    elif len(p) >= 3 and p[3] == ";": # Abordagem disfuncional uma vez que isinstance sempre retorna True, ja que todos os termos sao strings - realizar testes
        try:
            verificar_variavel_redeclarada(p[2], p.lineno(2))
            simbolos[p[2]] = {'valor': None, 'tipo': tipo, 'contexto': get_contexto(), 'em_linha': False}
            print(f"Declarada variável '{p[2]}' do tipo '{tipo}'")
        except ErroSemantico as e:
            # Cria um token de erro com a mensagem
            error_token = yacc.YaccSymbol()
            error_token.type = 'ERROR'
            error_token.value = 'error'
            error_token.error_message = str(e)
            
            # Substitui o token atual pelo token de erro
            p_error(error_token)
            
            # Interrompe o parsing
            raise SyntaxError("Parsing interrompido devido a erro semântico")
    
    # Caso de declaração com inicialização
    elif len(p) >= 5 and p[3] == '=':
        try:
            verificar_variavel_redeclarada(p[2], p.lineno(2))
            #verificar_tipo_token(p[4], lexer)
            print(f"p[4]: '{p.slice[4].value}' - '{p[4]}'")
            if p.slice[4].type == 'ID':
                verificar_variavel_usada(p[4], p.lineno(4))

            if p.slice[4].type == 'values':
                # Idealmente, checar compatibilidade entre 'tipo_declarado' e o tipo do literal
                print("Verificando tipo de literal:", p.slice[4].value)
            if p.slice[4].type == 'operacao_aritmetica':
                # Idealmente, checar compatibilidade entre 'tipo_declarado' e o resultado da operação
                print("Verificando tipo de literal:", p.slice[4].value)

            valor = p[4]
            simbolos[p[2]] = {'valor': valor, 'tipo': tipo, 'contexto': get_contexto(), 'em_linha': False}
            print(f"Declarada e inicializada variável '{p[2]}' do tipo '{tipo}' com valor '{valor}'")
        except ErroSemantico as e:
            # Cria um token de erro com a mensagem
            error_token = yacc.YaccSymbol()
            error_token.type = 'ERROR'
            error_token.value = 'error'
            error_token.error_message = str(e)
            
            # Substitui o token atual pelo token de erro
            p_error(error_token)
            
            # Interrompe o parsing
            raise SyntaxError("Parsing interrompido devido a erro semântico")
            
    print(f"Reconheci Declarações {tipo} {p[2] if isinstance(p[2], str) else ''} {p[3]}")

def p_declaracao_linha(p):
    '''declaracoes_linha : ID COMMA declaracoes_linha
                        | ID'''

    try:
        verificar_variavel_redeclarada(p[1], p.lineno(1))
        simbolos[p[1]] = {'valor': None, 'tipo': None, 'contexto': get_contexto(), 'em_linha': True}
        print(f"Declarada variável '{p[1]}'")
    except ErroSemantico as e:
        # Cria um token de erro com a mensagem
        error_token = yacc.YaccSymbol()
        error_token.type = 'ERROR'
        error_token.value = 'error'
        error_token.error_message = str(e)
        
        # Substitui o token atual pelo token de erro
        p_error(error_token)
        
        # Interrompe o parsing
        raise SyntaxError("Parsing interrompido devido a erro semântico")

    
    # Propaga os IDs para o nó pai
    if len(p) > 2:
        p[0] = None  # Sinaliza que é uma declaração em linha
    else:
        p[0] = None  # Sinaliza que é uma declaração em linha
    
    print(f"Reconheci Declarações linha {p[1]}")

def p_bloco_while(p):
    '''bloco_while : WHILE LPAREN condicao RPAREN LBRACES corpo RBRACES'''
#    print("Reconheci bloco while")

def p_bloco_if(p):
    '''bloco_if : IF LPAREN condicao RPAREN LBRACES corpo RBRACES
                | IF LPAREN condicao RPAREN LBRACES corpo RBRACES ELSE LBRACES corpo RBRACES
                | IF LPAREN condicao RPAREN LBRACES corpo RBRACES ELSE bloco_if'''
#                | IF LPAREN condicao RPAREN LBRACES corpo RBRACES ELSE IF LPAREN condicao RPAREN LBRACES corpo RBRACES
#                | IF LPAREN condicao RPAREN LBRACES corpo RBRACES ELSE IF LPAREN condicao RPAREN LBRACES corpo RBRACES ELSE LBRACES corpo RBRACES'''
#    print("Reconheci bloco if")

def p_bloco_for(p):
    '''bloco_for : FOR LPAREN condicao_for RPAREN LBRACES corpo RBRACES'''
#    print("Reconheci bloco bloco_for")

def p_condicao_for(p):
    '''condicao_for : tipos ID EQUALS values SEMICOLON ID operadores_comparativos values SEMICOLON ID PLUS PLUS
                    | tipos ID EQUALS values SEMICOLON ID operadores_comparativos ID SEMICOLON ID PLUS PLUS
                    | ID EQUALS values SEMICOLON ID operadores_comparativos values SEMICOLON ID PLUS PLUS
                    | ID EQUALS values SEMICOLON ID operadores_comparativos ID SEMICOLON ID PLUS PLUS
                    | tipos ID EQUALS values SEMICOLON ID operadores_comparativos values SEMICOLON ID MINUS MINUS
                    | tipos ID EQUALS values SEMICOLON ID operadores_comparativos ID SEMICOLON ID MINUS MINUS
                    | ID EQUALS values SEMICOLON ID operadores_comparativos values SEMICOLON ID MINUS MINUS
                    | ID EQUALS values SEMICOLON ID operadores_comparativos ID SEMICOLON ID MINUS MINUS'''
#    print("Reconheci bloco condicao_for")

def p_atribuicao(p):
    ''' atribuicao : ID EQUALS values SEMICOLON
                | ID EQUALS ID SEMICOLON
                | ID EQUALS operacao_aritmetica SEMICOLON'''
    
    print("Entrou no bloco de atribuicoes")
    try:
        verificar_variavel_usada(p[1], p.lineno(1))
        if len(p) >= 4:
            if p.slice[3].type == 'ID':
                verificar_variavel_usada(p[3], p.lineno(3))
            if p.slice[3].type == 'values':
                print("Verificando tipo de literal:", p.slice[3].value)
            if p.slice[3].type == 'operacao_aritmetica':
                print("Verificando tipo de literal:", p.slice[3].value)
            # Atribui o valor à variável
            valor = p[3]
            simbolos[p[1]]['valor'] = valor
    except ErroSemantico as e:
        # Cria um token de erro com a mensagem
        error_token = yacc.YaccSymbol()
        error_token.type = 'ERROR'
        error_token.value = 'error'
        error_token.error_message = str(e)
        
        # Substitui o token atual pelo token de erro
        p_error(error_token)
        
        # Interrompe o parsing
        raise SyntaxError("Parsing interrompido devido a erro semântico")
    print("Reconheci bloco atribuicao", p[1], p[2])

# | tipos ID EQUALS values SEMICOLON
# | tipos ID EQUALS ID SEMICOLON
# | tipos ID EQUALS operacao_aritmetica SEMICOLON - adicionar as declaracoes

def p_operacao_aritmetica(p):
    ''' operacao_aritmetica : ID operadores_aritmeticos ID
                    | ID operadores_aritmeticos values
                    | values operadores_aritmeticos ID
                    | values operadores_aritmeticos values'''
    print("Entrou no bloco de operacao_aritmetica")
    try:    
        if p.slice[1].type == 'ID':
            verificar_variavel_usada(p[1], p.lineno(1))
            val1, tipo1 = simbolos[p[1]]['valor'], simbolos[p[1]]['tipo']
        else: # Veio de 'values'
            val1 = p[1]
            tipo1 = "tipo do literal 1" # tipo_de_literal(p[1])  função hipotética
    
        # Verificar o segundo operando se for um ID
        if p.slice[3].type == 'ID':
            verificar_variavel_usada(p[3], p.lineno(3))
            val2, tipo2 = simbolos[p[3]]['valor'], simbolos[p[3]]['tipo']
        else: # Veio de 'values'
            val2 = p[3]
            tipo2 = "tipo do literal 2" # tipo_de_literal(p[3])
        print(f"Operação aritmética: {val1} {p[2]} {val2} (tipos: {tipo1}, {tipo2})")
        try:
            resultado = "Teste"
            if tipo1 == 'int' and tipo2 == 'int':
                match p[2]:
                    case '+':
                        resultado = int(val1) + int(val2)
                    case '-':
                        resultado = int(val1) - int(val2)
                    case '*':
                        resultado = int(val1) * int(val2)
                    case '/':
                        resultado = int(val1) / int(val2)
                    case '^':
                        resultado = int(val1) ** int(val2)
            elif tipo1 == 'float' and tipo2 == 'float':
                match p[2]:
                    case '+':
                        resultado = float(val1) + float(val2)
                    case '-':
                        resultado = float(val1) - float(val2)
                    case '*':
                        resultado = float(val1) * float(val2)
                    case '/':
                        resultado = float(val1) / float(val2)
                    case '^':
                        resultado = float(val1) ** float(val2)
            elif tipo1 == 'tipo do literal 1' or tipo2 == 'tipo do literal 2':
                # Aqui você poderia implementar a lógica para lidar com tipos de literais
                # Por exemplo, converter strings para números, etc.
                # Para simplificar, vamos apenas retornar None ou um placeholder.
                resultado = 'resultado_operacao_aritmetica_nao_implementada'
            else:
                #Erro caso sejam tipos diferentes que nao podem ser convertidos.
                resultado = 'resultado_tipos_diferentes'  # Ou algum valor padrão, se necessário

            p[0] = resultado
        except (ValueError, TypeError):
            p[0] = None
        
        # Aqui você faria a operação aritmética e a checagem de tipos.
        # Por simplicidade, vamos focar apenas na verificação de uso.
        # O resultado da operação (p[0]) deveria ser o valor calculado.
        # Como o cálculo não é o foco aqui, vamos apenas retornar um placeholder ou None.
        # Se você retornar None, p_declaracoes precisa estar ciente disso.
        # Para o propósito de apenas verificar o uso, p[0] não precisa ser sofisticado ainda.
        # p[0] = "resultado_operacao_aritmetica" # Placeholder. Em um sistema real, seria o valor.
    except ErroSemantico as e:
        error_token = yacc.YaccSymbol()
        error_token.type = 'ERROR'
        error_token.value = 'error'
        error_token.error_message = str(e)
        p_error(error_token)
        raise SyntaxError("Parsing interrompido devido a erro semântico")

def p_condicao(p):
    '''condicao : values operadores_comparativos values
            | values operadores_comparativos ID
            | ID operadores_comparativos values
            | ID operadores_comparativos ID'''
#    print("Reconheci bloco condicoes")

def p_operadores_comparativos(p):
    ''' operadores_comparativos : LT
                            | LE
                            | GT
                            | GE
                            | NE'''
#    print("Reconheci bloco operadores comparativos")
#Implementar token para operador EGUAL THAN ET ==

def p_operadores_aritmeticos(p):
    ''' operadores_aritmeticos : PLUS 
                            | MINUS
                            | TIMES
                            | DIVIDE
                            | POWER'''
    p[0] = p[1]
#    print("Reconheci operadores aritmeticos")

def p_tipos(p):
    ''' tipos : INT 
            | CHAR 
            | FLOAT'''
    p[0] = p[1]

def p_values(p):
    ''' values : INTEGER
            | STRING
            | FLOATN'''
    p[0] = p[1]
    
def p_error(p):
    if hasattr(p, 'error_message'):
        # Erro semântico personalizado
        print(p.error_message)
    elif p:
        print(f"Erro de sintaxe na linha {p.lineno}: token '{p.value}'")
        print(f"Tipo do token: {p.type}")
    else:
        print("Erro de sintaxe no final do arquivo (EOF)")  

# Constroi o analisador sintático
parser = yacc.yacc()

logging.basicConfig(
    level=logging.INFO,
    filename="parselog.txt"
)

# entrada do arquivo
file = open("input8.txt",'r')
data = file.read()

# data = 'int main();'

# string de teste como entrada do analisador léxico
#lexer.input(data)

# Tokenização
#for tok in lexer:
#    print(tok)
#    print(tok.type, tok.value, tok.lineno, tok.lexpos)

# chama o parser\
try:
    parser.parse(data, debug=logging.getLogger())
except SyntaxError as e:
    print(f"Compilação interrompida: {e}")
