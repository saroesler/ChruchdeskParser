
# Churchdesk Parser

This is a parser for Churchdesk calendar frames.
With this parser you can export data from the frame into a list of Python dictionaries.
The parser is included into `chruchdeskcalparser.py`
This repository also includes a module for the google Calendar API in
`googlecalapi.py`.


## Example

A small demo is provided in `example.py`.
You can run the example directly and add the churchdesk frame ID as well as your google calendar ID using the command line arguments.

You also can provide the number of days the script should look for appointments in the two calendars.
The script will show you the differences between the Chruchdesk and the Google calendar.
Depending on the arguments you pass the script will create, update or delete the changes in the Google calendar.
## Authors

- [@saroesler](https://www.github.com/saroesler)

