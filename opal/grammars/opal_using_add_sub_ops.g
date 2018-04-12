program: block

block:  (instruction term)*

instruction: statement
    | test

?statement: assign
    | print
    | if_

?assign: ass_bool
    | name "=" name

?ass_bool: name "=" test

print: "print" "(" test ")"

if_: IF (boolean THEN) block [ELSE block] END


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

?const: number | string | boolean

?number: float | int

float: FLOAT
int: INT
string: STRING
boolean: BOOLEAN _NEWLINE

name: NAME
NAME : /[a-zA-Z]\w*/
// bug on lark forces this to be a regex
BOOLEAN.2: /true|false/

IF.10: /if/
THEN.10: /then/
ELSE.10: /else/
END.10: /end/


INT: ["+"|"-"] DIGIT+
FLOAT   : ["+"|"-"] INT "." INT
STRING  : /("(?!"").*?(?<!\\)(\\\\)*?"|'(?!'').*?(?<!\\)(\\\\)*?')/i

?term   : _NEWLINE

%import common.DIGIT
%import common.NEWLINE -> _NEWLINE
%import common.WS
%ignore WS