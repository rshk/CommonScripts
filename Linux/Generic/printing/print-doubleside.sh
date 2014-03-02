#!/bin/bash

## Use lpr to print double-sided pages.

##============================================================
## NOTE: Right now, we're only supporting printers like
## the one described in the first case. In the other case,
## just swap the commands.
##============================================================

##------------------------------------------------------------
## Instructions for printers printing like this:
##
##     _______
##  ,-'    ^,__ stuff gets printed here
## ( O
##  `-,_______
##
##
## 1. Print even pages   2. Put the stack   3. Print odd pages
##    in reverse order      back on tray       in normal order
##
##         LAST
##     +----------+         +----------+        +----------+
##     | -blank-  |         | -blank-  |        |  page 1  |
##     |  page 2  |         |  page 2  |        |  page 2  |
##     +----------+         +----------+        +----------+
##     | -blank-  |         | -blank-  |        |  page 3  |
##     |  page 4  |         |  page 4  |        |  page 4  |
##     +----------+         +----------+        +----------+
##     | -blank-  |         | -blank-  |        |  page 5  |
##     |  page 6  |         |  page 6  |        |  page 6  |
##     +----------+         +----------+        +----------+
##         FIRST             ===TRAY===         |  page 7  |
##                                              |          |
##                                              +----------+
##
##------------------------------------------------------------

##------------------------------------------------------------
## Instructions for printers printing like this:
##
##  \
##   \         ,--- stuff will be printed here
##    \        v
##     '-,___________
##
##
## 1. Print even pages   2. Put the stack   3. Print odd pages
##    in normal order      back on tray       in reverse order
##
##                                                 LAST
##                          +----------+        +----------+
##                          | -blank-  |        |  page 1  |
##         LAST             | -blank-  |        |  page 2  |
##     +----------+         +----------+        +----------+
##     |  page 6  |         |  page 6  |        |  page 3  |
##     | -blank-  |         | -blank-  |        |  page 4  |
##     +----------+         +----------+        +----------+
##     |  page 4  |         |  page 4  |        |  page 5  |
##     | -blank-  |         | -blank-  |        |  page 6  |
##     +----------+         +----------+        +----------+
##     |  page 2  |         |  page 2  |        |  page 7  |
##     | -blank-  |         | -blank-  |        |          |
##     +----------+         +----------+        +----------+
##         FIRST             ===TRAY===            FIRST
##
## WARNING! If you're printing an odd number of pages, you
## need to add an extra sheet on top of the stack before
## printing, to pad for the (missing) last even page!
##------------------------------------------------------------

echo "Ready to print even pages. Press ENTER when you're ready."
read
echo "Printing even pages in reverse order.."
lpr -o page-set=even -o outputorder=reverse "$@"


cat <<EOF
----------------------------------------------------------------------
		       DONE PRINTING EVEN PAGES
----------------------------------------------------------------------

		You should now have a stack like this:

		 [TRAY] pg6 --- | pg4 --- | pg2 --- |

	Now put it back on the loading tray in the exact same
       fashion, but rotate it 180 degrees on the vertical axys:

		 [TRAY] pg6 --- | pg4 --- | pg2 --- |

**********************************************************************

	  WARNING! Remember to rotate the stack 180 degrees!

**********************************************************************

EOF


echo "Ready to print odd pages. Press ENTER when you're ready."
read
echo "Printing odd pages.."
lpr -o page-set=odd "$@"

echo "Done. Hopefully we saved another tree."
