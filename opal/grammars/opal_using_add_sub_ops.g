program: block

block: instruction
     | (instruction _term)*

instruction: selector
    | number

?selector: BOOLEAN -> boolean
    | name

name: /[a-zA-Z_]\w*/
number: INT

INT: ["+"|"-"] DIGIT+

BOOLEAN.2: /(true)|(false)/
STRING  : /("(?!"").*?(?<!\\)(\\\\)*?"|'(?!'').*?(?<!\\)(\\\\)*?')/i

_term   : _NEWLINE

%import common.DIGIT
%import common.LETTER
%import common.CNAME
%import common.NEWLINE -> _NEWLINE
%import common.WS
%ignore WS

