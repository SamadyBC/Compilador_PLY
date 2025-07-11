from ply import * # type: ignore
import logging

class ErroSemantico(Exception):
    """Exceção para erros semânticos durante a análise"""
    def __init__(self, mensagem):
        self.mensagem = mensagem
        super().__init__(self.mensagem)

class ErroSintatico(Exception):
    """Exceção para erros sintáticos durante a análise"""
    def __init__(self, mensagem):
        self.mensagem = mensagem
        super().__init__(self.mensagem)

def handle_semantic_error(e):
    """
    Função para tratar erros semânticos durante o parsing.
    
    Args:
        e: Exceção do tipo ErroSemantico capturada
    
    Raises:
        SyntaxError: Sempre levanta esta exceção para interromper o parsing
    """
    # Cria um token de erro com a mensagem
    error_token = yacc.YaccSymbol()
    error_token.type = 'ERROR'
    error_token.value = 'error'
    error_token.error_message = str(e)
    #
    ## Substitui o token atual pelo token de erro
    p_error(error_token)
    
    # Interrompe o parsing
    raise SyntaxError("Parsing interrompido devido a erro semântico")

def verificar_variavel_redeclarada(nome_var, linha=0):
    """
    Verifica se uma variável já foi declarada
    Retorna: True se a verificação passar (variável não declarada)
             Lança ErroSemantico se a variável já estiver declarada
    """
    if nome_var in simbolos:
        raise ErroSemantico(f"Erro semântico na linha {linha}: variável '{nome_var}' já declarada")
    return True

def verificar_variavel_usada(nome_var, linha=0):
    """
    Verifica se uma variável foi declarada antes de ser usada
    Retorna: True se a verificação passar (variável está declarada)
             Lança ErroSemantico se a variável não estiver declarada
    """
    if nome_var not in simbolos:
        raise ErroSemantico(f"Erro semântico na linha {linha}: variável '{nome_var}' usada mas não declarada")
    return True

def verificar_variavel_inicializada(nome_var, linha=0):
    """
    Verifica se uma variável foi inicializada antes de ser usada
    Retorna: O valor da variável se a verificação passar
             Lança ErroSemantico se a variável não estiver inicializada
    """
    
    if simbolos[nome_var]['valor'] is None:
        raise ErroSemantico(f"Erro semântico na linha {linha}: variável '{nome_var}' usada antes de ser inicializada")
    return

def verificar_compatibilidade_tipos(tipo_destino, valor, linha=0, modo="atribuicao"):
    """
    Verifica a compatibilidade entre um tipo de destino e um valor,
    realizando a conversão apropriada quando possível.
    
    Args:
        tipo_destino: Tipo da variável de destino ('int', 'float', 'char')
        valor: Valor a ser verificado e convertido
        linha: Número da linha para mensagens de erro
        modo: Contexto da verificação ('atribuicao' ou 'operacao')
    
    Returns:
        O valor convertido para o tipo apropriado
        
    Raises:
        ErroSemantico: Se a conversão não for possível
    """
    # Determinar o tipo do valor
    tipo_valor = None
    valor_convertido = None
    
    # Se o valor é um ID, obter seu tipo e valor da tabela de símbolos
    if isinstance(valor, str) and valor in simbolos:
        tipo_valor = simbolos[valor]['tipo']
        valor_original = simbolos[valor]['valor']
    else:
        valor_original = valor
        # Determinar o tipo do literal
        if isinstance(valor, str): #Verificar essa implementacao
            if valor.isdigit():
                tipo_valor = "int"
            elif '.' in valor and any(c.isdigit() for c in valor):
                tipo_valor = "float"
            else:
                tipo_valor = "char"
        elif isinstance(valor, int):
            tipo_valor = "int"
        elif isinstance(valor, float):
            tipo_valor = "float"
        elif isinstance(valor, str) and len(valor) == 1:  # Considerando um único caractere como 'char'
            tipo_valor = "char"
        else:
            if valor.isdigit(): # Verificar essa implementacao
                tipo_valor = "int"
            elif '.' in valor and any(c.isdigit() for c in valor):
                tipo_valor = "float"
            else:
                tipo_valor = "char"
    
    # Tentar realizar a conversão
    try:
        if tipo_destino == "int":
            if tipo_valor == "int":
                valor_convertido = int(valor_original)
            elif tipo_valor == "float":
                # Conversão de float para int (com potencial perda de precisão)
                valor_convertido = int(float(valor_original))
                if modo == "atribuicao":
                    print(f"Aviso: Conversão de float para int na linha {linha} (possível perda de precisão)")
            else:
                raise ErroSemantico(f"Erro semântico na linha {linha}: não é possível converter '{tipo_valor}' para 'int'")
        
        elif tipo_destino == "float":
            if tipo_valor in ["int", "float"]:
                valor_convertido = float(valor_original)
            else:
                raise ErroSemantico(f"Erro semântico na linha {linha}: não é possível converter '{tipo_valor}' para 'float'")
        
        elif tipo_destino == "char":
            # Implementação simplificada para char
            valor_convertido = str(valor_original)
        
        return valor_convertido
        
    except (ValueError, TypeError):
        raise ErroSemantico(f"Erro semântico na linha {linha}: valor '{valor_original}' incompatível com o tipo '{tipo_destino}'")

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

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Constroi o analisador léxico
lexer = lex.lex()
    
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
    '''corpo : comando
             | corpo comando'''
    print("Reconheci corpo")

def p_comando(p):
    '''comando : declaracoes
               | bloco_while
               | bloco_if
               | bloco_for
               | expressao'''
    print("Reconheci comando")

def p_expressao(p):
    '''expressao : atribuicao'''
#    print("Reconheci bloco expressao")

def p_declaracoes(p):
    '''declaracoes : tipos ID SEMICOLON 
                | tipos declaracoes_linha SEMICOLON
                | tipos ID EQUALS values SEMICOLON
                | tipos ID EQUALS ID SEMICOLON
                | tipos ID EQUALS operacao_aritmetica SEMICOLON'''

    # Armazena o tipo para uso posterior
    print("Entrou no bloco de declaracoes")
    tipo = p[1]
    
    # Caso de declaração com múltiplas variáveis (tipos declaracoes_linha SEMICOLON)
    # Adicionar um try except?
    if len(p) >= 3 and p[2] is None:
        try:
            print(simbolos.keys())
            print(simbolos.items())
            for chave, valor in simbolos.items():
                # Verificando se o atributo em_linha é True
                if valor.get('em_linha') == True:
                    # Atualizando o atributo tipo
                    simbolos[chave]['tipo'] = tipo
                    print(f"Atualizado tipo da variável '{chave}' para '{tipo}'")
            print('Declaracao realizada em linha')
        except ErroSemantico as e:
            handle_semantic_error(e)
    # Caso de declaração simples (tipos ID SEMICOLON)
    elif len(p) >= 3 and p[3] == ";": # Abordagem disfuncional uma vez que isinstance sempre retorna True, ja que todos os termos sao strings - realizar testes
        try:
            verificar_variavel_redeclarada(p[2], p.lineno(2))
            simbolos[p[2]] = {'valor': None, 'tipo': tipo, 'contexto': get_contexto(), 'em_linha': False}
            print(f"Declarada variável '{p[2]}' do tipo '{tipo}'")
        except ErroSemantico as e:
            handle_semantic_error(e)
    
    # Caso de declaracao com  inicializacao e operacao aritmetica (tipos ID EQUALS operacao_aritmetica SEMICOLON)
    elif len(p) >= 5 and p[3] == '=' and p.slice[4].type == 'operacao_aritmetica':
        try:
            verificar_variavel_redeclarada(p[2], p.lineno(2))
            valor = verificar_compatibilidade_tipos(p[1], p[4], p.lineno(4), "declaracao")
            simbolos[p[2]] = {'valor': valor, 'tipo': tipo, 'contexto': get_contexto(), 'em_linha': False}
            print(f"Declarada e inicializada variável '{p[2]}' do tipo '{tipo}' com valor '{valor}'")
        except ErroSemantico as e:
            handle_semantic_error(e)
    
    # Caso de declaração com inicialização (tipos ID EQUALS values SEMICOLON ou tipos ID EQUALS ID SEMICOLON)
    elif len(p) >= 5 and p[3] == '=':
        try:
            verificar_variavel_redeclarada(p[2], p.lineno(2))
            print(f"p[4]: '{p.slice[4].value}' - '{p.slice[4].type}'")
            if p.slice[4].type == 'ID':
                # Implementar funcao para checar compatibilidade entre 'tipo_declarado' e o tipo do literal
                verificar_variavel_usada(p[4], p.lineno(4))
                valor = verificar_compatibilidade_tipos(p[1], p[4], p.lineno(4), "declaracao")

            if p.slice[4].type == 'values':
                # Implementar funcao para checar compatibilidade entre 'tipo_declarado' e o tipo do literal
                print("Verificando tipo de literal:", p.slice[4].value)
                valor = verificar_compatibilidade_tipos(p[1], p[4], p.lineno(4), "declaracao")
                
            if p.slice[4].type == 'operacao_aritmetica':
                # Idealmente, checar compatibilidade entre 'tipo_declarado' e o resultado da operação
                print("Verificando tipo do reseultado da operacao aritmetica:", p.slice[4].value)
                valor = p[4]
            
            simbolos[p[2]] = {'valor': valor, 'tipo': tipo, 'contexto': get_contexto(), 'em_linha': False}
            print(f"Declarada e inicializada variável '{p[2]}' do tipo '{tipo}' com valor '{valor}'")
        except ErroSemantico as e:
           handle_semantic_error(e)
            
    print(f"Reconheci Declarações")

def p_declaracao_linha(p):
    '''declaracoes_linha : ID COMMA declaracoes_linha
                        | ID'''

    try:
        verificar_variavel_redeclarada(p[1], p.lineno(1))
        simbolos[p[1]] = {'valor': None, 'tipo': None, 'contexto': get_contexto(), 'em_linha': True}
    except ErroSemantico as e:
        handle_semantic_error(e)

    p[0] = None
    
    print(f"Reconheci Declarações linha - variavel: {p[1]}")

def p_bloco_while(p):
    '''bloco_while : WHILE LPAREN condicao RPAREN LBRACES corpo RBRACES'''
#    print("Reconheci bloco while")

def p_bloco_if(p):
    '''bloco_if : IF LPAREN condicao RPAREN LBRACES corpo RBRACES
                | IF LPAREN condicao RPAREN LBRACES corpo RBRACES ELSE LBRACES corpo RBRACES
                | IF LPAREN condicao RPAREN LBRACES corpo RBRACES ELSE bloco_if'''
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
        tipo = simbolos[p[1]]['tipo']
        verificar_variavel_usada(p[1], p.lineno(1))
        if len(p) >= 4:
            if p.slice[3].type == 'ID':
                verificar_variavel_usada(p[3], p.lineno(3))
                verificar_variavel_inicializada(p[3], p.lineno(3))
                print("Verificando tipo da variavel:", p.slice[1].value)
                valor = verificar_compatibilidade_tipos(tipo, p[3], p.lineno(4))
            if p.slice[3].type == 'values':
                print("Verificando tipo de literal:", p.slice[3].value)
                valor = verificar_compatibilidade_tipos(tipo, p[3], p.lineno(4))
                
            if p.slice[3].type == 'operacao_aritmetica':
                print("Verificando tipo do resultado da operacao aritmetica:", p.slice[3].value)
                valor = verificar_compatibilidade_tipos(tipo, p[3], p.lineno(4))

            simbolos[p[1]]['valor'] = valor

    except ErroSemantico as e:
        handle_semantic_error(e)
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
            verificar_variavel_inicializada(p[1], p.lineno(3))
            val1, tipo1 = simbolos[p[1]]['valor'], simbolos[p[1]]['tipo']
        else:  # Veio de 'values'
            val1 = p[1]
            # Determinar o tipo com base no valor # tipo_de_literal(p[1])  função hipotética
            print(isinstance(p[1], int), p[1].isdigit())
            if p[1].isdigit(): #Abordagem desfuncional;
                tipo1 = "int"
            elif '.' in p[1] and any(c.isdigit() for c in p[1]):
                tipo1 = "float"
            else:
                tipo1 = "char"  # ou outro tipo adequado
            print('Tipo de Literal: ', tipo1)
    
        # Verificar o segundo operando se for um ID
        if p.slice[3].type == 'ID':
            verificar_variavel_usada(p[3], p.lineno(3))
            verificar_variavel_inicializada(p[3], p.lineno(1))
            val2, tipo2 = simbolos[p[3]]['valor'], simbolos[p[3]]['tipo']
        else:  # Veio de 'values'
            val2 = p[3]
            # Determinar o tipo com base no valor
            print(p[3], isinstance(p[3], int), p[3].isdigit())
            if p[3].isdigit():
                tipo2 = "int"
            elif '.' in p[3] and any(c.isdigit() for c in p[3]):
                tipo2 = "float"
            else:
                tipo2 = "char"
            print('Tipo de Literal: ', tipo2)

        if tipo1 == "float" or tipo2 == "float":
            tipo_resultado = "float"
        else:
            tipo_resultado = "int"

        # Converter os valores para o tipo apropriado
        val1_convertido = verificar_compatibilidade_tipos(tipo_resultado, val1, p.lineno(1), "operacao")
        val2_convertido = verificar_compatibilidade_tipos(tipo_resultado, val2, p.lineno(3), "operacao")
        
        if tipo_resultado == "int":
            match p[2]:
                case '+':
                    resultado = val1_convertido + val2_convertido
                case '-':
                    resultado = val1_convertido - val2_convertido
                case '*':
                    resultado = val1_convertido * val2_convertido
                case '/':
                    if val2_convertido == 0:
                        raise ErroSemantico(f"Erro semântico na linha {p.lineno(3)}: divisão por zero")
                    resultado = val1_convertido // val2_convertido
        elif tipo_resultado == "float":
            match p[2]:
                case '+':
                    resultado = val1_convertido + val2_convertido
                case '-':
                    resultado = val1_convertido - val2_convertido
                case '*':
                    resultado = val1_convertido * val2_convertido
                case '/':
                    if val2_convertido == 0.0:
                        raise ErroSemantico(f"Erro semântico na linha {p.lineno(3)}: divisão por zero")
                    resultado = val1_convertido / val2_convertido
        
        p[0] = resultado

        #try:
        #    resultado = None
#
        #    if tipo1 == 'int' and tipo2 == 'int':
        #        match p[2]:
        #            case '+':
        #                resultado = int(val1) + int(val2)
        #            case '-':
        #                resultado = int(val1) - int(val2)
        #            case '*':
        #                resultado = int(val1) * int(val2)
        #            case '/':
        #                resultado = int(val1) / int(val2)
        #            case '^':
        #                resultado = int(val1) ** int(val2)
        #    elif tipo1 == 'float' and tipo2 == 'float':
        #        match p[2]:
        #            case '+':
        #                resultado = float(val1) + float(val2)
        #            case '-':
        #                resultado = float(val1) - float(val2)
        #            case '*':
        #                resultado = float(val1) * float(val2)
        #            case '/':
        #                resultado = float(val1) / float(val2)
        #            case '^':
        #                resultado = float(val1) ** float(val2)
        #    else:
        #        #Erro caso sejam tipos diferentes que nao podem ser convertidos.
        #        resultado = 'resultado_operacao_aritmetica_nao_implementada'  # Ou algum valor padrão, se necessário
#
        #    p[0] = resultado
        #except (ValueError, TypeError):
        #    p[0] = None
    except ErroSemantico as e:
        handle_semantic_error(e)

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
        print(f"Erro de sintaxe no token: '{p.value}'")
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
file = open("input.txt",'r')
data = file.read()

# data = 'int main( );'

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
