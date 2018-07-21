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
python << EOF
import jedi_expander
jedi_expander.expand_signatures()
EOF
endfunction


let g:expander_loaded = '1'