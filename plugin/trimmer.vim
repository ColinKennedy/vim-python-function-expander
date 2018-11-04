if !has('python')
    echoerr "vim-python-function-expander requires Python. Cannot continue loading this plugin"
    finish
endif


if get(g:, 'trimmer_loaded', '0') == '1'
    finish
endif

command! -nargs=0 TrimUnchangedPythonParameters call s:TrimUnchangedPythonParameters()

" Plugin mappings
nnoremap <silent> <Plug>(trimmer-mapping) :TrimUnchangedPythonParameters<CR>

" Create default mappings if they are not defined
if !hasmapto('<Plug>(trimmer-mapping)')
    nmap <leader>ta <Plug>(trimmer-mapping)
endif


pythonx << EOF
from python_function_expander import environment
environment.init()
EOF


function! s:TrimUnchangedPythonParameters()
pythonx << EOF
from python_function_expander.trimmer import vim_trimmer
vim_trimmer.trim_unchanged_arguments_in_buffer()
EOF
endfunction


let g:trimmer_loaded = '1'
