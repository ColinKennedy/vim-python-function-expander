function! TrimUnchangedPythonParameters()
python << EOF
from python_function_expander import trim
from python_function_expander import trimmer
from python_function_expander import vim_trimmer
reload(trim)
reload(trimmer)
reload(vim_trimmer)

vim_trimmer.trim_unchanged_parameters_in_buffer()
EOF
endfunction
