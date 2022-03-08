import random
#random.seed(114514)

class Card():
    def __init__(self, val) -> None:
        self.black = (val % 2 == 0)
        self.val = val
        self.visible = False
        self.upper_bound = None
        self.lower_bound = None
        self.possible_value = None



    def show(self):
        self.visible = True
        self.upper_bound = self.val
        self.lower_bound = self.val

class Player():
    deck: list[Card] = []
    alive = True
    other = None
    def __init__(self, alpha) -> None:
        self.alpha = alpha
        self.deck = []
        self.guessed = []

    def pickup(self, card):
        self.deck.append(card)
        self.deck.sort(key = lambda x: x.val)

    def guess_right(self):
        #print(f"player{self.alpha} start guessing")
        #print(f"player{self.alpha}'s deck:", [card.val for card in self.deck])
        #print(f"player{self.other.alpha}'s deck:", [(card.visible, card.val) for card in self.other.deck])
        chosen_card = self.guessing_list()[0]
        guess_value = chosen_card.possible_value[0]
        #self.guessed.append(guess_value)
        #choices = chosen_card.possible_value
        #print("chosen card value:", chosen_card.val, "guessed value:", guess_value)
        if guess_value == chosen_card.val:
            chosen_card.show()
            return True

        return False

    def guessing_list(self) -> list[Card]:
        self.other.set_possible_values(self.visibles())
        guessing_list = [card for card in self.other.deck if not card.visible]
        guessing_list.sort(key = lambda x: len(x.possible_value))
        #print(f"player{self.other.alpha}'s deck:", [(card.visible, card.possible_value) for card in self.other.deck])
        return guessing_list

    def set_last_upper_bound(self, visibles):
        card = self.deck[-1]
        if card.visible: 
            card.upper_bound = card.val
            return
        if card.black:
            start = 22
        else:
            start = 23
        while start in visibles: start -= 2
        card.upper_bound = start
        
    def set_first_lower_bound(self, visibles):
        card = self.deck[0]
        if card.visible: 
            card.lower_bound = card.val
            return
        if card.black:
            start = 0
        else:
            start = 1
        while start in visibles: start += 2
        card.lower_bound = start

    def set_all_lower_bounds(self, visibles):
        deck = self.deck
        for i in range(1, len(deck)):
            card = deck[i]
            previous_card = deck[i-1]
            if card.visible: continue
            if card.black != previous_card.black: start = previous_card.lower_bound + 1
            else: start = previous_card.lower_bound + 2
            while start in visibles: start += 2
            card.lower_bound = start
    
    def set_all_upper_bounds(self, visibles):
        deck = self.deck
        for i in range(1, len(deck)):
            card = deck[len(deck)-i-1]
            previous_card = deck[len(deck)-i]
            if card.visible: continue
            if card.black != previous_card.black: start = previous_card.upper_bound - 1
            else: start = previous_card.upper_bound - 2
            while start in visibles: start -= 2
            card.upper_bound = start

    def set_possible_values(self, visibles):
        self.set_first_lower_bound(visibles)
        self.set_last_upper_bound(visibles)
        self.set_all_upper_bounds(visibles)
        self.set_all_lower_bounds(visibles)
        for card in self.deck:
            if card.visible: continue
            card.possible_value = list()
            for num in range(card.lower_bound, card.upper_bound+1, 2):
                if num in visibles: continue
                card.possible_value.append(num)

    def visibles(self):
        visibles = set()
        visibles.update([card.val for card in self.deck])
        visibles.update([card.val for card in self.other.deck if card.visible])
        #visibles.update(self.other.guessed)
        return visibles

    def alive(self):
        for card in self.deck:
            if not card.visible: return True
        return False

class Game():
    turns = 0
    deck = []
    #player1: None
    def __init__(self, alpha1, alpha2, reverse = False) -> None:
        self.deck = []
        self.turns = 0
        
        player1 = Player(alpha1)
        player2 = Player(alpha2)
        player2.other = player1
        player1.other = player2
        self.player1 = player1
        self.player2 = player2
        self.reverse = reverse
        #self.player1.other = self.player2
        #self.player2.other = self.player1

        for i in range(24): self.deck.append(Card(i))
        self.deck.sort(key=lambda x: random.random())

        for i in range(4): self.player1.pickup(self.get_card())
        for i in range(4): self.player2.pickup(self.get_card())

    def get_card(self) -> Card: return self.deck.pop()

    def play(self):
        while True:
            if self.reverse:
                self.one_turn(self.player2)
                if not self.player1.alive(): return 1
                self.one_turn(self.player1)
                if not self.player2.alive(): return 0
            else:
                self.one_turn(self.player1)
                if not self.player2.alive(): return 0
                self.one_turn(self.player2)
                if not self.player1.alive(): return 1

    def one_turn(self, player1: Player):
        card = self.get_card()
        player1.pickup(card)
        if player1.guess_right():
            while True:
                lst = player1.guessing_list()
                if len(lst) < 1 or len(lst[0].possible_value) > 1: break
                #print(f"player{player1.alpha} guessed again")
                player1.guess_right()
            if player1.alpha > self.turns: return
            while player1.other.alive() and player1.guess_right(): pass
            card.show()
        else: card.show()

class Game2(Game):
    def play(self):
        
        while True:
            if self.reverse:
                self.one_turn(self.player2)
                if not self.player1.alive(): return 1
                self.one_turn2(self.player1)
                if not self.player2.alive(): return 0
            else:
                self.one_turn2(self.player1)
                if not self.player2.alive(): return 0
                self.one_turn(self.player2)
                if not self.player1.alive(): return 1
        

    def one_turn2(self, player1: Player):
        card = self.get_card()
        player1.pickup(card)
        if player1.guess_right():
            while True:
                if not self.continues(player1): return
                #print(f"player{player1.alpha} guessed again")
                if not player1.guess_right():
                    card.show()
                    break
        else: card.show()

    def continues(self, player1):
        lst = player1.guessing_list()
        if len(lst) < 1: return False
        values = len(lst[0].possible_value)
        choices = len([card for card in player1.other.deck if not card.visible])
        if values > 2: return False
        if values == 2 and choices > player1.alpha: return False
        return True
                
class Game3(Game2):
    def continues(self, player1: Player):
        lst = player1.guessing_list()
        if len(lst) < 1: return False
        if len(lst[0].possible_value) > player1.alpha : return False
        return True

class Game4(Game2):
    
    def one_turn(self, player1: Player):
        card = self.get_card()
        player1.pickup(card)
        if player1.guess_right():
            while True:
                if not super().continues(player1): return
                #print(f"player{player1.alpha} guessed again")
                if not player1.guess_right():
                    card.show()
                    break
        else: card.show()
    
    def continues(self, player1):
        #return super().continues(player1)
        lst = player1.guessing_list()
        if len(lst) < 1: return False
        choices = len([card for card in player1.other.deck if not card.visible])
        chance = len([card for card in player1.deck if not card.visible])
        values = len(lst[0].possible_value)
        #if 1/values < ratio and values > 1: return False
        if values > 2: return False
        if values == 1: return True
        if choices >= 3 or choices >= chance: return False
        return True

def simluation(alpha1, alpha2):
    result = ""
    for i in range(50000):
        #print("new game!!!!\n\n\n\n\n")
        result += str(Game4(alpha1, alpha2).play())
        #print("new game!!!!\n\n\n\n\n")
        result += str(Game4(alpha1, alpha2, True).play())
    return result

"""
#simluation(0, 7)
result = simluation(1,2)
from temp10 import count
print(count(result))
import json
"""
"""
from utils.threadsafe import threadsafe_file, exec_gen

def fn(item, file):
    print(item)
    try:
        i, j = item
        file.write(f"{i}{j} {simluation(i, j)}\n")
        print(f"{i}{j} completed")
    except Exception as e:
        print(e)
def iter():
    for i in range(8):
        for j in range(8):
            yield (i, j)

exec_gen(fn, iter(), threadsafe_file(open('davinci2.txt', mode='w')))
"""
"""
d = {}
for i in range(8):
    for j in range(8):
        d[f"{i}{j}"] = simluation(i, j)
        print(f"{i}{j} completed")
json.dump(d, open('davinci5.json', mode='w'))
"""