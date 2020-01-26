# PRESENTATION_findShopsByPhone


This is my 6th program on Python. At this point, I had already read a couple of books and a tutorial on this language.

The program is designed to search the store by phone number (or part thereof).
Like previous programs, it interacts with a specific database and contains confidential information,
which was cut from the screenshots.

This time the GUI was made on the basis of the wonderful PyQT module.

Features:

- Accepts the number even in extra characters (such as dashes, for example), allows the absence of the number "8", or
the presence of "7" instead of "+7", and also supports short IP-telephony numbers.
- User friendly, intuitive graphical interface
- The program is also compiled into an executable exe file, after which all files have been cleaned to
reduce the size from 100 Mb to 25 Mb.
- There is a convenient installer

Despite all these advantages, the program, as mentioned earlier, is intended for internal corporate use.
and without a correct setting of the main file to get the correct data, it will not work correctly

Used modules:

  PyQt5,
  sys,
  pyodbc
