import pydle

from wordirc.game import Game
from wordirc.utils import draw, pick
from wordirc.constants import *
from wordirc.dialogues import *

class Client(pydle.Client):
    async def on_connect(self):
        self.game = Game()

        await self.join(CHANNEL)

    async def on_message(self, target, source, message):
        if source == self.nickname:
            return

        if not message.startswith('!'):
            return

        text = message.removeprefix('!')
        text = text.lower()
        text = text.strip()

        nick = source

        if len(text) == 1 and text.isalpha():
            if target == CHANNEL:
                await self.do_guess(nick, text)
            else: # target == self.nickname
                await self.message(nick, pick(MESSAGE_SNEAK))
        elif text == 'quit':
            await self.part(CHANNEL, text)
            await self.quit(text)
        elif text == 'help':
            await self.message(nick, pick(MESSAGE_HELP))
        else:
            # unrecognised command
            await self.message(nick, pick(MESSAGE_UNKNOWN))

    async def on_join(self, channel, user):
        print('[debug]', '[client]', '{} joined {}'.format(user, channel))

        if user == self.nickname:
            await self.set_topic(CHANNEL, pick(JOIN_TOPIC))
            return

        nick = user

        status = self.game.append(nick)
        if status == 1:
            await self.message(nick, pick(JOIN_PLAYER))
        else:
            await self.message(nick, pick(JOIN_FRESH))

        if self.game.is_active():
            await self.message(nick, pick(JOIN_WAIT))
        else:
            await self.message(nick, pick(JOIN_START))
            await self.do_start()

    async def on_part(self, channel, user, message):
        print('[debug]', '[client]', '{} parted {}'.format(user, channel))

        if user == self.nickname:
            return

        nick = user

        status = self.game.remove(nick)
        if status == 1:
            await self.message(CHANNEL, pick(PART_UNKNOWN))
        else:
            await self.message(CHANNEL, pick(PART_PLAYER))

    async def on_unknown(self, message):
        print('[debug]', '[client]', 'unkonwn command received')

    # begining of private action methods

    async def do_start(self):
        status = self.game.start()
        if status == 1:
            await self.message(CHANNEL, pick(START_EMPTY))
        else:
            # inform all players about their assinged chances.
            for player in self.game.players.values():
                await self.message(player.nick, pick(START_INFORM).format(player.chances))
            # announce start of new round publicly.
            await self.message(CHANNEL, pick(START_READY))
            await self.do_print()

    async def do_guess(self, nick, text):
        status = self.game.guess(nick, text)
        if status == 1:
            await self.message(nick, pick(GUESS_UNKNOWN))
        elif status == 2:
            await self.message(nick, pick(GUESS_TURN))
        elif status == 3:
            await self.message(nick, pick(GUESS_BURNT))
        elif status == 4:
            await self.message(CHANNEL, pick(GUESS_REPEATED).format(nick))
            await self.do_inform(nick)
        elif status == 5:
            await self.message(CHANNEL, pick(GUESS_INCORRECT).format(nick))
            await self.do_inform(nick)
        else:
            await self.message(CHANNEL, pick(GUESS_CORRECT).format(nick))

        if status >= 4 or status == 0:
            await self.do_recap()

    async def do_recap(self):
        status = self.game.recap()
        if status == 1:
            await self.message(CHANNEL, pick(RECAP_EMPTY))
        elif status == 2:
            await self.message(CHANNEL, pick(RECAP_REVEALED).format(self.game.turns[0].nick))
            await self.do_start()
        elif status == 3:
            await self.message(CHANNEL, pick(RECAP_BURNT))
            await self.message(CHANNEL, draw(self.game.wordbox.letters))
            await self.do_start()
        else:
            await self.do_print()

    async def do_print(self):
        await self.message(CHANNEL, pick(PRINT_TURN).format(self.game.turns[0].nick))
        await self.message(CHANNEL, draw(self.game.wordbox.guessed))

        chances = str()

        for player in self.game.turns:
            chances += ' {} '.format('*' if player == self.game.turns[0] else ' ')
            chances += '{}: {}\t'.format(player.nick, player.chances)

        if len(chances) > 0:
            await self.message(CHANNEL, chances)

    async def do_inform(self, nick):
        if nick not in self.game.players.keys():
            return

        player = self.game.players[nick]

        if player.is_burnt():
            await self.message(CHANNEL, pick(INFORM_BURNT).format(nick))
