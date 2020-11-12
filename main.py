import sys


class Recipe:
    def __init__(self, identifier: str, d_0: str, d_1: str, d_2: str, d_3: str, p: str):
        self.id = identifier
        self.cost_0 = -int(d_0)
        self.cost_1 = -int(d_1)
        self.cost_2 = -int(d_2)
        self.cost_3 = -int(d_3)
        self.price = int(p)


class Witch:
    def __init__(self, i_0: int, i_1: int, i_2: int, i_3: int, s: int):
        self.inventory_0 = i_0
        self.inventory_1 = i_1
        self.inventory_2 = i_2
        self.inventory_3 = i_3
        self.score = s

    def can_make_recipe(self, recipe: Recipe):
        if self.inventory_0 >= recipe.cost_0 \
                and self.inventory_1 >= recipe.cost_1\
                and self.inventory_2 >= recipe.cost_2\
                and self.inventory_3 >= recipe.cost_3:
            return True
        else:
            return False

    def get_best_recipe_id(self, r_list: list):
        best_price = 0
        best_recipe_id = None
        for recipe in r_list:
            if self.can_make_recipe(recipe) and recipe.price > best_price:
                best_recipe_id = recipe.id
                best_price = recipe.price

        return best_recipe_id

    def print_inventory(self):
        print('i0: {}, i1: {}, i2:{}, i3:{}'.format(self.inventory_0, self.inventory_1, self.inventory_2,
                                                    self.inventory_3), file=sys.stderr, flush=True)


# game loop
while True:
    action_count = int(input())  # the number of spells and recipes in play
    recipes = []

    for i in range(action_count):
        # action_id: the unique ID of this spell or recipe
        # action_type: in the first league: BREW; later: CAST, OPPONENT_CAST, LEARN, BREW
        # delta_0: tier-0 ingredient change
        # delta_1: tier-1 ingredient change
        # delta_2: tier-2 ingredient change
        # delta_3: tier-3 ingredient change
        # price: the price in rupees if this is a potion
        # tome_index: in the first two leagues: always 0; later: the index in the tome if this is a tome spell, equal
        # to the read-ahead tax
        # tax_count: in the first two leagues: always 0; later: the amount of taxed tier-0 ingredients you gain from
        # learning this spell
        # castable: in the first league: always 0; later: 1 if this is a castable player spell
        # repeatable: for the first two leagues: always 0; later: 1 if this is a repeatable player spell

        action_id, action_type, delta_0, delta_1, delta_2, delta_3, price, tome_index, tax_count, castable, repeatable \
            = input().split()

        if action_type == 'BREW':
            r = Recipe(action_id, delta_0, delta_1, delta_2, delta_3, price)
            recipes.append(r)

    inv_0, inv_1, inv_2, inv_3, score = [int(j) for j in input().split()]
    player_witch = Witch(inv_0, inv_1, inv_2, inv_3, score)

    inv_0, inv_1, inv_2, inv_3, score = [int(j) for j in input().split()]
    opponent_witch = Witch(inv_0, inv_1, inv_2, inv_3, score)

    # basic strategy : always brew best potion
    if player_witch.get_best_recipe_id(recipes) is not None:
        print('BREW {}'.format(player_witch.get_best_recipe_id(recipes)))
    else:
        print('WAIT')

    # in the first league: BREW <id> | WAIT; later: BREW <id> | CAST <id> [<times>] | LEARN <id> | REST | WAIT
