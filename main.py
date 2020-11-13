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
    def __init__(self, identifier: int, d_0: int, d_1: int, d_2: int, d_3: int, repeatable_cast: int, t_i: int = None,
                 t_c: int = None):
        self.id = identifier
        self.deltas = [d_0, d_1, d_2, d_3]
        self.repeatable = repeatable_cast
        self.tome_index = t_i
        self.tax_count = t_c

    def get_gains(self):
        return sum([self.deltas[k] * (k + 1) for k in range(len(self.deltas))])


class Witch:

    def __init__(self):
        self.items = []
        self.score = None
        self.casts = []
        self.all_casts = []
        self.inventory_limit_size = 10
        self.nb_potions_made = 0

    def copy_witch(self):
        new_witch = Witch()
        new_witch.items = self.items.copy()
        new_witch.casts = self.casts.copy()
        new_witch.all_casts = self.all_casts.copy()
        new_witch.inventory_limit_size = self.inventory_limit_size
        return new_witch

    def add_cast(self, added_cast: Cast):
        self.casts.append(added_cast)

        if added_cast.id not in [x.id for x in self.all_casts]:
            self.all_casts.append(added_cast)

    def can_boost_item(self, item: int):
        boosting_casts = [x for x in self.casts if x.deltas[item] > 0]
        # print_debug(str([cast.id for cast in boosting_casts]))
        # filter on feasible casts : enough room and enough items
        for bc in boosting_casts:
            if self.can_launch_cast(bc):
                return True
        return False

    def boost_item(self, item: int):
        best_boost = 0
        best_boost_cast = None
        t = 0

        for bc in self.casts:
            if bc.get_gains() > best_boost and self.can_launch_cast(bc) and bc.deltas[item] > 0:
                best_boost_cast = bc
                best_boost = bc.get_gains()

        if best_boost_cast.repeatable == 1:
            while self.can_launch_cast(best_boost_cast):
                self.use_cast(best_boost_cast)
                t += 1
            return 'CAST {} {}'.format(best_boost_cast.id, t)
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

    def use_cast(self, cast_used: Cast):
        for k in range(len(cast_used.deltas)):
            self.items[k] += cast_used.deltas[k]

        self.remove_cast(cast_used.id)

    def next_action_for_recipe(self, recipe: Recipe):

        # if we can make the recipe
        if self.can_make_recipe(recipe):
            return 'BREW {}'.format(recipe.id)
        # if we can't make the recipe : test all possible casts
        else:

            min_distance = 99999
            bc = None
            for available_cast in self.casts:
                temp_witch = self.copy_witch()
                if temp_witch.can_launch_cast(available_cast):
                    temp_witch.use_cast(available_cast)
                    distance = temp_witch.get_recipe_distance(recipe)
                    if distance < min_distance:
                        bc = available_cast
                        min_distance = distance

            if bc is not None:
                return 'CAST {}'.format(bc.id)
            # if we could not use any cast : rest to recover them
            else:
                return 'REST'

    def get_recipe_distance(self, recipe: Recipe):
        # if nearly full, return impossible if not enough small items
        if self.inventory_limit_size - sum(self.items) < 2:
            for k in range(0, len(recipe.costs)):
                if sum(self.items[:k+1]) < sum(recipe.costs[:k+1]):
                    return 99999

        # else compute distance
        remaining_costs = [max(0, recipe.costs[k] - self.items[k]) for k in range(len(recipe.costs))]
        remaining_items = [max(0, self.items[k] - recipe.costs[k]) for k in range(len(recipe.costs))]

        distance = 0
        for k in range(1, len(remaining_costs)):
            item_level = k - 1
            # for each remaining cost we assign a distance
            while remaining_costs[k] > 0:
                if item_level >= 0:
                    if remaining_items[item_level] > 0:
                        distance += k - item_level
                        remaining_items[item_level] -= 1
                        remaining_costs[k] -= 1
                    else:
                        item_level -= 1
                else:
                    distance += k - item_level
                    remaining_costs[k] -= 1

        return distance

    def print(self):
        print_debug('items : {}, casts : {}'.format(self.items, [x.id for x in self.casts]))

    def reset(self):
        self.items = []
        self.score = None
        self.casts = []

    def can_launch_cast(self, cast_launched: Cast):
        has_enough_items = not len([x for x in np.add(self.items, cast_launched.deltas) if x < 0]) > 0
        has_enough_room = sum(np.add(self.items, cast_launched.deltas)) <= self.inventory_limit_size
        return has_enough_items and has_enough_room


player_witch = Witch()
opponent_witch = Witch()
turn_number = 0

# game loop
while True:
    action_count = int(input())  # the number of spells and recipes in play
    recipes = []
    grimory_casts = []
    action_made = False
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

    player_witch.print()

    # at the beginning of the game : get interesting and cheap casts
    if turn_number < 10:
        best_cast_value = 0
        best_cast = None
        for cast in grimory_casts:
            cast_value = cast.tax_count - cast.tome_index + cast.get_gains()
            print_debug('cast {} value : {}'.format(cast.id, cast_value))
            if cast_value > best_cast_value:
                best_cast_value = cast_value
                best_cast = cast

        # if there is an interesting cast
        if best_cast is not None:
            # if we can buy it
            if player_witch.items[0] >= best_cast.tome_index:
                print('LEARN {}'.format(best_cast.id))
            else:
                # else boost item 0
                if player_witch.can_boost_item(0):
                    player_witch.boost_item(0)
                else:
                    print('REST')
            action_made = True

    # no interesting casts to buy : make the recipes
    if not action_made:

        # if room left in inventory and not late game : maximize cast output
        if player_witch.inventory_limit_size - sum(player_witch.items) > 2 and player_witch.nb_potions_made < 5:
            best_cast_value = 0
            best_cast = None
            for cast in player_witch.casts:
                if cast.get_gains() > best_cast_value and player_witch.can_launch_cast(cast):
                    best_cast = cast
                    best_cast_value = cast.get_gains()

            if best_cast is not None:
                if best_cast.repeatable == 1:
                    times = 0
                    while player_witch.can_launch_cast(best_cast):
                        player_witch.use_cast(best_cast)
                        times += 1
                    print('CAST {} {}'.format(best_cast.id, times))
                else:
                    print('CAST {}'.format(best_cast.id))

            else:
                print('REST')

        # inventory almost full : get best recipe ratio score/distance
        else:
            best_ratio = 0
            best_recipe = None
            for r in recipes:

                # print_debug('recipe {} distance : {}'.format(r.id, player_witch.get_recipe_distance(r)))
                distance = (player_witch.get_recipe_distance(r) + 1) * 0.25
                if float(r.price / distance) > best_ratio:
                    best_ratio = float(r.price / distance)
                    best_recipe = r

            # print best recipe next action
            print_debug(best_recipe.id)
            print(player_witch.next_action_for_recipe(best_recipe))

    turn_number += 1

    # in the first league: BREW <id> | WAIT; later: BREW <id> | CAST <id> [<times>] | LEARN <id> | REST | WAIT
