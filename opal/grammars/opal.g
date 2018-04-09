program: block

block: instruction
     | (instruction term)*

instruction: sum
    | statements

statements: "print" "(" sum ")" -> print


?sum: product
    | sum "+" product   -> add
    | sum "-" product   -> sub
?product: atom
    | product "*" atom  -> mul
    | product "/" atom  -> div
?atom: atom _comp_op atom -> comp
    | const
    | "(" sum ")"
    |  assign

assign: var "=" sum
    | var "=" var

?var: id

!_comp_op: ">"|"<"|">="|"<="|"=="|"!="

// !_add_op: "+"|"-"
// !_mul_op: "*"|"@"|"/"|"%"|"//"

?const: number | string | boolean

?number: float | int

float: FLOAT
int: INT
string: STRING
!boolean: "true" | "false"

?id: ID

ID : /[a-zA-Z][a-zA-Z0-9_]*/

INT: ["+"|"-"] DIGIT+
FLOAT: ["+"|"-"] INT "." INT
STRING : /("(?!"").*?(?<!\\)(\\\\)*?"|'(?!'').*?(?<!\\)(\\\\)*?')/i

?term: NEWLINE

%import common.DIGIT
%import common.NEWLINE
%import common.WS
%ignore WS