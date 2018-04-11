program: block

block: instruction
     | (instruction _term)*

instruction: test
    | statements


?statements: assign
    | print_stmt -> print

assign: name "=" test

?print_stmt: "print" "(" test ")"

?test: product
    | test "+" product   -> add
    | test "-" product   -> sub
?product: atom
    | product "*" atom  -> mul
    | product "/" atom  -> div
?atom: atom _comp_op atom -> comp
    | const
    | "(" test ")"

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