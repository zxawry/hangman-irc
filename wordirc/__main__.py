import asyncio

from wordirc.client import Client, NICKNAME, REALNAME, SERVER

def main():
    print('[info]', '[main]', 'application started.')

    bot = Client(NICKNAME, realname=REALNAME)

    try:
        bot.run(SERVER, tls=True, tls_verify=False)
    except BaseException as e:
        print('[debug]', '[main]', e)

    print('[info]', '[main]', 'application shut down.')

if __name__ == '__main__':
    main()
