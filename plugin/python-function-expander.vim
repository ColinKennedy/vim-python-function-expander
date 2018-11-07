if !has('pythonx')
    echoerr "vim-python-function-expander requires Python. Cannot continue loading this plugin"
    finish
endif


" Get a Python version to run with (Vim 8.0+ can just use `pythonx`)
if get(g:, 'expander_python_version', '2') == '2' && has('python')
   let g:_uspy=":python "
elseif get(g:, 'expander_python_version', '3') == '3' && has('python3')
   let g:_uspy=":python3 "
else
    echoerr "No matching Python version could be found"
endif


if get(g:, 'expander_loaded', '0') == '1'
    finish
endif


if get(g:, 'expander_full_auto', '0') == '1'
    autocmd! CursorHoldI *.py call s:ExpandSignatures()
endif


function! s:ExpandSignatures()
    "from python_function_expander import jedi_expander
    "jedi_expander.expand_signature_at_cursor()"
    execute g:_uspy "from python_function_expander import jedi_expander;jedi_expander.expand_signature_at_cursor()"
endfunction


let g:expander_loaded = '1'
