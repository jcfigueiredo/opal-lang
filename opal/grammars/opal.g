program: block

block: instruction+

instruction: sum NEWLINE

?sum: product
    | sum "+" product   -> add
    | sum "-" product   -> sub
?product: atom
    | product "*" atom  -> mul
    | product "/" atom  -> div
?atom: NUMBER           -> number
    | "(" sum ")"

!_add_op: "+"|"-"
!_mul_op: "*"|"@"|"/"|"%"|"//"

NUMBER: FLOAT | INT

INT: ["+"|"-"] DIGIT+
FLOAT: ["+"|"-"] INT "." INT


%import common.DIGIT
%import common.NEWLINE
%import common.WS
%ignore WS