program: block

block: instruction+

instruction: sum NEWLINE

?sum: product
    | sum _add_op product   -> add_sub
?product: atom
    | product _mul_op atom  -> mul_div
?atom: NUMBER
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