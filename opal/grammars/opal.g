program: blockblock:  (_stmt _NEWLINE)*_stmt: _comp_statement    | test_comp_statement:    | assign    | print    | if_    | while_    | for_    | class_    | def_?assign: (name "=" test)print: "print" "(" test ")"?if_: (_IF test) block [_ELSE  block] _END?while_: break_    | continue_    | "while" test block _ENDbreak_: "break"continue_: "continue"?def_: "def" name "(" params? ")" block _ENDparams: name ("," name)*?class_: "class" name block _END    | "class" name "<" name block _END -> inherits?for_: break_    | continue_    | "for" name "in" (var|list) block _END?test: test _comp_op test -> comp    | product    | test "+" product   -> add    | test "-" product   -> sub?product: atom    | product "*" atom  -> mul    | product "/" atom  -> div?atom: const    | list    | "(" test ")"!_comp_op: ">"|"<"|">="|"<="|"=="|"!="?const: selector | number | string | boolean?selector: selector "[" index "]" -> list_access    | var?number: float | intlist: list "[" index "]" -> list_access    | "[" [test ("," test)*] "]"index: intfloat: FLOATint: INTstring: STRINGboolean: BOOLEANname: CNAMEvar: CNAME// bug on lark forces this to be a regexBOOLEAN.2: /true|false/_IF.10: /if/_DO.10: /do/_ELSE.10: /else/_END.10: /end/INT: ["+"|"-"] DIGIT+FLOAT   : ["+"|"-"] INT "." INTSTRING  : /("(?!"").*?(?<!\\)(\\\\)*?"|'(?!'').*?(?<!\\)(\\\\)*?')/i_NEWLINE: /\n\s*/%import common.WS_INLINE%import common.DIGIT%import common.CNAME%ignore WS_INLINE