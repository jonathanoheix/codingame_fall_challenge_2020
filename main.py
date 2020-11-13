import sys
import numpy as np


def print_debug(string: any):
    print(string, file=sys.stderr, flush=True)


class Recipe:
    def __init__(self, identifier: int, d_0: int, d_1: int, d_2: int, d_3: int, p: int):
        self.id = identifier
        self.costs = [-d_0, -d_1, -d_2, -d_3]
        self.price = p

    def get_reward_cost_ratio(self):
        return self.price - sum([self.costs[k] * (k + 1) for k in range(len(self.costs))])


class Cast:
    def __init__(self, identifier: int, d_0: int, d_1: int, d_2: int, d_3: int, repeatable_cast: int, t_i: int = None,
                 t_c: int = None):
        self.id = identifier
        self.deltas = [d_0, d_1, d_2, d_3]
        self.repeatable = repeatable_cast
        self.tome_index = t_i
        self.tax_count = t_c

    def cast_boost_value(self):
        gains = sum([self.deltas[k] * (k + 1) for k in range(len(self.deltas))])
        launch_difficulty_penalty = 1 - sum([self.deltas[k] * (k + 1) for k in range(len(self.deltas)) if self.deltas[k]
                                             < 0])
        repeatability_bonus = self.repeatable + 1
        # print_debug('gains {} launch_difficulty {} repeatability_bonus {}'.format(gains, launch_difficulty_penalty,
        # repeatability_bonus))
        return gains * repeatability_bonus / launch_difficulty_penalty


class Witch:

    def __init__(self):
        self.items = []
        self.score = None
        self.casts = []
        self.all_casts = []
        self.inventory_limit_size = 10

    def copy_witch(self):
        new_witch = Witch()
        new_witch.items = self.items.copy()
        new_witch.casts = self.casts.copy()
        new_witch.all_casts = self.all_casts.copy()
        new_witch.inventory_limit_size = self.inventory_limit_size
        return new_witch

    def add_cast(self, cast: Cast):
        self.casts.append(cast)

        if cast.id not in [x.id for x in self.all_casts]:
            self.all_casts.append(cast)

    def can_boost_item(self, item: int):
        boosting_casts = [cast for cast in self.casts if cast.deltas[item] > 0]
        # print_debug(str([cast.id for cast in boosting_casts]))
        # filter on feasible casts : enough room and enough items
        for cast in boosting_casts:
            if sum(np.add(self.items, cast.deltas)) <= self.inventory_limit_size and \
                    not len([x for x in np.add(self.items, cast.deltas) if x < 0]) > 0:
                return True
        return False

    def boost_item(self, item: int):
        best_boost = 0
        best_boost_cast = None
        times = 0

        for cast in self.casts:
            has_enough_items = not len([x for x in np.add(self.items, cast.deltas) if x < 0]) > 0
            has_enough_room = sum(np.add(self.items, cast.deltas)) <= self.inventory_limit_size
            if cast.deltas[item] > best_boost and has_enough_items and has_enough_room:
                best_boost_cast = cast
                best_boost = cast.deltas[item]

        has_enough_items = True
        has_enough_room = True
        if best_boost_cast.repeatable == 1:
            while has_enough_items and has_enough_room:
                self.use_cast(best_boost_cast)
                times += 1
                has_enough_items = not len([x for x in np.add(self.items, best_boost_cast.deltas) if x < 0]) > 0
                has_enough_room = sum(np.add(self.items, best_boost_cast.deltas)) <= self.inventory_limit_size
            return 'CAST {} {}'.format(best_boost_cast.id, times)
        else:
            return 'CAST {}'.format(best_boost_cast.id)

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

    def next_action_for_recipe(self, recipe: Recipe):

        temp_witch = self.copy_witch()

        # if we can't make the recipe
        if temp_witch.can_make_recipe(recipe):
            return 'BREW {}'.format(recipe.id)
        # if we can't make the recipe
        else:
            # temp_witch.print()

            for j in range(len(recipe.costs) - 1, -1, -1):
                # if we don't have enough of one item but we can boost it or one under it : launch corresponding cast

                superior_items_recipe = sum([recipe.costs[k] for k in range(j, len(recipe.costs))])
                superior_items_possessed = sum([temp_witch.items[k] for k in range(j, len(temp_witch.items))])
                print_debug('item {} cost of higher items {}'.format(j, superior_items_recipe -
                                                                     superior_items_possessed))

                if temp_witch.items[j] < recipe.costs[j] or superior_items_recipe > superior_items_possessed:
                    # print_debug('can boost {} {}'.format(temp_witch.can_boost_item(j), j))
                    if temp_witch.can_boost_item(j):
                        print_debug('boost item {}'.format(j))
                        return temp_witch.boost_item(j)

            # if we could not use any cast : rest to recover them
            print_debug('rest')
            temp_witch.casts = temp_witch.all_casts.copy()
            return 'REST'

    def get_recipe_proximity(self, recipe: Recipe):
        return sum([max(0, self.items[k] - recipe.costs[k]) * k for k in range(len(recipe.costs))])

    def print(self):
        print_debug('items : {}, casts : {}'.format(self.items, [x.id for x in self.casts]))

    def reset(self):
        self.items = []
        self.score = None
        self.casts = []


player_witch = Witch()
opponent_witch = Witch()
turn_number = 0

# game loop
while True:
    action_count = int(input())  # the number of spells and recipes in play
    recipes = []
    grimory_casts = []
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
            c = Cast(action_id, delta_0, delta_1, delta_2, delta_3, repeatable)
            player_witch.add_cast(c)

        elif action_type == 'OPPONENT_CAST' and castable == 1:
            c = Cast(action_id, delta_0, delta_1, delta_2, delta_3, repeatable)
            opponent_witch.add_cast(c)

        elif action_type == 'LEARN':
            c = Cast(action_id, delta_0, delta_1, delta_2, delta_3, repeatable, tome_index, tax_count)
            grimory_casts.append(c)

    inv_0, inv_1, inv_2, inv_3, score = [int(j) for j in input().split()]
    player_witch.items = [inv_0, inv_1, inv_2, inv_3]
    player_witch.score = score

    inv_0, inv_1, inv_2, inv_3, score = [int(j) for j in input().split()]
    opponent_witch.items = [inv_0, inv_1, inv_2, inv_3]
    opponent_witch.score = score

    # for each cast in the grimory : compute potential gain
    best_boost_value = 0
    best_cast = None
    for c in grimory_casts:
        boost_value = c.cast_boost_value()
        # print_debug('cast {} boost_value {}'.format(c.id, boost_value))
        if boost_value > best_boost_value:
            best_boost_value = boost_value
            best_cast = c
        elif boost_value == best_boost_value and boost_value > 0:
            if (best_cast.tome_index - best_cast.tax_count) > (c.tome_index - c.tax_count):
                best_boost_value = boost_value
                best_cast = c

    # if there is an interesting cast to buy
    if best_boost_value >= 2 and turn_number < 10:
        # we can buy it
        if player_witch.items[0] >= best_cast.tome_index:
            print('LEARN {}'.format(best_cast.id))
        # we can't buy it : reach that goal
        else:
            if player_witch.can_boost_item(0):
                print(player_witch.boost_item(0))
            else:
                print('REST')

    # no interesting casts to buy : make the recipes
    else:

        # get best recipe_proximity
        best_recipe_proximity = 99999
        best_recipe = None
        for r in recipes:
            if player_witch.get_recipe_proximity(r) < best_recipe_proximity:
                best_recipe_proximity = player_witch.get_recipe_proximity(r)
                best_recipe = r

        # print best recipe next action
        print_debug(best_recipe.id)
        print(player_witch.next_action_for_recipe(best_recipe))

    turn_number += 1

    # in the first league: BREW <id> | WAIT; later: BREW <id> | CAST <id> [<times>] | LEARN <id> | REST | WAIT
