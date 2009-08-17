#!/usr/bin/env python
# Copyright (c) 2009, Prashanth Ellina
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY Prashanth Ellina ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Prashanth Ellina BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import sys
import dbm
import time
import random
from cmd import Cmd

HOME_DIR = os.environ.get('HOME', '/tmp')
DATA_DIR = os.path.join(HOME_DIR, '.aliaser')
ALIASES_DB = os.path.join(DATA_DIR, 'aliases')
IGNORED_DB = os.path.join(DATA_DIR, 'ignored')
ALIASES_SH = os.path.join(DATA_DIR, 'aliases.sh')
BASH_HISTORY = os.path.join(HOME_DIR, '.bash_history')
DEFAULT_NUM_PREFIXES = 20
FREQ_THRESHOLD = 10

PREFIX_CHOOSERS = [
                     lambda count, ngram: count > 1,
                     lambda count, ngram: len(ngram) > 8 or ' ' in ngram,
                  ]

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
        print 'aliaser created directory "%s" ...' % DATA_DIR

ensure_data_dir()
if not os.path.exists(ALIASES_SH):
    open(ALIASES_SH, 'w').write('')

ALIASES = dbm.open(ALIASES_DB, 'c')
IGNORED = dbm.open(IGNORED_DB, 'c')

def process_history_lines(bh_file):

    freq = {}
    for line in bh_file:
        line = line[:-1]
    
        count = freq.setdefault(line, '0')
        count = str(int(count) + 1)
        freq[line] = count

    return freq

def generate_ngrams(text):
    parts = text.split(' ')
    ngrams = []

    for i in range(len(parts)):
        cur_parts = parts[0:i]
        ngram = ' '.join(cur_parts)
        ngrams.append(ngram)

    return ngrams

def perform_ngram(freq):
    ngrams = {}

    for command in freq.keys():
        count = int(freq[command])
        cur_ngrams = generate_ngrams(command)

        for cngram in cur_ngrams:
            ncount = ngrams.setdefault(cngram, 0)
            ncount = ncount + count
            ngrams[cngram] = ncount

    return ngrams

def regenerate_aliases_sh(aliases):
    keys = aliases.keys()
    keys.sort()

    f = open(ALIASES_SH, 'w')

    for k in keys:
        command = aliases[k]
        command = command.replace('"', r'\"')
        entry = 'alias %s="%s"' % (k, command)

        f.write('%s\n' % entry)

    f.close()

def choose_prefixes(prefixes):
    selected_prefixes = []

    for count, prefix in prefixes:
        reject = True

        for chooser in PREFIX_CHOOSERS:
            if not chooser(count, prefix):
                break
        else:
            reject = False

        if not reject:
            selected_prefixes.append((count, prefix))

    return selected_prefixes

def analyse(num, frequencies):

    aliases = set(ALIASES.keys())
    aliased = [ALIASES[a] for a in aliases]

    aliases = set()

    ignored = set(IGNORED.keys())

    ngrams = perform_ngram(frequencies)
    prefixes = [(v, k) for k, v in ngrams.iteritems()]

    # don't enumerate "aliased" prefixes
    firstterm = lambda x: x.split(' ')[0]
    prefixes = [(count, prefix) for count, prefix in prefixes \
                    if firstterm(prefix) not in aliases]

    prefixes = [(count, prefix) for count, prefix in prefixes \
                    if prefix not in aliased]

    # don't enumerate "ignored" prefixes
    prefixes = [(count, prefix) for count, prefix in prefixes \
                    if prefix not in ignored]

    # ignore prefixes below frequency threshold
    prefixes = [(count, prefix) for count, prefix in prefixes \
                    if count >= FREQ_THRESHOLD]

    prefixes = choose_prefixes(prefixes)

    prefixes.sort()
    prefixes.reverse()

    prefixes = prefixes[:num]
    return prefixes

def add_to_ignored(command):
    ignored = set(IGNORED.keys())
    if command not in ignored:
        IGNORED[command] = '1'
        print 'command/prefix "%s" added to ignore list' % command

def ignore_all(prefixes):
    for command in prefixes:
        add_to_ignored(command)

def do_showfreq(args):
    '''
    Analyses bash history and show frequency of commands.
    aliaser show-freq [commands_file]
    eg: aliaser show-freq
        aliaser show-freq sample.commands
    '''
    infile = None
    if args:
        infile = args[0]

    bh = infile or BASH_HISTORY
    bh = open(bh)
    frequency = process_history_lines(bh)

    entries = []
    for key in frequency.keys():
        value = frequency[key]
        entries.append((int(value), key))
    entries.sort()

    for count, command in entries:
        print count, command

def do_showanalysis(args):
    '''
    Analyses bash history and shows prefix frequency.
    aliaser show-analysis <num> [commands_file]
    eg: aliaser show-analysis 10
        aliaser show-analysis 20 sample.commands
    '''
    infile = None
    if len(args) == 0:
        num = 10

    elif len(args) == 1:
        num = args[0]

    else:
        num, infile = args

    num = int(num)
    bh = infile or BASH_HISTORY
    bh = open(bh)
    frequency = process_history_lines(bh)

    prefixes = analyse(num, frequency)
    for p in prefixes:
        print p

def do_doalias(args):
    '''
    Analyses bash history and prompts you to create aliases
    for most frequent commands.
    eg: aliaser
    '''

    bh = open(BASH_HISTORY)
    frequency = process_history_lines(bh)

    while 1:

        prefixes = analyse(DEFAULT_NUM_PREFIXES, frequency)
        if not prefixes:
            break

        for index, (count, prefix) in enumerate(prefixes):
            print '[%2s]\t%03d times\t%s' % (index, count, prefix)

        prefixes = [prefix for count, prefix in prefixes]

        choice = raw_input('Choice (empty to ignore all, CTRL+C to cancel): ')
        if not choice:
            ignore_all(prefixes)
            continue

        if not choice.isdigit():
            print 'bad  choice'
            continue

        choice = int(choice)

        if choice >= len(prefixes):
            print 'bad choice'
            continue

        alias = raw_input('Alias (empty to ignore, CTRL+C to cancel): ').strip()

        if not alias:
            command = prefixes[choice]
            add_to_ignored(command)
            continue

        command = prefixes[choice]
        do_addalias([alias, command])

def do_showaliases(args):
    '''
    Show aliases which are active.
    eg: aliaser show
    '''
    aliases = ALIASES.keys()
    aliases.sort()

    for a in aliases:
        command = ALIASES[a]
        print '\'%s\'\t --> \t%s' % (a, command)

def do_addalias(args):
    '''
    Add a new alias.
    aliaser <alias> "<command>"
    eg: aliaser add ssh43 "ssh root@192.168.1.43"
    '''

    if len(args) == 2:
        alias, command = args
    else:
        alias = raw_input('alias: ')
        command = raw_input('command: ')

    _command = ALIASES.get(alias)
    if _command:
        print 'Alias already used for command:'
        print _command
        return False

    ALIASES[alias] = command
    regenerate_aliases_sh(ALIASES)
    return True

def do_deletealias(args):
    '''
    Delete an existing alias.
    aliaser '<alias>'
    eg: aliaser delete 'ssh43'
    '''

    i = args[0]
    if ALIASES.has_key(i):
        del ALIASES[i]

def do_showrandom_alias(args):
    '''
    Show a random alias from the ones you created.
    eg: aliaser show-random
    '''

    if args and args[0].isdigit():
        num = int(args[0])
    else:
        num = 1

    aliases = ALIASES.keys()
    if aliases:
        aliases = random.sample(aliases, num)

    for a in aliases:
        command = ALIASES[a]
        print '\'%s\'\t --> \t%s' % (a, command)

def do_showtips(args):
    '''
    Show useful usage tips.
    eg: aliaser show-tips
    '''

    print 'Use aliases to become more productive:'
    do_showrandom_alias(args)

def do_showignored(args):
    '''
    Show list of ignored commands.
    eg: aliaser show-ignored
    '''

    ignored = list(IGNORED.keys())
    ignored.sort()

    for i in ignored:
        print repr(i)

def do_deleteignored(args):
    '''
    Delete an ignore command from list.
    aliaser '<ignore_command>'
    eg: aliaser delete-ignored 'sudo apt-get install'
    '''

    i = args[0]
    if IGNORED.has_key(i):
        del IGNORED[i]

null_command = lambda args: None
null_command.__doc__ = ''

COMMANDS = {
                'do': do_doalias,
                'show': do_showaliases,
                'delete': do_deletealias,
                'add': do_addalias,
                'show-freq': do_showfreq,
                'show-analysis': do_showanalysis,
                'show-ignored': do_showignored,
                'delete-ignored': do_deleteignored,
                'show-random': do_showrandom_alias,
                'show-tips': do_showtips,
                'install': null_command,
           }

def show_help():
    print 'usage: %s <command> <args>' % sys.argv[0]

    commands = COMMANDS.keys()
    commands.sort()

    for c in commands:
        print c
        print '-' * len(c)
        print COMMANDS[c].__doc__.strip()
        print

    print 'help'
    print '----'
    print 'prints the above.'
    print 'eg: aliaser help'

def main(command, args):

    if command == 'help':
        show_help()

    else:

        cmd_fn = COMMANDS.get(command, None)

        if not cmd_fn:
            show_help()
            return

        cmd_fn(args)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        args = sys.argv[2:]

    else:
        command = 'do'
        args = []

    try:
        main(command, args)

    except SystemExit:
        raise

    except KeyboardInterrupt:
        print
