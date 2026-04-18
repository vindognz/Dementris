from game import Game


def main():
    game = Game()
    game.show_start_screen()

    while game.running:
        game.new()
        game.run()
        game.show_go_screen()


if __name__ == "__main__":
    main()
