program: block

block:  (_stmt _NEWLINE)*

_stmt: _comp_statement
    | test

_comp_statement:
    | assign
    | print
    | if_

?assign: (name "=" test)

print: "print" "(" test ")"

?if_: (_IF test _THEN) block [_ELSE  block] _END

?test: test _comp_op test -> comp
    | product
    | test "+" product   -> add
    | test "-" product   -> sub
?product: atom
    | product "*" atom  -> mul
    | product "/" atom  -> div
?atom: const
    | "(" test ")"

!_comp_op: ">"|"<"|">="|"<="|"=="|"!="

?const: selector | number | string | boolean

?selector: var

?number: float | int

float: FLOAT
int: INT
string: STRING
boolean: BOOLEAN

name: CNAME
var: CNAME

// bug on lark forces this to be a regex
BOOLEAN.2: /true|false/

_IF.10: /if/
_THEN.10: /then/
_ELSE.10: /else/
_END.10: /end/


INT: ["+"|"-"] DIGIT+
FLOAT   : ["+"|"-"] INT "." INT
STRING  : /("(?!"").*?(?<!\\)(\\\\)*?"|'(?!'').*?(?<!\\)(\\\\)*?')/i


_NEWLINE: /\n\s*/

%import common.WS_INLINE
%import common.DIGIT
%import common.CNAME

%ignore WS_INLINE



