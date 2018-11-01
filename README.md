# vim-python-function-expander

Have you ever forgotten the parameters to a Python function?
Or maybe you are just tired of typing the same keyword arguments over and over?
Do you find yourself making typos while trying to create and instance of a class?

If so then vim-python-function-expander is here for you.

Write our your function/class/callable object,
put your cursor inside of the `()`s, and press Tab.
vim-python-function-expander will detect every argument inside of the `()`s and
insert them as text.

(|x| is the location of the cursor)

Before:

```python
import argparse

argparse.ArgumentParser(|x|)
```

After:

```python
import argparse

argparse.ArgumentParser(
    prog=None,
    usage=None,
    description=None,
    epilog=None,
    version=None,
    parents=[],
    formatter_class=HelpFormatter,
    prefix_chars='-',
    fromfile_prefix_chars=None,
    argument_default=None,
    conflict_handler='error',
    add_help=True,
)
```

vim-python-function-expander also integrates with
[UltiSnips](https://github.com/SirVer/ultisnips) so that you can jump from one
argument to the next with a single keystroke. vim-python-function-expander will
not only save you time but also prevent you from making mistakes and typos.

*As long as your Python file is able to be parsed, vim-python-function-expander
will find the call signature*. That means you can use it on anything, not just
the standard library.

Here's a recording of the function expansion, in-action:

https://asciinema.org/a/192301


## Requirements

For vim-python-function-expander to work, several vim plugins and Python
packages must be installed:

Vim Plugins:
[UltiSnips](https://github.com/SirVer/ultisnips)

[jedi-vim](https://github.com/davidhalter/jedi-vim)

Python Packages:
[astroid](https://pypi.org/project/astroid/)

Install all 3 requirements before continuing.


## Installation

1. First, install everything in [Requirements](#Requirements) if you have not already.

2. Add this repository with your preferred package manager:

Example (Using [vim-plug](https://github.com/junegunn/vim-plug)):
```vim
Plug 'https://bitbucket.org/korinkite/python-function-expander.git'
```
Then run `:PlugInstall` and restart Vim.


Or install this repository manually by cloning it and copying each of its
folder's contents to your `~/.vim` folder:

```bash
git clone https://github.com/ColinKennedy/vim-python-function-expander.git
```

## How Does It Work?
[jedi-vim](https://github.com/davidhalter/jedi-vim) is a fantastic
static-analysis library. As long your module's contents are importable, jedi
can usually find the definition of your object and its call signature.

I then take jedi-vim's found call signature, which could be `[foo, bar, bazz=8]`
and then convert into an UltiSnips-friendly string like
`"{1:foo}, {2:bar}, bazz{3:8}"` and send it to UltiSnips
[as an anonymous snippet](https://github.com/SirVer/ultisnips/blob/master/pythonx/UltiSnips/snippet_manager.py#L222).
UltiSnips "expands" that body of text at the cursor's position and voila,
an automatic call signature.

[astroid](https://pypi.org/project/astroid/) is unused if you have
`g:expander_use_local_variables` set to `0`. It is what is used to check
which variables you have already defined in your file and inserts them into the
call signature.


## Configuration Settings

|            Variable             | Default  |                                                     Description                                                      |
|---------------------------------|----------|----------------------------------------------------------------------------------------------------------------------|
| g:expander_use_local_variables  |       1  | This will try to fill in optional arguments in the expanded text with variables in the current scope. if they exist. |
| g:expander_full_auto            |       0  | If "1" then python-function-expander will automatically expand the callable object for you                           |
