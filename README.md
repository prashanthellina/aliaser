# What is aliaser? #

Aliaser helps you identify frequently typed commands and creates bash aliases for them. This can help make you more productive. Aliases works by analyzing your .bash\_history file.

# Installation #

Become root and run,
./install

The installer will print some lines which have to be added to your .bashrc; do so. Note that aliaser uses .bash\_history to understand how you use commands. Bash history is enabled by default on most distributions. If otherwise, please check your distribution's documentation to enabled it. It is advisable to increase the bash\_history size.

# Usage #

```
    usage: ./aliaser.py <command> <args>
    add
    ---
    Add a new alias.
        aliaser <alias> "<command>"
        eg: aliaser add ssh43 "ssh root@192.168.1.43"

    delete
    ------
    Delete an existing alias.
        aliaser '<alias>'
        eg: aliaser delete 'ssh43'

    delete-ignored
    --------------
    Delete an ignore command from list.
        aliaser '<ignore_command>'
        eg: aliaser delete-ignored 'sudo apt-get install'

    do
    --
    Analyses bash history and prompts you to create aliases
        for most frequent commands.
        eg: aliaser

    show
    ----
    Show aliases which are active.
        eg: aliaser show

    show-freq
    ---------
    Analyses bash history and show frequency of commands.

    show-ignored
    ------------
    Show list of ignored commands.
        eg: aliaser show-ignored

    show-random
    -----------
    Show a random alias from the ones you created.
        eg: aliaser show-random

    show-tips
    ---------
    Show useful usage tips.
        eg: aliaser show-tips

    help
    ----
    prints the above.
    eg: aliaser help
```

# License #

```
 Copyright (c) 2009, Prashanth Ellina
 All rights reserved.
 
 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions are met:
     * Redistributions of source code must retain the above copyright
       notice, this list of conditions and the following disclaimer.
     * Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.
     * Neither the name of the <organization> nor the
       names of its contributors may be used to endorse or promote products
       derived from this software without specific prior written permission.
 
 THIS SOFTWARE IS PROVIDED BY Prashanth Ellina ''AS IS'' AND ANY
 EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 DISCLAIMED. IN NO EVENT SHALL Prashanth Ellina BE LIABLE FOR ANY
 DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```