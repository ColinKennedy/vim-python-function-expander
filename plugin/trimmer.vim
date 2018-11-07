if !has('python') && !has('python3')
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


" from python_function_expander import environment
" environment.init()
execute g:_uspy "from python_function_expander import environment;environment.init()"


function! s:TrimUnchangedPythonParameters()
    " from python_function_expander.trimmer import vim_trimmer
    " vim_trimmer.trim_unchanged_arguments_in_buffer()
    execute g:_uspy "from python_function_expander.trimmer import vim_trimmer;vim_trimmer.trim_unchanged_arguments_in_buffer()"
endfunction


let g:trimmer_loaded = '1'
