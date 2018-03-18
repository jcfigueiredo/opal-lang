program: block

block: instruction  (term instruction)* (instruction term)*

instruction: sum


?sum: product
    | sum _add_op product   -> add_sub
?product: atom
    | product _mul_op atom  -> mul_div
?atom: NUMBER
    | "(" sum ")"

!_add_op: "+"|"-"
!_mul_op: "*"|"@"|"/"|"%"|"//"

?const: float | int | string

float: FLOAT
int: INT
string: STRING

INT: ["+"|"-"] DIGIT+
FLOAT: ["+"|"-"] INT "." INT
STRING : /("(?!"").*?(?<!\\)(\\\\)*?"|'(?!'').*?(?<!\\)(\\\\)*?')/i

term: NEWLINE

%import common.DIGIT
%import common.NEWLINE
%import common.WS
%ignore WS