################################# our code ###################################
import operator
from penguin_game import *
from nowork import turn
from trickyone import tricky
from circletwo import circle

################ Global variable ############
VULNERABLE_ICEBERG = 1
NUMBER_ADD = 1
NUMBER_STAY = 3
PRECENT_TO_HELP = 0.2
already_attacked = False
attacked = None
attackers = list()
real_shin_time = 0
DEBUG = False

################ Get closest ##############
def get_closest_natural_iceberg(game, my_iceberg, natural_icebergs):
    return min(natural_icebergs, key = lambda ice: ice.get_turns_till_arrival(my_iceberg))
    
def get_closest_my_iceberg(game, my_iceberg):
    return game.get_my_icebergs()[0]

def get_closest_enemy_iceberg(game, my_iceberg):
    return min(game.get_enemy_icebergs(), key = lambda ice: ice.get_turns_till_arrival(my_iceberg))

def get_closest_attack_iceberg(game, my_iceberg, ices_attacked):
    return min(ices_attacked, key = lambda ice: ice[0].get_turns_till_arrival(my_iceberg))

def get_closest_attack_iceberg_think_about_all(game, my_iceberg, ices_attacked):
    if len(ices_attacked) == 2:
        icebergs_attacked = [ice[0] for ice in ices_attacked]
        att_with_distance = []
        for attack in icebergs_attacked:
            this_att = []
            for ice in game.get_my_icebergs():
                if ice not in icebergs_attacked:
                    this_att += [(ice, attack.get_turns_till_arrival(ice))]
            att_with_distance += [this_att]
        if DEBUG:
            print icebergs_attacked, "icebergs_attacked"
            print att_with_distance, "att_with_distance"
        min_distance_from_two_attackers = [0,0]
        for d in range(len(att_with_distance[0])):#the distancese
            if att_with_distance[0][d][1] < att_with_distance[1][d][1]:
                min_distance_from_two_attackers[0] += 1
            else:
                min_distance_from_two_attackers[1] += 1
        
        if min_distance_from_two_attackers[0] == 0:
            closts = min(att_with_distance[0], key = lambda list: list[1])[0]
            if my_iceberg == closts:
                return ices_attacked[0]
                
        if min_distance_from_two_attackers[1] == 0:
            closts = min(att_with_distance[1], key = lambda list: list[1])[0]
            if my_iceberg == closts:
                return ices_attacked[1]
                
    return min(ices_attacked, key = lambda ice: ice[0].get_turns_till_arrival(my_iceberg))

def get_closest_vulnerable_iceberg(game, my_iceberg, vulnerable_icebergs):
    return min(vulnerable_icebergs, key = lambda ice: ice.get_turns_till_arrival(my_iceberg))
    
def get_my_partner_in_bridge(game, my_iceberg, bridge):
    ice = bridge.get_edges()
    des = [i for i in ice if i != my_iceberg]
    return des[0]
    
#get the closest natural iceberg there is no my penguins group on the way to it
def get_closest_natural_iceberg_not_sent_yet(game, my_iceberg, natural_icebergs):
    natural_icbergs_no_in_way = [d.destination for d in game.get_all_penguin_groups() if d.decoy == False]
    natural_icebergs_no_group_sent = [ice for ice in natural_icebergs if not ice in natural_icbergs_no_in_way]
    if len(natural_icebergs_no_group_sent) != 0:
        return min(natural_icebergs_no_group_sent, key = lambda ice: ice.get_turns_till_arrival(my_iceberg))
 
def get_closest_natural_iceberg_min_pinguin_not_sent_yet(game, my_iceberg, natural_icebergs):
    natural_icbergs_no_in_way = [d.destination for d in game.get_all_penguin_groups() if d.decoy == False]
    natural_icebergs_no_group_sent = [ice for ice in natural_icebergs if not ice in natural_icbergs_no_in_way]
    if len(natural_icebergs_no_group_sent) != 0:
        min_ice = min(natural_icebergs_no_group_sent, key = lambda ice: ice.penguin_amount)
        min_icebergs = [ice for ice in natural_icebergs_no_group_sent if ice.penguin_amount == min_ice.penguin_amount]
        return min(min_icebergs, key = lambda ice: ice.get_turns_till_arrival(my_iceberg))

def get_closest_natural_iceberg_min_pinguin(game, my_iceberg, natural_icebergs):
    if len(natural_icebergs) != 0:
        min_ice = min(natural_icebergs, key = lambda ice: natural_icebergs[ice])
        min_icebergs = [ice for ice in natural_icebergs if natural_icebergs[ice] == natural_icebergs[min_ice]]
        return min(min_icebergs, key = lambda ice: ice.get_turns_till_arrival(my_iceberg))


def get_closest_enemy_iceberg_min_pinguin(game):
    return min(game.get_enemy_icebergs(), key = lambda ice: ice.penguin_amount)

def enemy_one_shot(game, my_ice):
    closts_enemy = min(game.gget_enemy_icebergs(), key = lambda ice : ice.get_turns_till_arrival(my_ice))
    level_closts_enemy = closts_enemy.level
    distance = closts_enemy.get_tget_turns_till_arrival(my_ice) / 2
    enemy_burn = distance*level*3 + closts_enemy.penguin_amount
    if (my_ice.penguin_amount - my_ice.brigde_cost) > enemy_burn:
        return (closts_enemy, enemy_burn)
        
def get_closest_natural_iceberg_max_level(game, my_iceberg, natural_icebergs):
    ice_with_max_level = [ice for ice in natural_icebergs if ice.level > 1]
    if len(ice_with_max_level) != 0:
        min_dest_max_level = min(ice_with_max_level, key = lambda ice: ice.get_turns_till_arrival(my_iceberg))
        if min_dest_max_level.get_turns_till_arrival(my_iceberg) < 15:
            return min_dest_max_level   
            
def get_closest_natural_iceberg_max_level_not_sent_yet(game, my_iceberg, natural_icebergs):
    natural_icbergs_in_way = [d.destination for d in game.get_all_penguin_groups() if d.decoy == False]
    natural_icebergs_no_group_sent = [ice for ice in natural_icebergs if not ice in natural_icbergs_in_way]
    ice_with_max_level = [ice for ice in natural_icebergs_no_group_sent if ice.level > 1]
    if len(ice_with_max_level) != 0:
        min_dest_max_level = min(ice_with_max_level, key = lambda ice: ice.get_turns_till_arrival(my_iceberg))
        if min_dest_max_level.get_turns_till_arrival(my_iceberg) < 15:
            return min_dest_max_level
            
def change_from_max_natural_to_natural(game, my_iceberg, natural_icebergs):
    icebergs = game.get_my_icebergs()
    num_my_icebergs = len(icebergs)
    num_my_pg = len(game.get_my_penguin_groups())
    ene_pg = game.get_enemy_penguin_groups()
    if num_my_icebergs == 1:
        return True
    if num_my_icebergs == 1 and num_my_pg == 0:
        if [pg for pg in ene_pg if pg.destination != game.get_bonus_iceberg() and pg.destination.level == 1 and pg.decoy == False] != []:
            return True
    elif num_my_icebergs > 1:
        max_ice = max(icebergs, key = lambda ice : ice.penguin_amount*ice.level)
        ices = [ice for ice in icebergs if ice.penguin_amount*ice.level == max_ice.penguin_amount*max_ice.level]
        if len(ices) > 1:
            natural = get_closest_natural_iceberg_max_level(game, my_iceberg, natural_icebergs)
            max_ice = min(ices, key = lambda ice: ice.get_turns_till_arrival(natural))
        if my_iceberg != max_ice:
            return True
        if my_iceberg.level > 2 and num_my_pg == 0 and len(ene_pg) > 0:
            if num_my_icebergs == len(game.get_enemy_icebergs()):
                return True
    return False
  
def change_from_bonus_to_natural(game, my_iceberg, natural_icebergs):
    bonus = game.get_bonus_iceberg()
    if bonus and bonus.penguin_amount > 14:
        my_icebergs = game.get_my_icebergs()
        enemy_icebergs = game.get_enemy_icebergs()
        natural_penguin_amount = dict()
    
        for nat_ice in natural_icebergs:
            ice_owner_penguins = who_ice_going_to_be(game, nat_ice)
            if ice_owner_penguins:
                pg = ice_owner_penguins[1]
                natural_penguin_amount[nat_ice] = pg
                if ice_owner_penguins[0] == 'my':
                    my_icebergs += [nat_ice]
                elif ice_owner_penguins[0] == 'enemy':
                    enemy_icebergs += [nat_ice]
                    
        enemy_levels = [ice.level for ice in enemy_icebergs]
        my_levels = [ice.level for ice in my_icebergs]
        sum_enemy_levels = sum(enemy_levels)
        sum_my_levels = sum(my_levels)  
        if len(my_icebergs) == len(enemy_icebergs):
            if sum_enemy_levels == sum_my_levels:
                enemy_peng = []
                for ice in enemy_icebergs:
                    if ice not in natural_penguin_amount.keys():
                        enemy_peng += [ice.penguin_amount]
                    else:
                        enemy_peng += [natural_penguin_amount[ice]]
                        
                
                my_peng = []
                for ice in my_icebergs:
                    if ice not in natural_penguin_amount.keys():
                        my_peng += [ice.penguin_amount]
                    else:
                        my_peng += [natural_penguin_amount[ice]]
                sum_enemy_peng = sum(enemy_peng)
                sum_my_peng = sum(my_peng)  
                print sum_enemy_peng, "sum_enemy_peng"
                print sum_my_peng, "sum_my_peng"
                if sum_my_peng -2 <= sum_enemy_peng and game.turn < 50:
                    return True
                    
        elif len(my_icebergs) <= len(enemy_icebergs):
            if sum_enemy_levels >= sum_my_levels and game.turn < 50:
                return True


def who_ice_going_to_be(game, ice):
    penguin_amount = ice.penguin_amount

    my_to_ice = []
    enemy_to_ice = []
    bridges = [[ic for ic in br.get_edges() if ic != ice] for br in ice.bridges]
    for penguins_group in game.get_my_penguin_groups():
        if penguins_group.destination == ice and penguins_group.decoy == False:
            if penguins_group.source in bridges:
                my_to_ice += [(penguins_group.turns_till_arrival//2, penguins_group.penguin_amount)]
            else:
                my_to_ice += [(penguins_group.turns_till_arrival, penguins_group.penguin_amount)]
    
    for penguins_group in game.get_enemy_penguin_groups():
        if penguins_group.destination == ice and penguins_group.decoy == False:
            if penguins_group.source in bridges:
                enemy_to_ice += [(penguins_group.turns_till_arrival//2, -penguins_group.penguin_amount)]
            else:
                enemy_to_ice += [(penguins_group.turns_till_arrival, -penguins_group.penguin_amount)]

    all_to_ice = sorted(my_to_ice + enemy_to_ice, key = lambda pg: pg[0])
    
    my = True if ice.owner == game.get_myself() else False
    enemy =  True if ice.owner == game.get_enemy() else False
    natural =  True if ice.owner == game.get_neutral() else False

    if DEBUG:
        print 'all_to_ice', all_to_ice
    
    if all_to_ice == []:
        if my:
            return ('my', ice.penguin_amount, 0)
        elif enemy:
            return ('enemy', ice.penguin_amount, 0)
        elif natural:
            return ('natural', ice.penguin_amount, 0)

    last_turn = 0
  
    for i in all_to_ice:
        if natural:
            if i[1] < 0:
                penguins = -i[1]   
                if penguins <= penguin_amount: 
                    penguin_amount -= penguins
                else:
                    penguin_amount = penguins - penguin_amount
                    enemy =True
                    natural = False
            elif i[1] > 0:
                penguins = i[1]     
                if penguins <= penguin_amount:
                    penguin_amount -= penguins
                else:
                    penguin_amount = penguins - penguin_amount
                    my =True
                    natural = False
        elif my:
            penguin_amount += (i[0] - last_turn)*ice.level
        
            if i[1] < 0:    
                penguins = -i[1]      
                if penguins < penguin_amount:
                    penguin_amount -= penguins
                elif penguins == penguin_amount:
                    penguin_amount = 0
                    natural = True
                    my = False
                else:
                    penguin_amount = penguins - penguin_amount
                    enemy =True
                    my = False
            elif i[1] > 0:   
               penguins = i[1]   
               penguin_amount += penguins
               
        elif enemy:
            penguin_amount += (i[0] - last_turn)*ice.level 

            if i[1] > 0:    
                penguins = i[1]        
                if penguins < penguin_amount:
                    penguin_amount -= penguins
                elif penguins == penguin_amount:
                    penguin_amount = 0
                    natural = True
                    enemy = False
                else:
                    penguin_amount = penguins - penguin_amount 
                    my =True
                    enemy = False
            elif i[1] < 0:   
               penguins = -i[1]   
               penguin_amount += penguins
        last_turn = i[0]
    
    num_turns = last_turn 
    if my:
        return ('my', penguin_amount, last_turn)
    if enemy:
        return ('enemy', penguin_amount, num_turns)
    if natural:
        return ('natural', penguin_amount, num_turns)


############ destination penguin amount #############

def get_destination_pinguin_amount(game, type, my_iceberg, destination, icebergs_attacked, bridges, natural_icebergs):
    destination_penguin_amount = destination.penguin_amount
    if destination in natural_icebergs.keys():
        destination_penguin_amount = natural_icebergs[destination]
    my_penguin_amount = my_iceberg.penguin_amount  # type: int

    # The amount of penguins the target has
    # default: natural iceberg case
    if type == 'natural':
        return destination_penguin_amount 
    
    #Calculate the number of penguins to send according to the target
    # enemy iceberg case
    if type == 'winner':
        return my_iceberg.penguin_amount - 2
        
    if type == 'enemy':
        # The level, The penguin amount added per turn
        destination_level = destination.level 

        # The distance from my iceberg to the distance iceberg
        destination_distance = my_iceberg.get_turns_till_arrival(destination)
         
        # nump = number of penguin_amount, munt = number of turns
        owner_munp_munt = who_ice_going_to_be(game, destination)
        
        # How penguins need to sends to enemy iceberg
        #destination_penguin_amount = destination_distance*destination_level + destination_penguin_amount + 1
        
        destination_penguin_amount = owner_munp_munt[1] + (destination_distance- owner_munp_munt[2])*destination.level
        
    
        enemy_bonus = game.get_enemy_bonus_iceberg()
        if enemy_bonus and destination_distance > enemy_bonus.turns_left_to_bonus: 
            destination_penguin_amount += enemy_bonus.penguin_bonus
        if DEBUG:
            print destination_penguin_amount, "enemy need "
            print destination_distance, "enemy deistance"
            print owner_munp_munt, "owner_munp_munt"
        return destination_penguin_amount
            
    # enemy iceberg case
    if type == 'attack':
        # The amount of penguins attacking
        # iceberg[0]- type : iceberg
        # iceberg[1]- type : int, the number of penguins in the way to my iceberg
        
        if destination in natural_icebergs:
            destination_penguin_amount = [att[1]+1 for att in icebergs_attacked if att[0] == destination][0]
            print destination_penguin_amount, "natural attacked need "
            print my_iceberg.penguin_amount, "i have now"
            return destination_penguin_amount

        else:
            print icebergs_attacked, "icebergs_attacked"
            attackers_amount = [iceberg[1] for iceberg in icebergs_attacked if iceberg[0] == destination]
            print attackers_amount, "attackers_amount"
            # The amount of penguins already sent
            sender_amount = get_sum_my_penguin_groups_to_my_icberg(game, destination)
            print sender_amount, "sender_amount"
            # How penguins need to sends to enemy iceberg
            destination_penguin_amount = attackers_amount[0] - destination_penguin_amount - sender_amount 
            destination_penguin_amount = 0 if destination_penguin_amount < 0 else destination_penguin_amount
            print destination_penguin_amount, "attacked need "
            print my_iceberg.penguin_amount, "i have now"
            return destination_penguin_amount

        
    if type == 'defence':
        destination_penguin_amount = int(my_iceberg.penguin_amount* PRECENT_TO_HELP)
        return destination_penguin_amount

    if type == 'bonus':
        destination_penguin_amount = destination.penguin_amount + 2
        return destination_penguin_amount
        
    if type == 'bridge':
        # The level, The penguin amount added per turn
        destination_level = destination.level
        # The distance from my iceberg to the distance iceberg
        destination_distance = my_iceberg.get_turns_till_arrival(destination)
   
        bridge_speed_multiplier = my_iceberg.bridge_speed_multiplier
            
        destination_distance_faster = bridges[0].duration   
        destination_distance_slowly = destination_distance - destination_distance_faster * bridge_speed_multiplier   
        destination_distance_slowly = 0 if destination_distance_slowly < 0 else destination_distance_slowly
        distance = destination_distance_faster + destination_distance_slowly 
        
        # How penguins need to sends to enemy iceberg
        destination_penguin_amount = distance * destination_level + destination_penguin_amount + 1
        print destination_penguin_amount, "bridge enemy need " 
            
        destination_penguin_amount = my_penguin_amount-2 if destination_penguin_amount > my_penguin_amount-2 else int(destination_penguin_amount)
        return destination_penguin_amount


def just_one(game, my_iceberg, natural_icebergs):
    for pg in game.get_enemy_penguin_groups():
        if pg.destination in natural_icebergs and len([p for p in game.get_enemy_penguin_groups() if p.destination == pg.destination]) == 1 and pg.decoy == False:
            #checks if the iceberg closts to my icebergs and not too far- because they take it from me immidiatly
            if avg_from(pg.destination, game.get_my_icebergs()) <= avg_from(pg.destination, game.get_enemy_icebergs()):
                if pg.penguin_amount - pg.destination.penguin_amount == 1:
                    my_to_it = sum([penguins_group.penguin_amount for penguins_group in game.get_my_penguin_groups() if penguins_group.destination == pg.destination and penguins_group.decoy == False])
                   #num to send it is the diffrence between the turn that the enemy arrived to the destination, until my penguins 
                    num_to_send = my_iceberg.get_turns_till_arrival(pg.destination) - pg.turns_till_arrival
                    num_to_send *= pg.destination.level
                    if my_to_it < num_to_send:
                        if num_to_send <= 3 and num_to_send > 1:
                            if my_iceberg.penguin_amount > num_to_send + 1:
                                return (pg.destination, num_to_send)

def just_one_with_bridge(game, my_iceberg, natural_icebergs):
    for pg in game.get_enemy_penguin_groups():
        if pg.destination in natural_icebergs and pg.decoy == False:
            if pg.penguin_amount - pg.destination.penguin_amount == 1:
                num_to_send = my_iceberg.get_turns_till_arrival(pg.destination)/2 - pg.turns_till_arrival
                if num_to_send <= 3:
                    if my_iceberg.penguin_amount > num_to_send + 1 + my_iceberg.bridge_cost:
                        return pg.destination

def avg_from(des, all_ice):
    if all_ice == []:
        return 0
    num_ice = len(all_ice)
    if des in all_ice and num_ice == 1:
        return 0
    sum = 0
    for ice in all_ice:
        sum += ice.get_turns_till_arrival(des)
    return sum // num_ice
        
        
########### Prevention of attack ###########
        
#get the attacked iceberg  
def get_attack_iceberg(game):
    icebergs = dict()
    dist = dict()
    for ice in game.get_my_icebergs():
        enemy_penguin_groups_in_way = [penguins_group.penguin_amount for penguins_group in game.get_enemy_penguin_groups() if penguins_group.destination == ice and penguins_group.decoy == False]
        sum_enemy_penguin_groups_in_way = sum(enemy_penguin_groups_in_way)
        icebergs[ice] = sum_enemy_penguin_groups_in_way
        
        dest_and_amount = [g.turns_till_arrival for g in game.get_enemy_penguin_groups() if g.destination == ice and g.decoy == False]
        dest_and_amount_mine = [g.turns_till_arrival for g in game.get_my_penguin_groups() if g.destination == ice and g.decoy == False]
        clost = 0 if dest_and_amount == [] else min(dest_and_amount)
        clost_mine = 0 if dest_and_amount_mine == [] else min(dest_and_amount_mine)
        dist[ice] = (clost, clost_mine)
    
    icebergs_attacked = []
    for iceberg in icebergs:
        dest_from_me_enemy_mine = dist[iceberg]
        closts_enemy = dest_from_me_enemy_mine[0]
        closts_mine = dest_from_me_enemy_mine[1]
        all_p = iceberg.penguin_amount -1
        all_to_me = icebergs[iceberg]
        
        min_dest = [pg.destination for pg in game.get_enemy_penguin_groups() if pg.turns_till_arrival == closts_enemy and penguins_group.decoy == False]
        is_bridge = False
        for closts in min_dest:
            bridges = iceberg.bridges
            if bridges != []:
                min_with_bridges =[ice for ice in min_dest if ice in [b.get_edges() for b in bridges]]
                if min_with_bridges != []:
                    is_bridge = True
        
        if closts_mine <= closts_enemy:
            amount_closts_mine = [g.penguin_amount for g in game.get_my_penguin_groups() if g.destination == ice and g.turns_till_arrival == closts_mine and penguins_group.decoy == False]
            sum_amount_mine = sum(amount_closts_mine)
            all_p += sum_amount_mine
            
        if is_bridge:  
            all_p += (closts_enemy/iceberg.bridge_speed_multiplier) * iceberg.level 
        else:
            all_p += closts_enemy * iceberg.level 
       
        if all_to_me > all_p:
            icebergs_attacked += [(iceberg,icebergs[iceberg])]
    return icebergs_attacked

def get_attack_iceberg_with_natural(game, natural_icebergs):
    icebergs = dict()
    dist = dict()
    for ice in game.get_my_icebergs():
        enemy_penguin_groups_in_way = [penguins_group.penguin_amount for penguins_group in game.get_enemy_penguin_groups() if penguins_group.destination == ice and penguins_group.decoy == False]
        sum_enemy_penguin_groups_in_way = sum(enemy_penguin_groups_in_way)
        icebergs[ice] = sum_enemy_penguin_groups_in_way
        
        dest_and_amount = [g.turns_till_arrival for g in game.get_enemy_penguin_groups() if g.destination == ice and g.decoy == False]
        clost = 0 if dest_and_amount == [] else min(dest_and_amount)
        dist[ice] = clost
    
    icebergs_attacked = [(iceberg,icebergs[iceberg]) for iceberg in icebergs if icebergs[iceberg] > (iceberg.penguin_amount + dist[iceberg] * iceberg.level -1)]
    
    natural_sent = [pg.destination for pg in game.get_my_penguin_groups() if pg.destination in natural_icebergs and pg.decoy == False]
    for ice in natural_sent:
        penguin_amount = ice.penguin_amount
        
        my_to_ice = []
        enemy_to_ice = []
        for penguins_group in game.get_my_penguin_groups():
            if penguins_group.destination == ice and penguins_group.decoy == False:
                my_to_ice += [(penguins_group.turns_till_arrival, penguins_group.penguin_amount)]
        for penguins_group in game.get_enemy_penguin_groups():
            if penguins_group.destination == ice and penguins_group.decoy == False:
                enemy_to_ice += [(penguins_group.turns_till_arrival, -penguins_group.penguin_amount)]
        all_to_ice = sorted(my_to_ice + enemy_to_ice, key = lambda pg: pg[0])
        
        if all_to_ice == [] or all_to_ice[0][1] > 0:
            return icebergs_attacked
            
        for pg in all_to_ice:
            penguin_amount += pg[1]
        
        if penguin_amount < 0:
            icebergs_attacked += [(ice, -penguin_amount)]
            print "addd", ice, -penguin_amount
    return icebergs_attacked


def get_attack_bonus_iceberg(game):
    ice = game.get_bonus_iceberg()
    enemy_penguin_groups_in_way = [penguins_group.penguin_amount for penguins_group in game.get_enemy_penguin_groups() if penguins_group.destination == ice]
    sum_enemy_penguin_groups_in_way = sum(enemy_penguin_groups_in_way)
    dest_and_amount = [g.turns_till_arrival for g in game.get_enemy_penguin_groups() if g.destination == ice]
    clost = 0 if dest_and_amount == [] else min(dest_and_amount)
    
    if sum_enemy_penguin_groups_in_way > ice.penguin_amount + clost * ice.level -1:
        return True
    return False

    
def get_vulnerable_icebergs(game):
    icebergs = []
    for ice in game.get_my_icebergs():
        if ice.penguin_amount == VULNERABLE_ICEBERG and ice.level == 1:
            icebergs += [ice]
        
        if avg_from(ice, game.get_my_icebergs()) > avg_from(ice, game.get_enemy_icebergs()):
            result = who_ice_going_to_be(game, ice)
            print "result", result
            if result[0] == 'my':
                if result[1] < 10:
                    icebergs += [ice]
                #if ice.can_upgrade() and (result[1] - ice.upgrade_cost)  < get_closest_enemy_iceberg(game, ice).penguin_amount - 1:
                #    icebergs += [ice]

    return icebergs
        
def get_attack_iceberg_with_enemy_that_i_in_way(game):
    icebergs = dict()
    for ice in game.get_my_icebergs():
        enemy_penguin_groups_in_way = [penguins_group.penguin_amount for penguins_group in game.get_enemy_penguin_groups() if penguins_group.destination == ice]
        sum_enemy_penguin_groups_in_way = sum(enemy_penguin_groups_in_way) 
        icebergs[ice] = sum_enemy_penguin_groups_in_way
        
    for ice in [my_traget.destination for my_traget in game.get_my_penguin_groups() if my_traget.destination in game.get_enemy_icebergs()]:
        enemy_penguin_groups_in_way = [penguins_group.penguin_amount for penguins_group in game.get_enemy_penguin_groups() if penguins_group.destination == ice]
        sum_enemy_penguin_groups_in_way = sum(enemy_penguin_groups_in_way)
        icebergs[ice] = sum_enemy_penguin_groups_in_way
   
    icebergs_attacked = [(iceberg,icebergs[iceberg]) for iceberg in icebergs if icebergs[iceberg] > iceberg.penguin_amount]
    return icebergs_attacked

 #get sum of my penguins in the way to my iceberg
def get_sum_my_penguin_groups_to_my_icberg(game, my_iceberg):
    my_penguin_groups_in_way = [penguins_group.penguin_amount for penguins_group in game.get_my_penguin_groups() if penguins_group.destination == my_iceberg]
    sum_my_penguin_in_way = sum(my_penguin_groups_in_way)
    return sum_my_penguin_in_way
  
     
 #get sum of enemy penguins in the way to my iceberg
def get_sum_enemy_penguin_groups_to_my_icberg(game, my_iceberg):
    enemy_penguin_groups_in_way = [penguins_group.penguin_amount for penguins_group in game.get_enemy_penguin_groups() if penguins_group.destination == my_iceberg]
    sum_enemy_penguin_groups_in_way = sum(enemy_penguin_groups_in_way)
    return sum_enemy_penguin_groups_in_way
    

def danger_to_send_pinguins(game, my_iceberg, number_optional_to_send):
    on_the_way = get_sum_enemy_penguin_groups_to_my_icberg(game, my_iceberg)
    if (my_iceberg.penguin_amount - number_optional_to_send) < on_the_way:
        return True
    return False

def danger_to_upgrade(game, my_iceberg, upgrade_cost, new_level):
    enemy_penguin_groups_in_way = [penguins_group for penguins_group in game.get_enemy_penguin_groups() if penguins_group.destination == my_iceberg and penguins_group.decoy == False]
    num_turn_and_how_i_need = [(g.turns_till_arrival, g.penguin_amount) for g in enemy_penguin_groups_in_way]
    my_penguin_amount = my_iceberg.penguin_amount  ##21
    all_my_icebergs = game.get_my_icebergs()
    all_enemy_icebergs = game.get_enemy_icebergs()
    if len(all_my_icebergs) == 1 and len(all_enemy_icebergs) == 1:
        if my_penguin_amount - upgrade_cost + new_level*my_iceberg.get_turns_till_arrival(all_enemy_icebergs[0]) < all_enemy_icebergs[0].penguin_amount:
            return True
    
    if my_penguin_amount - upgrade_cost == 0:
        return True

    for i in num_turn_and_how_i_need:
        if my_penguin_amount - upgrade_cost + i[0]*new_level -1 <= i[1]:
            return True
        else:
            my_penguin_amount = my_penguin_amount - i[1] 
    return False
    
#def danger_to_upgrade(game, my_iceberg, upgrade_cost, new_level):
#    enemy_penguin_groups_in_way = [penguins_group for penguins_group in game.get_enemy_penguin_groups() if penguins_group.destination == my_iceberg]
#    num_turn_and_how_i_need = [(g.turns_till_arrival, g.penguin_amount) for g in enemy_penguin_groups_in_way]
#    num_turn_and_how_i_need.append((0,0))
#    num_turn_and_how_i_need = sorted(num_turn_and_how_i_need, key = lambda x: x[0])
#    print num_turn_and_how_i_need, "dest & amount"
#    my_penguin_amount = my_iceberg.penguin_amount
#    for i in range(1, len(num_turn_and_how_i_need)):
#        print "my_penguin_amount", my_penguin_amount
#        print "upgrade_cost", upgrade_cost
#        if (my_penguin_amount - upgrade_cost + (num_turn_and_how_i_need[i][0]- num_turn_and_how_i_need[i-1][0])*new_level) <= num_turn_and_how_i_need[i][1]:
#            return True
#        else:
#            my_penguin_amount = my_penguin_amount - num_turn_and_how_i_need[i][1] 
#    return False


# Return boolean if my_iceberg under attack
def is_under_attack(game, my_iceberg):
    attacked_iceberg = get_attack_iceberg(game)
    #check if my iceberg is under attack
    if any(map(lambda iceberg: iceberg[0] == my_iceberg, attacked_iceberg)):
        return True
    return False
 
# Get the distances from my_iceberg to the penguins group that my_iceberg is their destination  
def get_all_distances_enemy_penguins_groups_to_my_iceberg(game, my_iceberg):
    penguins_group = [penguins_group for penguins_group in game.get_enemy_penguin_groups() if penguins_group.destination == my_iceberg and penguins_group.decoy == False]
    return [group.turns_till_arrival for group in penguins_group]
    
# Return boolean if i have to escape my penguins from the icebergs    
def need_escape_and_not_die(game, my_under_attack_iceberg):
    if is_under_attack(game, my_under_attack_iceberg):
        the_target_distances_from_the_enemy_penguins = get_all_distances_enemy_penguins_groups_to_my_iceberg(game, my_under_attack_iceberg)
        how_many_come_to_help_me = get_sum_my_penguin_groups_to_my_icberg(game, my_under_attack_iceberg)
        if how_many_come_to_help_me == 0 and 1 in the_target_distances_from_the_enemy_penguins:
            print "escape!!! look: ", the_target_distances_from_the_enemy_penguins
            return True
    return False
        
    
 ###################### Bonus ##########################
def bonus_is_mine1(game):
    if game.get_enemy_bonus_iceberg() or game.get_neutral_bonus_iceberg():
        bonus_ice = game.get_bonus_iceberg()
        for penguins_group in game.get_my_penguin_groups():
            if penguins_group.destination == bonus_ice and penguins_group.decoy == False:
                return True
        return False
    return True

def bonus_is_mine(game):
    if game.get_enemy_bonus_iceberg() or game.get_neutral_bonus_iceberg():
        bonus_ice = game.get_bonus_iceberg()
        bonus_penguin_amount = -bonus_ice.penguin_amount
        
        my_to_bunos = []
        enemy_to_bunos = []
        for penguins_group in game.get_my_penguin_groups():
            if penguins_group.destination == bonus_ice and penguins_group.decoy == False:
                my_to_bunos += [(penguins_group.turns_till_arrival, penguins_group.penguin_amount)]
        for penguins_group in game.get_enemy_penguin_groups():
            if penguins_group.destination == bonus_ice and penguins_group.decoy == False:
                enemy_to_bunos += [(penguins_group.turns_till_arrival, -penguins_group.penguin_amount)]
        all_to_bonus = sorted(my_to_bunos + enemy_to_bunos, key = lambda pg: pg[0])
        
        for pg in all_to_bonus:
            bonus_penguin_amount += pg[1]
        
        if bonus_penguin_amount > 0:
            return True
        return False
    return True  
    
def bonus_is_enemy(game):
    if game.get_neutral_bonus_iceberg() or game.get_my_bonus_iceberg():
        bonus_ice = game.get_bonus_iceberg()
        for penguins_group in game.get_enemy_penguin_groups():
            if penguins_group.destination == bonus_ice and penguins_group.decoy == False:
                return True
        return False
    return True
    
    
####################### bridges ######################
def effictive_bridge(game, my_iceberg, destination, des_penguin_amount_need, des_penguin_amount_actually, dict_ice_briges, type):
    if type == "enemy":
        if danger_to_send_pinguins(game, my_iceberg, des_penguin_amount_actually) != True:
            if my_iceberg.can_create_bridge(destination) and not my_iceberg.bridges:
                enemy_levels = [ice.level for ice in game.get_enemy_icebergs()]
                my_levels = [ice.level for ice in game.get_my_icebergs()]
                sum_enemy_levels = sum(enemy_levels)
                sum_my_levels = sum(my_levels)
                print sum_enemy_levels, "sum_enemy_levels", sum_my_levels, "sum_my_levels"
                if sum_enemy_levels > sum_my_levels:
                    return False
                my_penguin_amount = sum([p.penguin_amount for p in game.get_my_icebergs()])
                enemy_penguin_amount = sum([p.penguin_amount for p in game.get_enemy_icebergs()])
             
                if sum_enemy_levels >=18 and sum_enemy_levels >= 18:
                    if enemy_penguin_amount > my_penguin_amount:
                        return False
                if max(my_levels) < 3 and my_penguin_amount < enemy_penguin_amount:
                    return False
                #if sum_enemy_levels == sum_my_levels and len(game.get_my_icebergs()) == len(game.get_enemy_icebergs()):
                #    return False
                if des_penguin_amount_need > des_penguin_amount_actually*2.6 and len(game.get_my_icebergs()) < 6:
                    return False
                if game.turn < 50 and len(game.get_my_icebergs()) <= len(game.get_enemy_icebergs()):
                    return False
                if des_penguin_amount_actually > 9:
                    print "des_penguin_amount_actually", des_penguin_amount_actually
                    if dict_ice_briges[destination] < 4:
                        print "num bridges", dict_ice_briges[destination]
                        return True
        return False
    elif type == "natural":
        if len(game.get_my_icebergs()) <= 4 and des_penguin_amount_need > 15:
            print my_iceberg.get_turns_till_arrival(destination) , "distance"
            bridges = my_iceberg.bridges
            if bridges != [] and destination in [br.get_edges() for br in bridges]:
                return False
            if [pg.penguin_amount for pg in game.get_enemy_penguin_groups() if pg.destination == my_iceberg and pg.decoy == False] != []:
                return False
            if len(game.get_my_icebergs()) == 1 and 1 == len(game.get_enemy_icebergs()):
                if game.get_enemy_icebergs()[0].level > game.get_my_icebergs()[0].level:
                    return False
            print "my penguin_amount", my_iceberg.penguin_amount
            print "des_penguin_amount_need", des_penguin_amount_need
            if my_iceberg.penguin_amount > des_penguin_amount_need:
                if my_iceberg.can_upgrade() == False: 
                    return True
                elif my_iceberg.level >= 2:
                    return True
                
def effective_use_natural_bridge(game, bridges_to_natural, natural_icebergs):
    for br in bridges_to_natural:
        natural_ice = [ice for ice in br.get_edges() if ice in natural_icebergs][0]
        all_pg = [pg.penguin_amount for pg in game.get_my_penguin_groups() if pg.destination == natural_ice and pg.decoy == False]
        if all_pg != []:
            if sum(all_pg) < natural_ice.penguin_amount:
                return True
            else:
                return False
        return True
    
def effictive_bridge11(game, my_iceberg, destination, des_penguin_amount, des_penguin_amount_actually, dict_ice_briges):
    if danger_to_send_pinguins(game, my_iceberg, des_penguin_amount_actually) != True:
        if my_iceberg.can_create_bridge(destination) and not my_iceberg.bridges:
            if des_penguin_amount_actually > 9:
                if dict_ice_briges[destination] < 4:
                    return True
    return False
    
#when we build bridge to natural icebergs, we checks that we have enough penguins.
#so, we need to send after building just one time!
#we have a dict that say if we need to send 


def intialize_bridges_from_my_icebergs_to_natural_destination(game, bridges_to_natural):
    d = dict()
    for ice in game.get_my_icebergs():
        if ice in bridges_to_natural.keys():
            d[ice] = bridges_to_natural[ice]
        else:
            d[ice] = False
    return d
    
def get_relenant_bridges_for_this_icebergs(game, my_iceberg, bridges, not_relevant_bridges_to_natural):
    my_bridges = [br for br in bridges if my_iceberg in br.get_edges() and br.owner == game.get_myself()]
    relevant_bridges = []
    for br in my_bridges:
        second_side = [ice for ice in br.get_edges() if ice not in game.get_my_icebergs()]
        if second_side != []:
            second_side = second_side[0]
            if second_side not in not_relevant_bridges_to_natural.values():
                relevant_bridges += [br]

            if second_side in not_relevant_bridges_to_natural.values():
                if my_iceberg in not_relevant_bridges_to_natural.keys():
                    if second_side != not_relevant_bridges_to_natural[my_iceberg]:
                        relevant_bridges += [br]
    return relevant_bridges
        
def intialize_number_bridges_from_my_icebergs_to_this_destination(game):
    bridges = dict()
    for ice in game.get_enemy_icebergs():
        all_ice_bridges = ice.bridges
        my_icebergs_to_destination = []
        for bridge in all_ice_bridges:
            source = [i for i in bridge.get_edges() if i != ice][0]
            if source in game.get_my_icebergs():
                my_icebergs_to_destination += [source]
        bridges[ice] = len(my_icebergs_to_destination)
    return bridges
        
def plus_1_bridge(dict_icebergs_num_briges, destination):
    dict_icebergs_num_briges[destination] += 1
    
###############  winner ###########################
def is_win(game, my_iceberg):
    all_my_icebergs = game.get_my_icebergs()
    all_enemy_icebergs = game.get_enemy_icebergs()
    if len(all_my_icebergs) == 1 and len(all_enemy_icebergs) == 1:
        penguins = [penguins_group.penguin_amount for penguins_group in game.get_enemy_penguin_groups() if penguins_group.decoy == False]
        enemy_iceberg = all_enemy_icebergs[0]
        distance = my_iceberg.get_turns_till_arrival(enemy_iceberg)
        penguin_amount_need = enemy_iceberg.penguin_amount + distance*enemy_iceberg.level
        penguin_amount_need += sum(penguins)
        if my_iceberg.penguin_amount > penguin_amount_need:
            return True
        
        if len(all_my_icebergs) == 1 and len(all_enemy_icebergs) == 1:
            if distance == 7:
                return True
    return False
    
################## hero iceberg #############
def i_am_hero(game, my_iceberg):
    if not game.get_bonus_iceberg():
        return False
    dice_ice_sum_distances = dict() 
    for my_ice in game.get_my_icebergs():
        distance_bonus = my_ice.get_turns_till_arrival(game.get_bonus_iceberg())
        dice_ice_sum_distances[my_ice] = distance_bonus
    max_ice = max(dice_ice_sum_distances.iteritems(), key = operator.itemgetter(1))[0]
    
    if max_ice == my_iceberg and my_iceberg.level < 4:
        if len(game.get_my_icebergs()) > len(game.get_enemy_icebergs()):
            return True
    
    my_icebergs = len(game.get_enemy_icebergs())
    if my_icebergs == len(game.get_my_icebergs()) and my_icebergs > 3:
        enemy_levels = [ice.level for ice in game.get_enemy_icebergs()]
        print enemy_levels, "enemy_levels"
        my_levels = [ice.level for ice in game.get_my_icebergs()]
        all_enemy_levels = sum(enemy_levels)
        all_my_levels = sum(my_levels)
        if all_enemy_levels >= all_my_levels:
            return True
    return False
    
def i_am_week(game, my_iceberg):
    if my_iceberg.level == 1:
        return True
    if my_iceberg.level < 4 and game.turn > 110:
        return True
        
    
################### intialize icebergs #####################
def intialize_natural_icebergs(game, priority_icebergs):
    natural_ices = dict()
    for ice in game.get_neutral_icebergs():
        if avg_from(ice, game.get_enemy_icebergs()) < avg_from(ice, game.get_my_icebergs()):
            continue
        result = who_ice_going_to_be(game, ice)
        if result[0] != 'my':
            natural_ices[ice] = result[1]
 
    intersection = set(priority_icebergs.keys()) & set(natural_ices.keys())
    
    if len(intersection) != 0:
        natural_ices = dict()
        for ice in intersection:
            natural_ices[ice] = priority_icebergs[ice]
    return natural_ices

def upgrade_instead_natural(game, natural_icebergs):
    my_icebergs = game.get_my_icebergs()
    enemy_icebergs = game.get_enemy_icebergs()
    
    if len(natural_icebergs) == 1 and len(my_icebergs) == len(enemy_icebergs):
        if [1 for pg in game.get_enemy_penguin_groups() if pg.destination in game.get_neutral_icebergs()] == []:
            enemy_levels = [ice.level for ice in enemy_icebergs]
            my_levels = [ice.level for ice in my_icebergs]
            sum_enemy_levels = sum(enemy_levels)
            sum_my_levels = sum(my_levels)  
            if sum_enemy_levels > sum_my_levels:
                return True
    return False
    

def is_effective_send(game, my_iceberg, destination, destination_penguin_amount, natural_icebergs):
    if len(natural_icebergs) > 1:
        return True
    sorted_icebergs = sorted(game.get_my_icebergs(), key = lambda i: destination.get_turns_till_arrival(i))
    for ice in sorted_icebergs:
        if ice.penguin_amount + ice.level*2 >= destination_penguin_amount:
            if ice == my_iceberg:
                return True
            else:
                return False

def shin_time(game):
    for my_iceberg in game.get_my_icebergs():
        min_ices = sorted(game.get_enemy_icebergs(), key = lambda ice : ice.level*ice.penguin_amount*ice.get_turns_till_arrival(my_iceberg))
        if len(min_ices) == 1:
            min_ice = min_ices[0]
            shin_time = (game.max_turns - min_ice.penguin_amount//2)
            print shin_time
            if game.turn == shin_time:
                if my_iceberg.can_create_bridge(min_ice):
                    my_iceberg.create_bridge(min_ice)
                    return True
            elif game.turn == shin_time + 1:
                my_iceberg.send_penguins(min_ice, min_ice.penguin_amount + 1)
                
        elif len(min_ices) > 1:
            min_ice = min_ices[0]
            shin_time_1 = (game.max_turns - min_ice.penguin_amount//2)
            print shin_time_1
            min_ice_2 = min_ices[1]
            shin_time_2 = (game.max_turns - min_ice_2.penguin_amount//2)
            print shin_time_2
           
            if shin_time_1 == shin_time_2:
                shin_time_1 -= 1
                
            if game.turn == shin_time_1:
                if my_iceberg.can_create_bridge(min_ice):
                    my_iceberg.create_bridge(min_ice)
                    return True
            elif game.turn == shin_time_1 + 1:
                my_iceberg.send_penguins(min_ice, min_ice.penguin_amount + 1)
                
            if game.turn == shin_time_2:
                if my_iceberg.can_create_bridge(min_ice_2):
                    my_iceberg.create_bridge(min_ice_2)
                    return True
            elif game.turn == shin_time_2 + 1:
                my_iceberg.send_penguins(min_ice_2, min_ice_2.penguin_amount + 1)
    return False
ice1_end = None
ice2_end = None
enemy1_end =None
enemy2_end = None
distance1_end = None
distance2_end = None
def finish_time(game, my_iceberg):
    my_icebergs = [ice for ice in game.get_my_icebergs() if sum([pg.penguin_amount for pg in game.get_enemy_penguin_groups() if pg.destination == ice]) < ice.penguin_amount/10]
    my_icebergs = sorted(my_icebergs, key = lambda ice: ice.penguin_amount)
    if len(my_icebergs) < 2:
        return
    if len(game.get_enemy_icebergs()) == 1:
        return
    global ice1_end 
    global ice2_end 
    global enemy1_end 
    global enemy2_end 
    global distance1_end
    global distance2_end

    ###### ICE1 ########
    #if not ice1_end:
    ice1 = my_icebergs[-1]
    print ice1, ice1.penguin_amount
    for_enemy1 = sorted(game.get_enemy_icebergs(), key = lambda ice : ice.get_turns_till_arrival(ice1))
    enemy1 = for_enemy1[0]
    distance1 = ice1.get_turns_till_arrival(enemy1) / 2 + 1
    print enemy1, enemy1.penguin_amount, distance1

    ###### ICE2 ########
    #if not ice2_end:
    ice2 = my_icebergs[-2]
    print ice2, ice2.penguin_amount
    for_enemy2 = sorted(game.get_enemy_icebergs(), key = lambda ice : ice.get_turns_till_arrival(ice2))
    enemy2 = for_enemy2[0]
    distance2 = ice2.get_turns_till_arrival(enemy2) / 2 + 1
    print enemy2, enemy2.penguin_amount, distance2
        
    if enemy1 == enemy2:
        if distance1 < distance2:
            enemy2 = for_enemy2[1]
            distance2 = ice1.get_turns_till_arrival(enemy2) / 2 + 1
        else:
            enemy1 = for_enemy1[1]
            distance1 = ice1.get_turns_till_arrival(enemy1) / 2 + 1
    
    print enemy1, enemy1.penguin_amount, distance1
    print enemy2, enemy2.penguin_amount, distance2
    
    ####### ICE1 ########
    if game.turn == game.max_turns-distance1:
        ice1_end = ice1
        enemy1_end = enemy1
        distance1_end = distance1
        ice1_end.create_bridge(enemy1_end)
        return True
    
    elif distance1_end and game.turn == game.max_turns-distance1_end+1:
        print "need to send"
        amount1 = enemy1_end.penguin_amount + distance1_end*3*enemy1_end.level
        for amount in [3,2,1]:
            print ice1_end, enemy1_end, distance1_end
            amo = amount1*amount
            print amount1
            if ice1_end.penguin_amount > amount1*3:
                ice1_end.send_penguins(enemy1_end, int(amount1*3))
                return True
            if ice1_end.penguin_amount > amount1*1.5:
                ice1_end.send_penguins(enemy1_end, int(amount1*1.5))
                return True
    
    elif distance1_end and game.turn == game.max_turns-distance1_end+ice1_end.max_bridge_duration-1:
        ice1_end.create_bridge(enemy1_end)
        return True
    
    ####### ICE2 #######   
    if game.turn == game.max_turns-distance2:
        ice2_end = ice2
        enemy2_end = enemy2
        distance2_end = distance2
        ice2_end.create_bridge(enemy2_end)
        return True
    
    elif distance2_end and game.turn == game.max_turns-distance2_end+1:
        print "need to send"
        amount2 = enemy2_end.penguin_amount + distance2_end*3*enemy2_end.level
        for amount in [3,2,1]:
            print ice2_end, enemy2_end, distance2_end
            amo = amount2*amount
            print amount2
            if ice2_end.penguin_amount > amount2*3:
                ice2_end.send_penguins(enemy2_end, int(amount2*3))
                return True
            if ice2_end.penguin_amount > amount2*1.5:
                ice2_end.send_penguins(enemy2_end, int(amount2*1.5))
                return True
        
    elif distance2_end and game.turn == game.max_turns-distance2_end+ice2_end.max_bridge_duration-1:
        ice2_end.create_bridge(enemy2_end)
        return True
    

    
bridges_to_natural = dict()
not_relevant_bridges_to_natural = dict()
priority_icebergs = dict()

def do_turn(game):
    enemy_player = game.get_enemy().__str__()
    if DEBUG:
        print enemy_player
        
    if "Group30" in enemy_player and len(game.get_enemy_icebergs()) == 1:
        if game.get_enemy_icebergs()[0].level > game.get_my_icebergs()[0].level:
            game.get_my_icebergs()[0].upgrade()
        return
    error_player = ["Group30", "group45"]
 
    if len(game.get_all_icebergs()) == 5:
        tricky(game)
        return
    
    if len(game.get_all_icebergs()) == 12:
        circle(game)
        return
   
    if len(enemy_player.split("bot name:",1)[1]) == 9 and all(e not in enemy_player for e in error_player):
        if avg_from(game.get_bonus_iceberg(), game.get_all_icebergs()) == 11:
            turn(game)
            return
    

    avoid_duplicate_sent_mine = True
    avoid_duplicate_bonus = True 
    avoid_duplicate_sent_natural = True
    avoid_duplicate_defence = True  
    
    dict_icebergs_num_briges = intialize_number_bridges_from_my_icebergs_to_this_destination(game)
    natural_icebergs = intialize_natural_icebergs(game, priority_icebergs)
    if DEBUG:
        print natural_icebergs, "natural_icebergs"
    send = []
    upgrades = []
    
    for my_iceberg in game.get_my_icebergs():
        if game.turn > 280:
            if finish_time(game, my_iceberg):
                return
        # The amount of penguins in my iceberg.
        if DEBUG:
            print my_iceberg, "my_iceberg"
        my_penguin_amount = my_iceberg.penguin_amount  # type: int
        
        is_enemy = False
        is_attack = False
        is_natural = False
        is_defence = False
        is_bonus = False
        is_bridge = False
        is_max_level = False
        is_make_me_winner = False
        is_hero = False
        
        icebergs_attacked = get_attack_iceberg(game)
        vulnerable_icebergs = get_vulnerable_icebergs(game)
        bridges = get_relenant_bridges_for_this_icebergs(game, my_iceberg, my_iceberg.bridges, not_relevant_bridges_to_natural) 
        
        # If my iceberg attacked
        if len(game.get_enemy_penguin_groups()) != 0 and len(icebergs_attacked) != 0:
            destination = get_closest_attack_iceberg(game, my_iceberg, icebergs_attacked)[0]
            is_attack = True
            if DEBUG:
                print destination, "attack "
            destination_penguin_amount = get_destination_pinguin_amount(game, 'attack', my_iceberg, destination, icebergs_attacked, bridges, natural_icebergs)
        
        elif is_win(game, my_iceberg):
            destination = game.get_enemy_icebergs()[0]
            is_make_me_winner = True
            if DEBUG:
                print destination, "got winner "
            destination_penguin_amount = get_destination_pinguin_amount(game, 'winner', my_iceberg, destination, icebergs_attacked, bridges, natural_icebergs)
            
        elif my_iceberg in bridges_to_natural.keys() and bridges_to_natural[my_iceberg]:
            destination = get_my_partner_in_bridge(game, my_iceberg, my_iceberg.bridges[0])
            is_bridge = True
            if DEBUG:
                print destination, "bridge "
            bridges_to_natural[my_iceberg] = False
            not_relevant_bridges_to_natural[my_iceberg] = destination
            destination_penguin_amount = get_destination_pinguin_amount(game, 'natural', my_iceberg, destination, icebergs_attacked, bridges, natural_icebergs)
        
        elif len(bridges) > 0:
            destination = get_my_partner_in_bridge(game, my_iceberg, bridges[0])
            is_bridge = True
            if DEBUG:
                print destination, "bridge "
            destination_penguin_amount = get_destination_pinguin_amount(game, 'bridge', my_iceberg, destination, icebergs_attacked, bridges, natural_icebergs)
            
        elif len(vulnerable_icebergs) != 0 and my_iceberg not in vulnerable_icebergs:
            destination = get_closest_vulnerable_iceberg(game, my_iceberg, vulnerable_icebergs)
            is_defence = True
            if DEBUG:
                print destination, "defence "
            destination_penguin_amount = get_destination_pinguin_amount(game, 'defence', my_iceberg, destination, icebergs_attacked, bridges, natural_icebergs)

        elif get_closest_natural_iceberg_max_level(game, my_iceberg, natural_icebergs):
            destination = get_closest_natural_iceberg_max_level(game, my_iceberg, natural_icebergs)
            is_natural = True
            is_max_level = True
            if DEBUG:
                print destination, " max level natural"
            destination_penguin_amount = get_destination_pinguin_amount(game, 'natural', my_iceberg, destination, icebergs_attacked, bridges, natural_icebergs)
        
        elif get_closest_natural_iceberg_min_pinguin(game, my_iceberg, natural_icebergs): 
                destination = get_closest_natural_iceberg_min_pinguin(game, my_iceberg, natural_icebergs) # type: Iceberg
                is_natural = True
                if DEBUG:
                    print destination, " natural"
                destination_penguin_amount = get_destination_pinguin_amount(game, 'natural', my_iceberg, destination, icebergs_attacked, bridges, natural_icebergs)

        elif bonus_is_mine(game) == False and not len(game.get_my_icebergs())*2 < len(game.get_enemy_icebergs()):
            destination = game.get_bonus_iceberg()
            is_bonus = True
            if DEBUG:
                print destination, "bonus "
            destination_penguin_amount = get_destination_pinguin_amount(game, 'bonus', my_iceberg, destination, icebergs_attacked, bridges, natural_icebergs)
            
        elif get_closest_enemy_iceberg(game, my_iceberg):
            destination = get_closest_enemy_iceberg(game, my_iceberg)
            is_enemy = True
            if DEBUG:
                print destination, " enemy"
            destination_penguin_amount = get_destination_pinguin_amount(game, 'enemy', my_iceberg, destination, icebergs_attacked, bridges, natural_icebergs)
     
        if is_max_level and change_from_max_natural_to_natural(game, my_iceberg, natural_icebergs):
            is_max_level = False
            destination = get_closest_natural_iceberg_min_pinguin(game, my_iceberg, natural_icebergs) # type: Iceberg
            if destination:
                is_natural = True
                if DEBUG:
                    print destination, " natural"
                destination_penguin_amount = get_destination_pinguin_amount(game, 'natural', my_iceberg, destination, icebergs_attacked, bridges, natural_icebergs) 
        
        if (my_penguin_amount < destination_penguin_amount and is_bonus) or (is_attack and destination_penguin_amount == 0):
            if get_closest_natural_iceberg_min_pinguin(game, my_iceberg, natural_icebergs):
                destination = get_closest_natural_iceberg_min_pinguin(game, my_iceberg, natural_icebergs)
                destination_penguin_amount = destination.penguin_amount 
                is_natural = True
                is_attack = False
                is_bonus = False
                if DEBUG:
                    print destination, " natural"
            else:
                is_attack = False
                is_bonus = False
        
        if is_natural and upgrade_instead_natural(game, natural_icebergs):
            is_natural = False
            
        if is_attack and destination_penguin_amount == 0:
           is_attack = False
           
        if is_bonus and my_iceberg.can_upgrade():
            is_bonus = False
        
        if is_bonus and game.get_neutral_bonus_iceberg() and [pg for pg in game.get_enemy_penguin_groups() if pg. destination == game.get_bonus_iceberg()] == []:
            if game.turn<50:
                is_bonus = False
                
        if my_penguin_amount <= destination_penguin_amount and is_enemy and len(game.get_my_icebergs()) <= 3:
            nat = get_closest_natural_iceberg_min_pinguin(game, my_iceberg, natural_icebergs)
            if nat:
                destination = nat
                destination_penguin_amount = destination.penguin_amount 
                is_natural = True
                is_enemy = False
                if DEBUG:
                    print destination, " natural"
        
        if is_enemy and len(game.get_my_icebergs()) == len(game.get_enemy_icebergs()) and [pg for pg in game.get_enemy_penguin_groups() if pg.destination in natural_icebergs and pg.decoy == False] != []:
            nat = get_closest_natural_iceberg_min_pinguin(game, my_iceberg, natural_icebergs)
            if nat:
                destination = nat
                destination_penguin_amount = destination.penguin_amount 
                is_natural = True
                is_enemy = False
                if DEBUG:
                    print destination, " natural"
                
        if is_enemy and (i_am_hero(game, my_iceberg) or i_am_week(game, my_iceberg)):
            is_hero = True
            is_enemy = False

        number_penguin_to_send = my_penguin_amount -3 if destination_penguin_amount > my_penguin_amount-2 else destination_penguin_amount + 1
        if is_enemy and effictive_bridge(game, my_iceberg, destination, destination_penguin_amount, number_penguin_to_send, dict_icebergs_num_briges, "enemy"):
            is_enemy = False
            my_iceberg.create_bridge(destination)
            plus_1_bridge(dict_icebergs_num_briges, destination)
            
        elif is_natural and effictive_bridge(game, my_iceberg, destination, destination_penguin_amount, number_penguin_to_send, dict_icebergs_num_briges, "natural"):
            if my_penguin_amount > destination_penguin_amount + 1 + my_iceberg.bridge_cost:
                is_natural = False
                bridges_to_natural[my_iceberg] = True
                my_iceberg.create_bridge(destination)

        elif is_make_me_winner:
            is_make_me_winner = False
            if destination_penguin_amount > destination.penguin_amount:
                send += [[my_iceberg, destination, destination_penguin_amount+1, destination_penguin_amount, "winner"]]
            
        elif (len(game.get_enemy_penguin_groups()) == 0 or is_natural) and my_iceberg.can_upgrade() == True and not is_bridge:
            if danger_to_upgrade(game, my_iceberg, my_iceberg.upgrade_cost, my_iceberg.level+1) != True:
                if DEBUG:
                    print my_iceberg, "upgrade from ", my_iceberg.level, " to", (my_iceberg.level + 1)
                my_iceberg.upgrade() 
                upgrades += [my_iceberg]
        
        elif my_penguin_amount > destination_penguin_amount and  is_bonus and avoid_duplicate_bonus:
            if danger_to_send_pinguins(game, my_iceberg, destination_penguin_amount+1) != True:
                if DEBUG:
                    print my_iceberg, "sends", (destination_penguin_amount +1), "penguins to", destination
                send += [[my_iceberg, destination, destination_penguin_amount+1, destination_penguin_amount, "bonus"]]
                #avoid_duplicate_bonus = False
                
        elif is_bridge:
            if danger_to_send_pinguins(game, my_iceberg, destination_penguin_amount+1) != True:
                if DEBUG:
                    print my_iceberg, "sends", (destination_penguin_amount+1), "penguins to", destination
                send += [[my_iceberg, destination, destination_penguin_amount+1, destination_penguin_amount, "bridge"]]

        # if the target is enemy- We will send some penguins including what will be created with him at this time
        elif my_penguin_amount > destination_penguin_amount and is_enemy:
            # Send penguins to the target.
            if danger_to_send_pinguins(game, my_iceberg, destination_penguin_amount + NUMBER_ADD) != True:
                if DEBUG:
                    print my_iceberg, "sends", (destination_penguin_amount + NUMBER_ADD), "penguins to", destination
                send += [[my_iceberg, destination, destination_penguin_amount+NUMBER_ADD, destination_penguin_amount, "enemy"]]
                #my_iceberg.send_penguins(destination, destination_penguin_amount + NUMBER_ADD)
     
         # if the target is attack iceberg- We sent some penguins that he lacked to deal with the enemy
        elif my_penguin_amount > destination_penguin_amount and is_attack and avoid_duplicate_sent_mine:
            # Send penguins to the target.
            if destination_penguin_amount != 0 and danger_to_send_pinguins(game, my_iceberg, destination_penguin_amount + NUMBER_ADD) != True:
                if DEBUG:
                    print my_iceberg, "sends", (destination_penguin_amount + NUMBER_ADD), "penguins to", destination, "regularrr"
                send += [[my_iceberg, destination, destination_penguin_amount+NUMBER_ADD, destination_penguin_amount, "attack"]]
                #my_iceberg.send_penguins(destination, destination_penguin_amount + NUMBER_ADD)
                avoid_duplicate_sent_mine = False
         
        elif is_defence and avoid_duplicate_defence and len(game.get_my_icebergs())+1 >= len(game.get_enemy_icebergs()):
            # Send penguins to the target.
            if destination_penguin_amount != 0 and danger_to_send_pinguins(game, my_iceberg, destination_penguin_amount + NUMBER_ADD) != True:
                if DEBUG:
                    print my_iceberg, "sends", (destination_penguin_amount + NUMBER_ADD), "penguins to", destination, "regularrr"
                send += [[my_iceberg, destination, destination_penguin_amount+NUMBER_ADD, destination_penguin_amount, "attack"]]
                avoid_duplicate_defence = False
                
        elif my_penguin_amount > destination_penguin_amount and is_natural and avoid_duplicate_sent_natural:
            # Send penguins to the target.
            if danger_to_send_pinguins(game, my_iceberg, destination_penguin_amount + 1) != True:
                if DEBUG:
                    print my_iceberg, "sends", (destination_penguin_amount + 1), "penguins to", destination
                send += [[my_iceberg, destination, destination_penguin_amount + 1, destination_penguin_amount, "natural"]]
                #my_iceberg.send_penguins(destination, destination_penguin_amount + NUMBER_ADD)
                avoid_duplicate_sent_natural = False
        
        elif is_natural and avoid_duplicate_sent_natural:   
            if DEBUG:
                print "natural_icebergs", natural_icebergs
            if danger_to_send_pinguins(game, my_iceberg, my_penguin_amount-NUMBER_STAY) != True and (my_penguin_amount-NUMBER_STAY) > 7:
                if DEBUG:
                    print my_iceberg, "sends", (my_penguin_amount-NUMBER_STAY), "penguins to", destination
                send += [[my_iceberg, destination, my_penguin_amount-NUMBER_STAY, destination_penguin_amount, "natural"]]
                natural_icebergs[destination] -= (my_penguin_amount-NUMBER_STAY)
                priority_icebergs[destination] = natural_icebergs[destination]
                if DEBUG:
                    print "natural_icebergs", natural_icebergs
                #my_iceberg.send_penguins(destination, destination_penguin_amount + NUMBER_ADD)
                        
        elif is_attack and my_iceberg.can_upgrade() == False:
            if danger_to_send_pinguins(game, my_iceberg, my_penguin_amount-NUMBER_STAY) != True:
                if DEBUG:
                    print my_iceberg, "sends", (my_penguin_amount-NUMBER_STAY), "penguins to", destination
                send += [[my_iceberg, destination, my_penguin_amount-NUMBER_STAY, destination_penguin_amount, "att"]]
                #my_iceberg.send_penguins(destination, my_penguin_amount - NUMBER_STAY)
        
        elif is_enemy and my_iceberg.can_upgrade() == False:
            if my_penguin_amount-NUMBER_STAY > 1 and len(game.get_my_icebergs()) < 4:
                if danger_to_send_pinguins(game, my_iceberg, my_penguin_amount- NUMBER_STAY) != True:
                    if DEBUG:
                        print my_iceberg, "sends", (my_penguin_amount-NUMBER_STAY), "penguins to", destination
                    send += [[my_iceberg, destination, my_penguin_amount-NUMBER_STAY, destination_penguin_amount, "ene"]]
                    #my_iceberg.send_penguins(destination, my_penguin_amount - NUMBER_STAY)

        elif my_iceberg.can_upgrade() == True:
            if danger_to_upgrade(game, my_iceberg, my_iceberg.upgrade_cost, my_iceberg.level+1) != True:
                if DEBUG:
                    print my_iceberg, "upgrade from ", my_iceberg.level, " to", (my_iceberg.level + 1)
                my_iceberg.upgrade() 
                upgrades += [my_iceberg]
        
    for i in send:
        my_ice = i[0]
        des = i[1]
        num = i[2]
        type = i[-1]
    
        my_ice.send_penguins(des, num)
        
    for my_ice in game.get_my_icebergs():
        if my_ice in upgrades:
            continue
  
        if just_one(game, my_ice, natural_icebergs): 
            just_1 = just_one(game, my_ice, natural_icebergs)
            dest = just_1[0]
            dest_penguin_amount = just_1[1] + 1
            all_he_sent = sum([d[2] for d in send if d[0] == my_ice])
            if my_ice.penguin_amount - 3 > all_he_sent:
                if DEBUG:
                    print dest, "just one to natural"
                    print "send", dest_penguin_amount
                my_ice.send_penguins(dest, dest_penguin_amount+1)
                #send += [[my_iceberg, dest, dest_penguin_amount+1, dest_penguin_amount+1, "one"]]
    
    ############## if do on me just one ##############
    #for pg in game.get_my_penguin_groups():
    #    if pg.destination in game.get_neutral_icebergs():
    #        if pg.turns_till_arrival == (pg.source.get_turns_till_arrival(pg.destination) - 2):
    #            if pg.source not in upgrades and pg.penguin_amount > 2:
    #                pg.source.send_penguins(pg.destination, 2)


