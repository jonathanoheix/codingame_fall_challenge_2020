import sys
import numpy as np


def print_debug(string: any):
    print(string, file=sys.stderr, flush=True)


class Recipe:
    def __init__(self, identifier: int, d_0: int, d_1: int, d_2: int, d_3: int, p: int):
        self.id = identifier
        self.costs = [-d_0, -d_1, -d_2, -d_3]
        self.price = p


class Cast:
    def __init__(self, identifier: int, d_0: int, d_1: int, d_2: int, d_3: int):
        self.id = identifier
        self.deltas = [d_0, d_1, d_2, d_3]


class Witch:

    def __init__(self):
        self.items = []
        self.score = None
        self.casts = []
        self.all_casts = []

    def copy_witch(self):
        new_witch = Witch()
        new_witch.items = self.items.copy()
        new_witch.casts = self.casts.copy()
        new_witch.all_casts = self.all_casts.copy()
        return new_witch

    def add_cast(self, cast: Cast):
        self.casts.append(cast)

        if cast.id not in [x.id for x in self.all_casts]:
            self.all_casts.append(cast)

    def can_boost_item(self, item: int):
        boosting_casts = [cast for cast in self.casts if cast.deltas[item] > 0]
        # print_debug(str([cast.id for cast in boosting_casts]))
        # filter on feasible casts
        for cast in boosting_casts:
            if not len([x for x in np.add(self.items, cast.deltas) if x < 0]) > 0:
                return True
        return False

    def boost_item(self, item: int):
        for cast in self.casts:
            if cast.deltas[item] > 0 and not len([x for x in np.add(self.items, cast.deltas) if x < 0]) > 0:
                self.use_cast(cast)
                return 'CAST {}'.format(cast.id)

    def can_make_recipe(self, recipe: Recipe):
        if self.items[0] >= recipe.costs[0] and self.items[1] >= recipe.costs[1] and self.items[2] >= recipe.costs[2] \
                and self.items[3] >= recipe.costs[3]:
            return True
        else:
            return False

    def remove_cast(self, cast_id: int):
        for j in range(len(self.casts)):
            if self.casts[j].id == cast_id:
                del (self.casts[j])
                break

    def use_cast(self, cast: Cast):
        for k in range(len(cast.deltas)):
            self.items[k] += cast.deltas[k]

        self.remove_cast(cast.id)

    def next_actions_for_recipe(self, recipe: Recipe):

        temp_witch = self.copy_witch()

        actions = []

        # while we can't make the recipe
        while temp_witch.can_make_recipe(recipe) is False:

            # temp_witch.print()
            used_cast = False
            superior_needed = False

            for j in range(len(recipe.costs)-1, -1, -1):
                # if we don't have enough of one item but we can boost it or one under it : launch corresponding cast
                if not superior_needed:
                    if temp_witch.items[j] < recipe.costs[j]:
                        if temp_witch.can_boost_item(j):
                            # print_debug('boost item {}'.format(j))
                            actions.append(temp_witch.boost_item(j))
                            used_cast = True
                            break
                        else:
                            superior_needed = True
                elif superior_needed:
                    if temp_witch.items[j] < sum([recipe.costs[k] for k in range(j, len(recipe.costs))]):
                        # print_debug('can boost {} {}'.format(temp_witch.can_boost_item(j), j))
                        if temp_witch.can_boost_item(j):
                            # print_debug('boost item {}'.format(j))
                            actions.append(temp_witch.boost_item(j))
                            used_cast = True
                            break

            # if we could not use any cast : rest to recover them
            if not used_cast:
                # print_debug('rest')
                temp_witch.casts = temp_witch.all_casts.copy()
                actions.append('REST')

        return actions

    def print(self):
        print_debug('items : {}, casts : {}'.format(self.items, [x.id for x in self.casts]))

    def reset(self):
        self.items = []
        self.score = None
        self.casts = []


player_witch = Witch()
opponent_witch = Witch()

# game loop
while True:
    action_count = int(input())  # the number of spells and recipes in play
    recipes = []
    player_witch.reset()
    opponent_witch.reset()

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

        action_id = int(action_id)
        delta_0 = int(delta_0)
        delta_1 = int(delta_1)
        delta_2 = int(delta_2)
        delta_3 = int(delta_3)
        price = int(price)
        tome_index = int(tome_index)
        tax_count = int(tax_count)
        castable = int(castable)
        repeatable = int(repeatable)

        if action_type == 'BREW':
            r = Recipe(action_id, delta_0, delta_1, delta_2, delta_3, price)
            recipes.append(r)

        elif action_type == 'CAST' and castable == 1:
            c = Cast(action_id, delta_0, delta_1, delta_2, delta_3)
            player_witch.add_cast(c)

        elif action_type == 'OPPONENT_CAST' and castable == 1:
            c = Cast(action_id, delta_0, delta_1, delta_2, delta_3)
            opponent_witch.add_cast(c)

    inv_0, inv_1, inv_2, inv_3, score = [int(j) for j in input().split()]
    player_witch.items = [inv_0, inv_1, inv_2, inv_3]
    player_witch.score = score

    inv_0, inv_1, inv_2, inv_3, score = [int(j) for j in input().split()]
    opponent_witch.items = [inv_0, inv_1, inv_2, inv_3]
    opponent_witch.score = score

    # for each recipe : get the number of actions required
    recipes_actions = []
    for r in recipes:
        # print_debug('testing actions for recipe {}'.format(r.id))
        if len(player_witch.next_actions_for_recipe(r)) > 0:
            recipes_actions.append(player_witch.next_actions_for_recipe(r))
        else:
            recipes_actions.append(['BREW {}'.format(r.id)])
        print_debug(player_witch.next_actions_for_recipe(r))

    # get best reward_action_ratio
    reward_action_ratios = []
    for i in range(len(recipes_actions)):
        if len(recipes_actions[i]) != 0:
            reward_action_ratios.append(float(recipes[i].price)/len(recipes_actions[i]))
        else:
            reward_action_ratios.append(99999)

    print_debug(reward_action_ratios)

    print_debug(recipes[reward_action_ratios.index(max(reward_action_ratios))].id)
    print(recipes_actions[reward_action_ratios.index(max(reward_action_ratios))][0])

    # in the first league: BREW <id> | WAIT; later: BREW <id> | CAST <id> [<times>] | LEARN <id> | REST | WAIT
