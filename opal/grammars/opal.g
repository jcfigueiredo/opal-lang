program: block

block: instruction
     | (instruction term)*

instruction: sum
    | statements

?statements: assign
    | print_stmt -> print

?print_stmt: "print" "(" sum ")"
    | "print" "(" boolean ")"

?sum: product
    | sum "+" product   -> add
    | sum "-" product   -> sub
?product: atom
    | product "*" atom  -> mul
    | product "/" atom  -> div
?atom: atom _comp_op atom -> comp
    | const
    | ID -> var
    | boolean
    | "(" sum ")"

assign: ID "=" sum
    | ID "=" ID

!_comp_op: ">"|"<"|">="|"<="|"=="|"!="

?const: number | string

?number: float | int

float: FLOAT
int: INT
string: STRING
boolean: BOOLEAN

ID : /[a-zA-Z][a-zA-Z0-9_]\w*/
// bug on lark forces this to be a regex
BOOLEAN.2: /true|false/

INT: ["+"|"-"] DIGIT+
FLOAT   : ["+"|"-"] INT "." INT
STRING  : /("(?!"").*?(?<!\\)(\\\\)*?"|'(?!'').*?(?<!\\)(\\\\)*?')/i

?term   : NEWLINE

%import common.DIGIT
%import common.NEWLINE
%import common.WS
%ignore WS