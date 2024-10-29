import sys
import getopt


def parser(argv):
    game_mode = 2
    max_iteration = 10

    # try and catch
    try:
        opts, args = getopt.getopt(argv, "m:i:")
    except getopt.GetoptError:
        sys.stdout.write('usage: main.py [-m game mode][-i max_iteration]'+'\n')
        sys.exit(2)

    # parameter parsing
    for opt, arg in opts:

        # game mode
        if opt == '-m':
            if arg == 'train':
                game_mode = 100
            elif arg == 'free_play':
                game_mode = 2
            elif arg == 'play':
                game_mode = 2
            elif arg == 'auto':
                game_mode = 3
            else:
                sys.stdout.write('usage: -m [train|play|auto]'+'\n')
                sys.exit(2)

        # max_iteration
        elif opt == '-i':
            try:
                arg = int(arg)
                max_iteration = arg
            except ValueError:
                sys.stdout.write('usage: -i max_iteration(integer)'+'\n')
                sys.exit(2)

        # exception
        else:
            sys.stdout.write('usage: main.py [-m game mode][-i max_iteration]'+'\n')
            sys.exit(2)

    # system log
    # sys.stdout.write('game mode: %d' % game_mode+'\n')
    # sys.stdout.write('max iteration: %d' % max_iteration+'\n')

    return game_mode, max_iteration
