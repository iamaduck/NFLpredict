from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.toast import toast
from kivymd.uix.bottomsheet import MDListBottomSheet
import numpy as np

# due to melo being old, np.float has to be changed to float and np.asscalar(x) has to be changed to x.item()
# i've submitted these changes as a fork
from melo import Melo

__version__ = "0.1.3"

class Predict(MDApp):

    teamcodes = { 'ARI': 'ARI - Arizona Cardinals', 'ATL': 'ATL - Atlanta Falcons', 'BAL': 'BAL - Baltimore Ravens', 'BUF': 'BUF - Buffalo Bills', 'CAR': 'CAR - Carolina Panthers', 'CHI': 'CHI - Chicago Bears', 'CIN': 'CIN - Cincinnati Bengals', 'CLE': 'CLE - Cleveland Browns', 'DAL': 'DAL - Dallas Cowboys', 'DEN': 'DEN - Denver Broncos', 'DET': 'DET - Detroit Lions', 'GB': ' GB - Green Bay Packers', 'HOU': 'HOU - Houston Texans', 'IND': 'IND - Indianapolis Colts', 'JAX': 'JAX - Jacksonville Jaguars', 'KC': ' KC - Kansas City Chiefs', 'LAC': 'LAC - Los Angeles Chargers', 'LA': 'LA  - Los Angeles Rams', 'LV': ' LV - Las Vegas Raiders', 'MIA': 'MIA - Miami Dolphins', 'MIN': 'MIN - Minnesota Vikings', 'NE': ' NE - New England Patriots', 'NO': ' NO - New Orleans Saints', 'NYG': 'NYG - New York Giants', 'NYJ': 'NYJ - New York Jets', 'PHI': 'PHI - Philadelphia Eagles', 'PIT': 'PIT - Pittsburgh Steelers', 'SEA': 'SEA - Seattle Seahawks', 'SF': ' SF - San Francisco 49ers', 'TB': ' TB - Tampa Bay Buccaneers', 'TEN': 'TEN - Tennessee Titans', 'WAS': 'WAS - Washington Football Team' }

    def build(self):
        self.theme_cls.primary_palette = "Purple"
        return Builder.load_file('main.kv')

    def select_callback(self, hometeam, *args):

        if hometeam:
            self.root.ids.home.text = args[0]
            toast(f'Changed HOME to {args[0]}')
        else:
            self.root.ids.away.text = args[0]
            toast(f'Changed AWAY to {args[0]}')

    def select(self, hometeam):

        bottom_sheet_menu = MDListBottomSheet()

        for short, name in self.teamcodes.items():
            bottom_sheet_menu.add_item(name, lambda x, y=hometeam, z=short: self.select_callback(y, z))

        bottom_sheet_menu.open()

    def submit(self):
        
        home = self.root.ids.home.text
        away = self.root.ids.away.text

        if home not in self.teamcodes and away not in self.teamcodes:
            self.root.ids.show.text = "HOME and AWAY team codes are not valid."
        elif home not in self.teamcodes:
            self.root.ids.show.text = "HOME team code is not valid."
        elif away not in self.teamcodes:
            self.root.ids.show.text = "AWAY team code is not valid."
        else:
            #open data from file nfl.dat
            f = open('nfl.dat', 'r')
            data = f.read().splitlines()
            dates, teams_home, scores_home, teams_away, scores_away = zip(
                *[l.split() for l in data[1:]])

            # define a binary comparison statistic
            spreads = [int(h) - int(a) for h, a
                in zip(scores_home, scores_away)]

            # hyperparameters and options
            k = 0.245
            lines = np.arange(-50.5, 51.5)
            regress = lambda months: .413 if months > 3 else 0
            regress_unit = 'month'
            commutes = False

            # initialize the estimator
            nfl_spreads = Melo(k, lines=lines, commutes=commutes,
                            regress=regress, regress_unit=regress_unit)

            # fit the estimator to the training data
            nfl_spreads.fit(dates, teams_home, teams_away, spreads)

            # specify a comparison time
            time = nfl_spreads.last_update

            # predict the mean outcome at that time
            mean = nfl_spreads.mean(time, home, away)

            if mean == 0:
                self.root.ids.show.text = f'Mean is {abs(mean)}, pick your favourite!'
            elif mean < 0:
                self.root.ids.show.text = f'{away} -{round(abs(mean), 2)} (Raw: {mean})'
            elif mean > 0:
            	self.root.ids.show.text = f'{home} -{round(abs(mean), 2)} (Raw: {mean})'

Predict().run()