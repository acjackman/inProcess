# inProcess
Parse and process a structured text file. There are some very common notes such as tasks and calendar events that we make that we could have to computer file instead of doing it manually. This script allows you to write a single continuous stream of thought document in a markdown-like syntax, and then have it parsed intelligently, leaving only the things that a computer can't handle for you to deal with.

# Parseable objects
### Calendar
    !@ Fantasical Calendar event

### Tasks

    !- Single line task

With Notes:

    !- Task with notes
    Note Line 1
    Note Line 2
    Note Line 3

There must be a newline after the last note to indicate the end of Task notes and the beginning of the next item.

`otask` also provides some options for setting task properties

* `@context` (fragment, no spaces)
* `#project` (fragment, no spaces)
* `due(due date)` (can be shortened as `d(date)`)
* `start(start date)` (can be shortened as `s(date)`)
* `(notes)` (inProcess only supports in single line tasks)
* ` !`    sets task as flagged (Must be at the end of the line)

### Journal Entries

    Journal 2013-04-07T19:53:44
    _Entry text_
    * * * * * *

### Food Log

    Food 2013-04-07T19:53:44
    Orange
    2 slices pizza
    2 cookies
    2 cookies --- Grandma's best recipe yet
    @ Location ate at
    > Location from
    * * * * * *

* `@` is where the food was eaten
* `>` should be specified when the `@` location is not where the food was prepared/from.

### Life track

    Life Track: 2013-04-07T20:18:59 --- Entry

### Health track

    Health Track: 2013-04-07T20:18:59 --- Entry


# Requirements
The script is written against Python 2.7, and is the only requirement for the base functionality. However, some parsers require additional applications to record the idetified information.

* Tasks are recorded in OmniFocus using Brett Terbstra's `otask` script
* Journal Entries are recorded using Day One's CLI interface
* Calendar events are parsed and recorded via Fantastical's AppleScript interface
