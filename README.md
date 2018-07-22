# Python auto-expander

Leverage the power of the Jedi to write better Python code, faster.


## Usage

Write a function, class, or callable Python object like you normally would.
Then, after you type "(", press your snippet-expansion key (For example. [TAB])
and let auto-expander do the work.

https://asciinema.org/a/192301


## Requirements

This plug-in is an integration of two other Vim plug-ins.

[UltiSnips](https://github.com/SirVer/ultisnips)

[jedi-vim](https://github.com/davidhalter/jedi-vim)

jedi-vim handles parsing the current Python file and UltiSnips is used to
insert the text directly into Vim.


## Installation

1. First, install UltiSnips and jedi-vim if you have not already.

2. Add this repository manually or use your preferred package manager and add
   the following line to your .vimrc.

Example (Using [vim-plug](https://github.com/junegunn/vim-plug)):
```
Plug 'https://bitbucket.org/korinkite/python-function-expander.git'
```

Then run `:PlugInstall` and restart Vim.


## Configuration Settings

|            Variable             | Default  |                                                     Description                                                      |
|---------------------------------|----------|----------------------------------------------------------------------------------------------------------------------|
| g:expander_use_local_variables  |       1  | This will try to fill in optional arguments in the expanded text with variables in the current scope. if they exist. |
| g:expander_full_auto            |       0  | If "1" then python-function-expander will automatically expand the callable object for you                           |
