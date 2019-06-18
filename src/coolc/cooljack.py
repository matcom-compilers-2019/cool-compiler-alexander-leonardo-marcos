from .coolex import tokens, Coolex
from . import coolast as ast
from .ply import yacc


# noinspection PyMethodMayBeStatic
class CoolJack:
    def __init__(self, lexer=None):
        # Initialize self.parser to None
        self.tokens = tokens
        self.lexer = lexer
        self.parser = None
        self.error_list = []

    # ################################ PRECEDENCE RULES ################################

    # precedence rules
    precedence = (
        ('right', 'ASSIGN'),
        ('right', 'NOT'),
        ('nonassoc', 'LTEQ', 'LT', 'EQ'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULTIPLY', 'DIVIDE'),
        ('right', 'ISVOID'),
        ('right', 'INT_COMP'),
        ('left', 'AT'),
        ('left', 'DOT')
    )

    # ################### START OF FORMAL GRAMMAR RULES DECLARATION ####################

    def p_program(self, parse):
        """
        program : class_list
        """
        parse[0] = ast.Program(classes=parse[1])

    def p_class_list(self, parse):
        """
        class_list : class_list class SEMICOLON
                   | class SEMICOLON
        """
        if len(parse) == 3:
            parse[0] = (parse[1],)
        else:
            parse[0] = parse[1] + (parse[2],)

    def p_class(self, parse):
        """
        class : CLASS TYPE LBRACE features_list_opt RBRACE
        """
        parse[0] = ast.Class(name=parse[2], parent="Object", features=parse[4])

    def p_class_inherits(self, parse):
        """
        class : CLASS TYPE INHERITS TYPE LBRACE features_list_opt RBRACE
        """
        parse[0] = ast.Class(name=parse[2], parent=parse[4], features=parse[6])

    def p_feature_list_opt(self, parse):
        """
        features_list_opt : features_list
                          | empty
        """
        parse[0] = tuple() if parse.slice[1].type == "empty" else parse[1]

    def p_feature_list(self, parse):
        """
        features_list : features_list feature SEMICOLON
                      | feature SEMICOLON
        """
        if len(parse) == 3:
            parse[0] = (parse[1],)
        else:
            parse[0] = parse[1] + (parse[2],)

    def p_feature_method(self, parse):
        """
        feature : ID LPAREN formal_params_list RPAREN COLON TYPE LBRACE expression RBRACE
        """
        parse[0] = ast.ClassMethod(
            name=parse[1], formal_params=parse[3], return_type=parse[6], body=parse[8])

    def p_feature_method_no_formals(self, parse):
        """
        feature : ID LPAREN RPAREN COLON TYPE LBRACE expression RBRACE
        """
        parse[0] = ast.ClassMethod(
            name=parse[1], formal_params=tuple(), return_type=parse[5], body=parse[7])

    def p_feature_attr_initialized(self, parse):
        """
        feature : ID COLON TYPE ASSIGN expression
        """
        parse[0] = ast.ClassAttribute(
            name=parse[1], attr_type=parse[3], init_expr=parse[5])

    def p_feature_attr(self, parse):
        """
        feature : ID COLON TYPE
        """
        parse[0] = ast.ClassAttribute(
            name=parse[1], attr_type=parse[3], init_expr=None)

    def p_formal_list_many(self, parse):
        """
        formal_params_list  : formal_params_list COMMA formal_param
                            | formal_param
        """
        if len(parse) == 2:
            parse[0] = (parse[1],)
        else:
            parse[0] = parse[1] + (parse[3],)

    def p_formal(self, parse):
        """
        formal_param : ID COLON TYPE
        """
        parse[0] = ast.FormalParameter(name=parse[1], param_type=parse[3])

    def p_expression_object_identifier(self, parse):
        """
        expression : ID
        """
        parse[0] = ast.Object(name=parse[1])

    def p_expression_integer_constant(self, parse):
        """
        expression : INTEGER
        """
        parse[0] = ast.Integer(content=parse[1])

    def p_expression_boolean_constant(self, parse):
        """
        expression : BOOLEAN
        """
        parse[0] = ast.Boolean(content=parse[1])

    def p_expression_string_constant(self, parse):
        """
        expression : STRING
        """
        parse[0] = ast.String(content=parse[1])

    def p_expr_self(self, parse):
        """
        expression  : SELF
        """
        parse[0] = ast.Self()

    def p_expression_block(self, parse):
        """
        expression : LBRACE block_list RBRACE
        """
        parse[0] = ast.Block(expr_list=parse[2])

    def p_block_list(self, parse):
        """
        block_list : block_list expression SEMICOLON
                   | expression SEMICOLON
        """
        if len(parse) == 3:
            parse[0] = (parse[1],)
        else:
            parse[0] = parse[1] + (parse[2],)

    def p_expression_assignment(self, parse):
        """
        expression : ID ASSIGN expression
        """
        parse[0] = ast.Assignment(ast.Object(name=parse[1]), expr=parse[3])

    # ######################### METHODS DISPATCH ######################################

    def p_expression_dispatch(self, parse):
        """
        expression : expression DOT ID LPAREN arguments_list_opt RPAREN
        """
        parse[0] = ast.DynamicDispatch(
            instance=parse[1], method=parse[3], arguments=parse[5])

    def p_arguments_list_opt(self, parse):
        """
        arguments_list_opt : arguments_list
                           | empty
        """
        parse[0] = tuple() if parse.slice[1].type == "empty" else parse[1]

    def p_arguments_list(self, parse):
        """
        arguments_list : arguments_list COMMA expression
                       | expression
        """
        if len(parse) == 2:
            parse[0] = (parse[1],)
        else:
            parse[0] = parse[1] + (parse[3],)

    def p_expression_static_dispatch(self, parse):
        """
        expression : expression AT TYPE DOT ID LPAREN arguments_list_opt RPAREN
        """
        parse[0] = ast.StaticDispatch(
            instance=parse[1], dispatch_type=parse[3], method=parse[5], arguments=parse[7])

    def p_expression_self_dispatch(self, parse):
        """
        expression : ID LPAREN arguments_list_opt RPAREN
        """
        parse[0] = ast.DynamicDispatch(
            instance=ast.Self(), method=parse[1], arguments=parse[3])

    # ######################### PARENTHESIZED, MATH & COMPARISONS #####################

    def p_expression_math_operations(self, parse):
        """
        expression : expression PLUS expression
                   | expression MINUS expression
                   | expression MULTIPLY expression
                   | expression DIVIDE expression
        """
        if parse[2] == '+':
            parse[0] = ast.Addition(first=parse[1], second=parse[3])
        elif parse[2] == '-':
            parse[0] = ast.Subtraction(first=parse[1], second=parse[3])
        elif parse[2] == '*':
            parse[0] = ast.Multiplication(first=parse[1], second=parse[3])
        elif parse[2] == '/':
            parse[0] = ast.Division(first=parse[1], second=parse[3])

    def p_expression_math_comparisons(self, parse):
        """
        expression : expression LT expression
                   | expression LTEQ expression
                   | expression EQ expression
        """
        if parse[2] == '<':
            parse[0] = ast.LessThan(first=parse[1], second=parse[3])
        elif parse[2] == '<=':
            parse[0] = ast.LessThanOrEqual(first=parse[1], second=parse[3])
        elif parse[2] == '=':
            parse[0] = ast.Equal(first=parse[1], second=parse[3])

    def p_expression_with_parenthesis(self, parse):
        """
        expression : LPAREN expression RPAREN
        """
        parse[0] = parse[2]

    # ######################### CONTROL FLOW EXPRESSIONS ##############################

    def p_expression_if_conditional(self, parse):
        """
        expression : IF expression THEN expression ELSE expression FI
        """
        parse[0] = ast.If(predicate=parse[2],
                          then_body=parse[4], else_body=parse[6])

    def p_expression_while_loop(self, parse):
        """
        expression : WHILE expression LOOP expression POOL
        """
        parse[0] = ast.WhileLoop(predicate=parse[2], body=parse[4])

    # ######################### LET EXPRESSIONS ########################################

    def p_expression_let(self, parse):
        """
        expression : let_expression
        """
        parse[0] = parse[1]

    def p_let(self, parse):
        """
        let_expression : LET declaration_list IN expression
        """
        parse[0] = ast.Let(declaration_list=parse[2], body=parse[4])

    def p_declaration_list(self, parse):
        """
        declaration_list : declaration_list COMMA declaration
                         | declaration
        """
        if len(parse) == 2:
            parse[0] = (parse[1],)
        else:
            parse[0] = parse[1] + (parse[3],)

    def p_declaration(self, parse):
        """
        declaration : ID COLON TYPE ASSIGN expression
                    | ID COLON TYPE
        """
        if len(parse) == 6:
            parse[0] = ast.Declaration(identifier=ast.Object(
                name=parse[1]), ttype=parse[3], expression=parse[5])
        else:
            parse[0] = ast.Declaration(identifier=ast.Object(
                name=parse[1]), ttype=parse[3], expression=None)

    # ######################### CASE EXPRESSION ########################################

    def p_expression_case(self, parse):
        """
        expression : CASE expression OF actions_list ESAC
        """
        parse[0] = ast.Case(expr=parse[2], actions=parse[4])

    def p_actions_list(self, parse):
        """
        actions_list : actions_list action
                     | action
        """
        if len(parse) == 2:
            parse[0] = (parse[1],)
        else:
            parse[0] = parse[1] + (parse[2],)

    def p_action_expr(self, parse):
        """
        action : ID COLON TYPE ARROW expression SEMICOLON
        """
        parse[0] = ast.Action(parse[1], parse[3], parse[5])

    # ######################### UNARY OPERATIONS #######################################

    def p_expression_new(self, parse):
        """
        expression : NEW TYPE
        """
        parse[0] = ast.NewObject(parse[2])

    def p_expression_isvoid(self, parse):
        """
        expression : ISVOID expression
        """
        parse[0] = ast.IsVoid(parse[2])

    def p_expression_integer_complement(self, parse):
        """
        expression : INT_COMP expression
        """
        parse[0] = ast.IntegerComplement(parse[2])

    def p_expression_boolean_complement(self, parse):
        """
        expression : NOT expression
        """
        parse[0] = ast.BooleanComplement(parse[2])

    # ######################### THE EMPTY PRODUCTION ###################################

    def p_empty(self, parse):
        """
        empty :
        """
        parse[0] = None

    # ######################### PARSE ERROR HANDLER ####################################

    def p_error(self, parse):
        """
        Error rule for Syntax Errors handling and reporting.
        """
        if parse is None:
            print("Error! Unexpected end of input!")
        else:
            # error = f'Syntax error! Line: {parse.lineno}, position: {parse.lexpos}, character: {parse.value}, type: {parse.type}'
            error = f"({parse.lineno},{parse.lexpos}) - SyntacticError: " \
                    f"Parse -> '{parse.value}' Type -> '{parse.type}'"
            self.error_list.append(error)
            self.parser.errok()

    # ################### END OF FORMAL GRAMMAR RULES SPECIFICATION ####################

    # #################################  PUBLIC  #######################################

    def build(self, **kwargs):
        # Obviously needs a lexer
        lexer = Coolex() if not self.lexer else self.lexer
        lexer.build()

        # Build yacc parser
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self, program_source_code: str) -> ast.Program:
        """
        Parses a COOL program source code passed as a string.
        :param program_source_code: string.
        :return: Parser output.
        """
        if self.parser is None:
            raise Exception("Please, build the parser first.")

        return self.parser.parse(program_source_code)


def main():
    import sys

    parser = CoolJack()
    parser.build()

    if len(sys.argv) > 1:
        if not str(sys.argv[1]).endswith(".cl"):
            print("Cool program source code files must end with .cl extension.")
            print("Usage: python3 cooljack.py program.cl")
            exit()

        input_file = sys.argv[1]
        with open(input_file, encoding="utf-8") as file:
            cool_program_code = file.read()

        parse_result = parser.parse(cool_program_code)
        print(parse_result)
    else:
        print("CoolJack Parser: Interactive Mode.\r\n")
        while True:
            try:
                s = input('COOL >>> ')
            except EOFError:
                break
            if not s:
                continue
            result = parser.parse(s)
            if result is not None:
                print(result)


if __name__ == '__main__':
    main()
