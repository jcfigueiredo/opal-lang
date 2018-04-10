program: block

block: instruction
     | (instruction _term)*

instruction: sum
    | statements


?statements: assign
    | print_stmt -> print

assign: name "=" sum

?print_stmt: "print" "(" sum ")"

?sum: product
    | sum "+" product   -> add
    | sum "-" product   -> sub
?product: atom
    | product "*" atom  -> mul
    | product "/" atom  -> div
?atom: atom _comp_op atom -> comp
    | const
    | "(" sum ")"

!_comp_op: ">"|"<"|">="|"<="|"=="|"!="

?const: selector | number | string | boolean

?selector: name

?number: float | int

float: FLOAT
int: INT
string: STRING
boolean: BOOLEAN

name : /[a-zA-Z]\w*/
// bug on lark forces this to be a regex
BOOLEAN.2: /true|false/

INT: ["+"|"-"] DIGIT+
FLOAT   : ["+"|"-"] INT "." INT
STRING  : /("(?!"").*?(?<!\\)(\\\\)*?"|'(?!'').*?(?<!\\)(\\\\)*?')/i

_term   : _NEWLINE

%import common.DIGIT
%import common.NEWLINE -> _NEWLINE
%import common.WS
%ignore WS