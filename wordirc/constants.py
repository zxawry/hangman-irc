import os

SERVER = os.environ["SERVER_ADDRESS"]
CHANNEL = os.environ["CHANNEL_NAME"]

NICKNAME = 'WordBot'
REALNAME = 'WordBot'

WORDS = './wordirc/words.txt'

# Charcters used to draw word box
# Not every client supports uincode.
# Use ascii instead.
HS = '-' #'\u2500'  # Horizontal Space
VS = '|' #'\u2502'  # Vertical Space
TE = ' ' #'\u252c'  # Top Edge
BE = ' ' #'\u2534'  # Bottom Edge
TLC = ' ' #'\u250c' # Top Left Corner
TRC = ' ' #'\u2510' # Top Right Corner
BLC = ' ' #'\u2514' # Bottom Left Corner
BRC = ' ' #'\u2518' # Bottom Right Corner
