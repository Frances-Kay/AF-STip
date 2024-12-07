# -*- coding: utf-8 -*-
"""
@Time    : 2024/12/07 14:00
@Author  : Frances_LQ
@FileName: lq_cleanup_contract_test.py
@SoftWare: PyCharm
@Description: TClean the raw contract code and break it into smaller pieces of data.
"""


import re

# keywords of solidity; immutable set == 提取solidity的关键词
keywords = frozenset(
    {'bool', 'break', 'case', 'catch', 'const', 'continue', 'default', 'do', 'double', 'struct',
     'else', 'enum', 'payable', 'function', 'modifier', 'emit', 'export', 'extern', 'false', 'constructor',
     'float', 'if', 'contract', 'int', 'long', 'string', 'super', 'or', 'private', 'protected', 'noReentrancy',
     'public', 'return', 'returns', 'assert', 'event', 'indexed', 'using', 'require', 'uint', 'onlyDaoChallenge',
     'transfer', 'Transfer', 'Transaction', 'switch', 'pure', 'view', 'this', 'throw', 'true', 'try', 'revert',
     'bytes', 'bytes4', 'bytes32', 'internal', 'external', 'union', 'constant', 'while', 'for', 'notExecuted',
     'NULL', 'uint256', 'uint128', 'uint8', 'uint16', 'address', 'call', 'msg', 'value', 'sender', 'notConfirmed',
     'private', 'onlyOwner', 'internal', 'onlyGovernor', 'onlyCommittee', 'onlyAdmin', 'onlyPlayers', 'ownerExists',
     'onlyManager', 'onlyHuman', 'only_owner', 'onlyCongressMembers', 'preventReentry', 'noEther', 'onlyMembers',
     'onlyProxyOwner', 'confirmed', 'mapping'})

# holds known non-user-defined functions; immutable set  == 保存合约中已知非用户定义的函数
main_set = frozenset({'function', 'constructor', 'modifier', 'contract'})

# arguments in main function; immutable set  == 保存主函数main中的参数
main_args = frozenset({'argc', 'argv'})


# input is a list of string lines
def clean_fragment(fragment):
    # dictionary; map function name to symbol name + number
    fun_symbols = {}
    # dictionary; map variable name to symbol name + number
    var_symbols = {}

    fun_count = 1
    var_count = 1

    # regular expression to catch multi-line comment
    rx_comment = re.compile('\*/\s*$')
    # regular expression to find function name candidates
    rx_fun = re.compile(r'\b([_A-Za-z]\w*)\b(?=\s*\()')
    # regular expression to find variable name candidates
    # rx_var = re.compile(r'\b([_A-Za-z]\w*)\b(?!\s*\()')
    rx_var = re.compile(r'\b([_A-Za-z]\w*)\b(?:(?=\s*\w+\()|(?!\s*\w+))(?!\s*\()')

    # final cleaned gadget output to return to interface
    cleaned_fragment = []

    for line in fragment:
        # process if not the header line and not a multi-line commented line
        if rx_comment.search(line) is None:
            # remove all string literals (keep the quotes)
            nostrlit_line = re.sub(r'".*?"', '""', line)
            # remove all character literals
            nocharlit_line = re.sub(r"'.*?'", "''", nostrlit_line)
            # replace any non-ASCII characters with empty string
            ascii_line = re.sub(r'[^\x00-\x7f]', r'', nocharlit_line)

            # return, in order, all regex matches at string list; preserves order for semantics
            user_fun = rx_fun.findall(ascii_line)
            user_var = rx_var.findall(ascii_line)

            # Could easily make a "clean fragment" type class to prevent duplicate functionality
            # of creating/comparing symbol names for functions and variables in much the same way.
            # The comparison frozenset, symbol dictionaries, and counters would be class scope.
            # So would only need to pass a string list and a string literal for symbol names to
            # another function.
            for fun_name in user_fun:
                if len({fun_name}.difference(main_set)) != 0 and len({fun_name}.difference(keywords)) != 0:
                    # DEBUG
                    # print('comparing ' + str(fun_name + ' to ' + str(main_set)))
                    # print(fun_name + ' diff len from main is ' + str(len({fun_name}.difference(main_set))))
                    # print('comparing ' + str(fun_name + ' to ' + str(keywords)))
                    # print(fun_name + ' diff len from keywords is ' + str(len({fun_name}.difference(keywords))))
                    ###
                    # check to see if function name already in dictionary
                    if fun_name not in fun_symbols.keys():
                        fun_symbols[fun_name] = 'FUN' + str(fun_count)
                        fun_count += 1
                    # ensure that only function name gets replaced (no variable name with same
                    # identifier); uses positive lookforward
                    ascii_line = re.sub(r'\b(' + fun_name + r')\b(?=\s*\()', fun_symbols[fun_name], ascii_line)

            for var_name in user_var:
                # next line is the nuanced difference between fun_name and var_name
                if len({var_name}.difference(keywords)) != 0 and len({var_name}.difference(main_args)) != 0:
                    # DEBUG
                    # print('comparing ' + str(var_name + ' to ' + str(keywords)))
                    # print(var_name + ' diff len from keywords is ' + str(len({var_name}.difference(keywords))))
                    # print('comparing ' + str(var_name + ' to ' + str(main_args)))
                    # print(var_name + ' diff len from main args is ' + str(len({var_name}.difference(main_args))))
                    ###
                    # check to see if variable name already in dictionary
                    if var_name not in var_symbols.keys():
                        var_symbols[var_name] = 'VAR' + str(var_count)
                        var_count += 1
                    # ensure that only variable name gets replaced (no function name with same
                    # identifier; uses negative lookforward
                    ascii_line = re.sub(r'\b(' + var_name + r')\b(?:(?=\s*\w+\()|(?!\s*\w+))(?!\s*\()', \
                                        var_symbols[var_name], ascii_line)

            cleaned_fragment.append(ascii_line)
    # return the list of cleaned lines
    return cleaned_fragment


if __name__ == '__main__':
    test1 = ['require(msg.sender == address(tokenContract));']
    print(clean_fragment(test1))

