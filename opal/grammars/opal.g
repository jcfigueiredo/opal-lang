program: block

block: instruction (instruction term)*

instruction: sum


?sum: "print" "(" sum ")" -> print
    | product
    | sum "+" product   -> add
    | sum "-" product   -> sub
?product: atom
    | product "*" atom  -> mul
    | product "/" atom  -> div
?atom: const
    | "(" sum ")"

// !_add_op: "+"|"-"
// !_mul_op: "*"|"@"|"/"|"%"|"//"

?const: float | int | string | boolean

float: FLOAT
int: INT
string: STRING
!boolean: "true" | "false"

INT: ["+"|"-"] DIGIT+
FLOAT: ["+"|"-"] INT "." INT
STRING : /("(?!"").*?(?<!\\)(\\\\)*?"|'(?!'').*?(?<!\\)(\\\\)*?')/i

term: NEWLINE

%import common.DIGIT
%import common.NEWLINE
%import common.WS
%ignore WS