# ATIVIDADE PRÁTICA - reconhecedor de estruturas em C

from ply import *
import logging

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
    print(simbolos)

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
                | tipos ID SEMICOLON declaracoes
                | tipos ID EQUALS values SEMICOLON declaracoes'''
    # Armazena o tipo para uso posterior
    tipo = p[1]
    
    # Caso de declaração com múltiplas variáveis (tipos declaracoes_linha SEMICOLON)
    if len(p) >= 3 and p[2] is None:
        print('Declaracao realizada em linha')
    
    # Caso de declaração simples (tipos ID SEMICOLON)
    elif len(p) >= 3 and isinstance(p[2], str):
        print('Declaracao simples (tipos ID SEMICOLON)')
        if p[2] in simbolos:
            print(f"Erro semantico: variavel '{p[2]}' ja declarada")
        else:
            simbolos[p[2]] = {'valor': None, 'tipo': tipo, 'contexto': get_contexto()}
            print(f"Declarada variável '{p[2]}' do tipo '{tipo}'")
    
    # Caso de declaração com inicialização (tipos ID EQUALS values SEMICOLON)
    elif len(p) >= 5 and p[3] == '=':
        print('Declaracao com inicialização (tipos ID EQUALS values SEMICOLON)')
        if p[2] in simbolos:
            print(f"Erro semantico: variavel '{p[2]}' ja declarada")
        else:
            valor = p[4]
            simbolos[p[2]] = {'valor': valor, 'tipo': tipo, 'contexto': get_contexto()}
            print(f"Declarada e inicializada variável '{p[2]}' do tipo '{tipo}' com valor '{valor}'")
    
    print(f"Reconheci Declarações {tipo} {p[2] if isinstance(p[2], str) else ''} {p[3]}")

def p_declaracao_linha(p):
    '''declaracoes_linha : ID COMMA declaracoes_linha
                        | ID'''
     # Captura o tipo da declaração do nó pai (que deve ser propagado)
    tipo = p[-1]  # Acessa o tipo do nó pai
    
    if p[1] in simbolos:
        print(f"Erro semantico: variavel '{p[1]}' ja declarada")
    else:
        simbolos[p[1]] = {'valor': None, 'tipo': tipo, 'contexto': get_contexto()}
        print(f"Declarada variável '{p[1]}' do tipo '{tipo}'")
    
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
    ''' atribuicao : tipos ID EQUALS values SEMICOLON
                | ID EQUALS values SEMICOLON
                | tipos ID EQUALS ID SEMICOLON
                | ID EQUALS ID SEMICOLON
                | tipos ID EQUALS operacao_aritmetica SEMICOLON
                | ID EQUALS operacao_aritmetica SEMICOLON'''
#    print("Reconheci bloco atribuicao", p[1], p[2])

def p_operacao_aritmetica(p):
    ''' operacao_aritmetica : ID operadores_aritmeticos ID
                    | ID operadores_aritmeticos values
                    | values operadores_aritmeticos ID
                    | values operadores_aritmeticos values'''
#    print("Reconheci bloco operacoes aritmeticas")

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
    if p:
        print(f"Erro de sintaxe na linha {p.lineno}: token '{p.value}'")
        print(f"Tipo do token: {p.type}")
    else:
        print("Erro de sintaxe no final do arquivo (EOF)")


yacc.yacc()

logging.basicConfig(
    level=logging.INFO,
    filename="parselog.txt"
)

# entrada do arquivo
file = open("input8.txt",'r')
data = file.read()

# data = 'int main();'

# string de teste como entrada do analisador léxico
lexer.input(data)

# Tokenização
for tok in lexer:
     print(tok)

# chama o parser
yacc.parse(data, debug=logging.getLogger())
