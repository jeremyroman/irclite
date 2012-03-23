import irclite
import pwd

@irclite.observe('jbromanbot: whois (\w+)')
def whois(event, username):
    try:
        passwd = pwd.getpwnam(username)
        event.respond(passwd.pw_gecos)
    except KeyError:
        event.respond('person not found')

count = 0
@irclite.observe('jbromanbot: count')
def counter(event):
    global count
    count = count + 1
    event.respond(str(count))

stack = []

@irclite.observe('jbromanbot: push (.*)')
def push(event, thing):
    stack.append(thing)
    event.respond('OK. Stack now has size %d.' % len(stack))

@irclite.observe('jbromanbot: pop')
def pop(event):
    try:
        what = stack.pop()
        event.respond(what)
    except IndexError:
        event.respond('stack is empty')

@irclite.observe('jbromanbot: help')
def help(event):
    event.respond("""Permitted commands:
whois [username]
count
push [string]
pop""")


irclite.run('/tmp/irctest/irc.freenode.net', ['#jbroman-test'])
