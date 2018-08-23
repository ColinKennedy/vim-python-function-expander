" TODO : Make this a local function later
" TODO : Remove the reload statements, later
"
function! TrimUnchangedPythonParameters()
python << EOF
from python_function_expander.trimmer import parser
from python_function_expander.trimmer import trimmer
from python_function_expander.trimmer import vim_trimmer
reload(parser)
reload(trimmer)
reload(vim_trimmer)

vim_trimmer.trim_unchanged_arguments_in_buffer()
EOF
endfunction
