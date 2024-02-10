import numpy as np
import PySide6
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QListWidget, QListWidgetItem, QMainWindow,
    QMenuBar, QSizePolicy, QSplitter, QStatusBar,
    QToolButton, QWidget, QSpacerItem)


class Player:
    def __init__(self, name, points=0):
        self.name = name
        self.points = points
        self.team = None
        # self.conditions = []

    def __str__(self):
        return f"({self.name}, {self.points})"

    def __repr__(self):
        return self.__str__()

    def win(self):
        self.points += 1

    def loose(self):
        self.points -= 1


class Team:
    def __init__(self, name=None, players: list = None, offset=0):
        self.players = players if players else []
        self.name = name
        self.points = 0
        self.offset = offset
        for player in self.players:
            self.points += player.points

    def __str__(self):
        return f"({self.name}, {self.points}, {self.players})"

    def __repr__(self):
        return self.__str__()

    def add_player(self, player):
        if len(self.players) < 5:
            self.players.append(player)
            self.points += player.points + self.offset
            return True
        return False

    def win(self):
        for player in self.players:
            player.win()
            self.points += 1

    def loose(self):
        for player in self.players:
            player.loose()
            self.points -= 1

    def apply_offset(self, offset):
        self.offset = offset
        self.points += self.offset * len(self.players)

    def remove_offset(self):
        self.points -= self.offset * len(self.players)
        self.offset = 0


class Tournament:
    def __init__(self, teams_num, prep_games_num, bo, window_system):
        self.win_system = window_system
        self.teams_num = teams_num
        self.prep_games_num = prep_games_num
        self.bo = bo

        self.players = []
        self.teams = []
        self.current_game_num = 0
        self.bracket = []

        self.final_teams = []
        # self.players_per_team = []

    def register_player(self, name):
        self.players.append(Player(name))

    def generate_first_time_teams(self):
        ratio = self.teams_num // len(self.players)
        rest = self.teams_num % len(self.players)
        self.players_per_team = [ratio for _ in range(len(self.players) - rest)] + [ratio + 1 for _ in range(rest)]

        rng = RandNumNoRepeat(len(self.players))

        for i in range(self.teams_num):
            team = Team(f'Team {i + 1}')
            for _ in range(self.players_per_team[i]):
                team.add_player(self.players[rng.get()])
            self.teams.append(team)

    def generate_random_teams(self):
        if self.current_game_num == 0:
            self.generate_first_time_teams()
        else:
            def min_of_arr(array, key=lambda x: x):
                index = -1
                val = float('inf')
                for i, e in enumerate(array):
                    e = key(e)
                    if e < val:
                        val = e
                        index = i
                return index, val

            min_points = abs(min_of_arr(self.players, key=lambda player: player.points)[1])

            players = sorted(self.players, key=lambda player: -player.points)

            team_size = len(players) // self.teams_num

            tmp_teams = [Team(f"Team {i}", offset=min_points) for i in range(self.teams_num)]
            self.teams = []

            for p in players:
                argmin = min_of_arr(tmp_teams, lambda x: x.points)[0]
                tmp_teams[argmin].add_player(p)

                if len(tmp_teams[argmin].players) >= team_size:
                    self.teams.append(tmp_teams[argmin])
                    self.teams[-1].remove_offset()
                    tmp_teams.pop(argmin)
                    if len(tmp_teams) == 0:
                        break

    def create_teams(self):
        self.current_game_num += 1

        if self.current_game_num < self.prep_games_num:
            return self.generate_random_teams()
        elif self.final_teams:
            return self.final_teams
        elif self.current_game_num - self.prep_games_num != self.bo:
            return self.generate_random_teams()
        else:
            return None

    def ask_for_winner(self, pair):
        res = self.win_system.get_pair(pair)
        self.bracket[pair][res].win()
        self.bracket[pair][abs(res - 1)].lose()

    def update(self):
        print(self.teams, self.current_game_num)
        for duel in self.bracket:
            self.ask_for_winner(*duel)

    def main(self):
        if len(self.players) < 2:
            print('Not enough players')
            return
        self.generate_first_time_teams()
        self.update()

        for _ in range(self.prep_games_num - 1):
            self.generate_random_teams()
            self.update()

        self.generate_random_teams()
        for _ in range(self.bo):
            self.update()


class MainManager(QApplication):
    def __init__(self):
        super().__init__()
        self.main_win = QMainWindow()

        self.main_win.setObjectName(u"MainWindow")
        self.main_win.resize(800, 600)
        self.centralwidget = QWidget(self.main_win)
        self.centralwidget.setObjectName(u"centralwidget")
        self.splitter_2 = QSplitter(self.centralwidget)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setGeometry(QRect(30, 10, 286, 73))
        self.splitter_2.setOrientation(Qt.Horizontal)
        self.splitter_2.setOpaqueResize(False)
        self.listWidget = QListWidget(self.splitter_2)
        QListWidgetItem(self.listWidget)
        self.listWidget.setObjectName(u"listWidget")
        self.splitter_2.addWidget(self.listWidget)
        self.splitter = QSplitter(self.splitter_2)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.toolButton = QToolButton(self.splitter)
        self.toolButton.setObjectName(u"toolButton")
        font = QFont()
        font.setFamilies([u"Pixelify Sans"])
        font.setPointSize(15)
        font.setBold(True)
        font.setUnderline(False)
        font.setKerning(True)
        font.setStyleStrategy(QFont.NoAntialias)
        self.toolButton.setFont(font)
        self.toolButton.setMouseTracking(False)
        self.toolButton.setText(u"+")
        self.splitter.addWidget(self.toolButton)
        self.toolButton_2 = QToolButton(self.splitter)
        self.toolButton_2.setObjectName(u"toolButton_2")
        self.toolButton_2.setFont(font)
        self.toolButton_2.setMouseTracking(False)
        self.toolButton_2.setText(u"-")
        self.splitter.addWidget(self.toolButton_2)
        self.splitter_2.addWidget(self.splitter)
        self.main_win.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(self.main_win)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        self.main_win.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self.main_win)
        self.statusbar.setObjectName(u"statusbar")
        self.main_win.setStatusBar(self.statusbar)

        self.main_win.show()


class RandNumNoRepeat:
    def __init__(self, number):
        num = np.arange(0, number)
        generator = np.random.default_rng()
        generator.shuffle(num)
        self.numbers = list(num)

    def get(self):
        if self.numbers:
            return self.numbers.pop(0)
        return None


if __name__ == '__main__':
    MainManager.setStyle('Fusion')
    app = MainManager()
    app.setStyleSheet('')
    app.exec()
