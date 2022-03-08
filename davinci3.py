from davinci import Card, Player, Game2
import random

dp = {}

def to_str(d1: list[Card], d2: list[Card]):
    res = ""
    for card in d1:
        num = card.val*2
        if card.visible: num += 1
        res += str(num)
    res += "&"
    for card in d2:
        num = card.val*2
        if card.visible: num += 1
        res += str(num)
    return res

def possible_combinations(visibles: set, d2: list[Card]):
    if len([card for card in d2 if not card.visible]) == 0:
        res = set([i for i in range(24)])
        return [], res.difference(visibles)
    res = []
    for i in range(len(d2)):
        card = d2[i]
        res.append(card.val)
        if card.visible: continue
        #if not card.possible_value: continue
        card.visible = True
        
        for val in card.possible_value:
            if i > 0 and d2[i-1].val >= val: continue
            if card.val in visibles: continue
            card.val = val
            visibles.add(val)
            for res2, remain in possible_combinations(visibles, d2):
                yield res + res2, remain
            visibles.discard(val)
        res = []
        card.visible = False

def possible_deck(visibles: set, d2: list[Card], p4: Player):
    for res, remain in possible_combinations(visibles, d2):
        deck = p4.deck

        yield [Card(i) for i in res], [Card(i) for i in remain]

def copy_card(c: Card):
    res = Card(c.val)
    res.visible = c.visible
    if c.visible:
        res.lower_bound = res.val
        res.upper_bound = res.val
    return res

def copy_player(p1: Player, p2: Player):
    p3 = Player(p1.alpha)
    p4 = Player(p2.alpha)
    p3.deck = [copy_card(card) for card in p1.deck]
    p4.deck = [copy_card(card) for card in p2.deck]
    p3.other = p4
    p4.other = p3
    return p3, p4

def eval2_reguess(p1: Player, p2: Player, remain: list[Card], val:int):
    if not p1.alive(): return 1
    if not p2.alive(): return 0
    p3, p4 = copy_player(p1, p2)
    guessing_list = p4.guessing_list()
    guess_card = guessing_list[0]
    values = len(guess_card.possible_value)
    choices = len([card for card in p1.other.deck if not card.visible])
    if values > 2: continues = False
    elif values == 2 and choices > 2: continues = False
    else: continues = True
    if continues: 
        guess_card.visible = True
        n = len(guess_card.possible_value)
        right_win_rate = eval2_reguess(p3, p4, remain, val)
        if n == 1: return right_win_rate
        for card in p4.deck: 
            if card.val == val: new_card = card
        new_card.visible = True
        wrong_win_rate = eval1(p3, p4, remain)
        return (right_win_rate + wrong_win_rate*(n-1))/n
    else:
        return eval1(p3, p4, remain)

def eval2(p1: Player, p2: Player, remain: list[Card]):
    if len(remain) == 0: return 0
    if not p1.alive(): return 1
    if not p2.alive(): return 0
    p3, p4 = copy_player(p1, p2)
    remain = [copy_card(card) for card in remain]
    new_card = remain.pop()
    p4.pickup(new_card)
    guess_card = p4.guessing_list()[0]
    n = len(guess_card.possible_value)
    guess_card.visible = True
    right_win_rate = eval2_reguess(p3, p4, remain, new_card.val)
    guess_card.visible = False
    new_card.visible = True
    wrong_win_rate = eval1(p3, p4, remain)
    return (right_win_rate + wrong_win_rate*(n-1))/n

def eval1_reguess(p1: Player, p2: Player, remain: list[Card], val, return_choice = False):
    if not p1.alive(): return 1
    if not p2.alive(): return 0
    p3, p4 = copy_player(p1, p2)
    #print(val)
    #print([card.val for card in p3.deck])
    guessing_list = p3.guessing_list()
    guess_card = guessing_list[0]
    n = len(guess_card.possible_value)
    guess_card.visible = True
    right_win_rate = eval1_reguess(p3, p4, remain, val)
    if n == 1:
        reguess_win_rate = right_win_rate
    else:
        guess_card.visible = False
        new_card = None
        
        for card in p3.deck: 
            if card.val == val: new_card = card
        new_card.visible = True
        wrong_win_rate = eval1(p3, p4, remain)
        reguess_win_rate = (right_win_rate + wrong_win_rate*(n-1))/n
    skip_win_rate = eval2(p3, p4, remain)
    if return_choice: return reguess_win_rate < skip_win_rate
    else: return min(reguess_win_rate, skip_win_rate)
        

def eval1(p1: Player, p2: Player, remain: list[Card]):
    if len(remain) == 0: return 1
    if not p1.alive(): return 1
    if not p2.alive(): return 0
    p3, p4 = copy_player(p1, p2)
    remain = [copy_card(card) for card in remain]
    new_card = remain.pop()
    p3.pickup(new_card)
    guessing_list = p3.guessing_list()
    guess_card = guessing_list[0]
    n = len(guess_card.possible_value)
    guess_card.visible = True
    right_win_rate = eval1_reguess(p3, p4, remain, new_card.val)
    guess_card.visible = False
    new_card.visible = True
    wrong_win_rate = eval2(p3, p4, remain)
    return (right_win_rate + wrong_win_rate*(n-1))/n

class Game114514(Game2):
    def one_turn2(self, player1: Player):
        card = self.get_card()
        player1.pickup(card)
        if player1.guess_right():
            while True:
                if not self.continues(player1, card): return
                #print(f"player{player1.alpha} guessed again")
                if not player1.guess_right():
                    card.show()
                    break
        else: card.show()
    
    def continues(self, player1, card):
        lst = player1.guessing_list()
        if len(lst) < 1: return False
        values = len(lst[0].possible_value)
        choices = len([card for card in player1.other.deck if not card.visible])
        if values > 2: return False
        if values == 2 and choices > player1.alpha: return False
        if values == 2: return eval1_reguess(self.player1, self.player2, self.deck, card.val, return_choice=True)
        return True

    def one_turn(self, player1: Player):
        card = self.get_card()
        player1.pickup(card)
        if player1.guess_right():
            while True:
                if not self.continues2(player1): return
                #print(f"player{player1.alpha} guessed again")
                if not player1.guess_right():
                    card.show()
                    break
        else: card.show()

    def continues2(self, player1):
        lst = player1.guessing_list()
        if len(lst) < 1: return False
        values = len(lst[0].possible_value)
        choices = len([card for card in player1.other.deck if not card.visible])
        if values > 2: return False
        if values == 2 and choices > player1.alpha: return False
        return True

def simluation(alpha1, alpha2):
    result = ""
    for i in range(5000):
        #print("new game!!!!\n\n\n\n\n")
        result += str(Game114514(alpha1, alpha2).play())
        #print("new game!!!!\n\n\n\n\n")
        result += str(Game114514(alpha1, alpha2, True).play())
        #print(result)
    return result

result = simluation(2,2)
from temp10 import count
for i in range(10): print(count(simluation(2,2)))