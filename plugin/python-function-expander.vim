if !has('python')
    echoerr "python-function-expander requires Python. Cannot continue loading this plugin"
    finish
endif


if get(g:, 'expander_loaded', '0') == '1'
    finish
endif


if get(g:, 'expander_full_auto', '0') == '1'
    autocmd! CursorHoldI *.py call s:ExpandSignatures()
endif


function! s:ExpandSignatures()
pythonx << EOF
from python_function_expander import jedi_expander
import UltiSnips
import vim

(row, column) = vim.current.window.cursor
current_line = vim.current.buffer[row - 1]
try:
    previous_character = current_line[column - 1]
except IndexError:
    previous_character = ''

needs_expansion = previous_character == '('
if needs_expansion:
    vim.current.buffer[row - 1] += jedi_expander.get_balanced_parenthesis()

    # Note: I took this next section from <UltiSnips.snippet.definition._base.SnippetDefinition._eval_code>
    current = vim.current

    _locals = {
        'window': current.window,
        'buffer': current.buffer,
        'line': current.window.cursor[0] - 1,
        'column': current.window.cursor[1] - 1,
        'cursor': UltiSnips.snippet.definition._base._SnippetUtilCursor(current.window.cursor),
    }

    snip = UltiSnips.text_objects._python_code.SnippetUtilForAction(_locals)

    # Now actually do the expansion
    jedi_expander.expand_signatures(snip)
EOF
endfunction


let g:expander_loaded = '1'
