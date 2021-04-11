"""
This is an example for a bot.
"""
##############################  ##################################
"""
This is our bot. Tehila,Dina,Keren-or and Odel
"""
from penguin_game import *

# Calculate turns_to_arrival with bridge
def Turns_till_arrival(game, g):
    s, d = g.source, g.destination
    b = hasBridge(s, d)
    if not b:
        return g.turns_till_arrival
    if b.duration >= g.turns_till_arrival:
        return int(g.turns_till_arrival // b.speed_multiplier)
    return int((g.turns_till_arrival - b.duration) + (b.duration // b.speed_multiplier))
    

#Check if two icebergs have a bridge between them
def hasBridge(s, d):
    s_bridges = set(s.bridges)
    for b in d.bridges:
        if b in s_bridges:
            return b
    return None
    
    
# Calculatee the iceberg state (owner and penguin_amount) in x turns
def IceState(game, ice, time, sent=0):
    owner = ice.owner
    amount = ice.penguin_amount - sent
    if amount < 0:
        owner = game.get_enemy() if owner != game.get_enemy() else game.get_myself()
        amount *= -1
        
    
    groups = [x for x in game.get_my_penguin_groups()+game.get_enemy_penguin_groups() if Turns_till_arrival(game, x) <= time and x.destination == ice]
    groups.sort(key=lambda gp: Turns_till_arrival(game, gp))
    curTime = 0
    for g in groups:
        if g.decoy:
            continue
        turns_till_arrival = Turns_till_arrival(game, g)
        if owner != game.get_neutral() and not ice.equals(game.get_bonus_iceberg()):
            amount += ((turns_till_arrival-curTime) * ice.level)
        
        amount += g.penguin_amount if g.owner == owner else -g.penguin_amount
        if amount < 0:
            owner = g.owner
            amount *= -1
        if amount == 0:
            owner = game.get_neutral()
        curTime = turns_till_arrival
    
    if owner != game.get_neutral() and not ice.equals(game.get_bonus_iceberg()):  
        amount += ((time-curTime) * ice.level)
    return [owner, amount]
    
        
def iceInDanger(game, my_ice):
    ans = []
    for ice in game.get_my_icebergs():
        if ice != my_ice and IceState(game, ice, my_ice.get_turns_till_arrival(ice))[0] == game.get_enemy():   
            ans.append(ice)
    return ans
            

def bridgeDest(game, ice, groups):
    dest =  []
    for g in groups:
        if g.source == ice: 
            if g.destination.owner == game.get_enemy() and Turns_till_arrival(game, g) / ice.max_bridge_duration >= 0.5 and g.penguin_amount > game.iceberg_bridge_cost:
                dest.append(g.destination)
            #elif [gEnemy for gEnemy in game.get_my_penguin_groups() if gEnemy.destination==g.destination and hasBridge(gEnemy.source, g.destination)]:
                #dest.append(g.destination)
    return dest

#determines average size of all peguin groups of one player
def groupsize(groups):
    sum=0
    count=0
    for x in groups:
        if not x.decoy:
            sum += x.penguin_amount
            count+=1
    return sum // count


def groups(ice, group):
    count = 0
    for x in group:
        if x.destination == ice and not x.decoy:
            count += x.penguin_amount
    return count
    

#checks if there are updated icebergs
def checkLevels(group):
    for berg in group:
        if berg.level>1:
            return False
    return True
    
#group1=penguin group group2=icebergs    
def checkDestination(group1,group2):
    for i in group1:
        if i.destination in group2:
            return i.source
    return None

def hasGoodLevels(game):
    return totalLevels(game.get_my_icebergs()) >= totalLevels(game.get_enemy_icebergs())

def totalLevels(group):
    count=0
    for i in group:
        count+=i.level
    return count

def enemyDecoy(game):
    for g in game.get_enemy_penguin_groups():
        if g.decoy:
            return True
    return False
 
def attackEnemy(game, ice):
    dest = None
    for g in game.get_my_penguin_groups():
        owner, amount = IceState(game, g.destination, ice.get_turns_till_arrival(g.destination))
        if owner == game.get_enemy() and not g.decoy and g.penguin_amount > g.source.level:
            if not dest or ice.get_turns_till_arrival(g.destination) < ice.get_turns_till_arrival(dest):
                dest = g.destination
    return dest
             
def enemyTerritory(game, my_ice, amount):
    ices = sorted(game.get_all_icebergs(), key = lambda x: my_ice.get_turns_till_arrival(x))
    ices = ices[1:len(ices)//3]
    for ice in ices:
        if ice.owner != game.get_enemy():
            return False
    if sum(ice.penguin_amount for ice in ices) < (my_ice.penguin_amount - amount):
        return False
    return True
    
def have_more_icebergs(game):
    return len(game.get_my_icebergs()) >= len(game.get_enemy_icebergs()) 

def staticState(game):
    return True if not game.get_my_penguin_groups() and not game.get_enemy_penguin_groups() else False
    
def canUpgrade(game, ice):
    return ice.can_upgrade() and IceState(game, ice, ice.upgrade_cost //ice.level, ice.upgrade_cost)[0] != game.get_enemy()
def enemyDecoyPenguins(game):
    for g in game.get_enemy_penguin_groups():
        if g.decoy:
            return True
    return False
    
    
############################## The 3 of Us ##################################
def neutral_ice12(game, iceberg,turns):
    penguins_per_turn=0
    if iceberg != game.get_bonus_iceberg():
        penguins_per_turn=iceberg.penguins_per_turn
    enemies=sorted(game.get_enemy_icebergs(), key=lambda x: x.penguin_amount*(-1))
    for enemy in enemies:
        enemy_amount = enemy.penguin_amount + turns*enemy.penguins_per_turn# * penguins_per_turn
        if enemy_amount >= enemy.get_turns_till_arrival(iceberg) * penguins_per_turn:
            return False, enemy_amount-enemy.get_turns_till_arrival(iceberg) * penguins_per_turn
    return True, enemy_amount

#this function checks for a neutral iceberg if the enemy has enough penguins to conquer it from us after we conquer it.
def neutral_ice(game, iceberg,my_iceberg):
    turns=distance_between_iceberges(game,my_iceberg, iceberg)
    #if risk(game):
     #   return neutral_ice12(game, iceberg,turns)
    penguins_per_turn=0
    #if distance_from_myself(game, iceberg)<distance_from_enemy(game, iceberg):
    #    return True, 20
    if iceberg != game.get_bonus_iceberg():
        penguins_per_turn=iceberg.penguins_per_turn
    enemies=sorted(game.get_enemy_icebergs(), key=lambda x: x.penguin_amount*(-1))
    for enemy in enemies:
        if iceberg!=game.get_bonus_iceberg():
            if distance_from_myself(game, iceberg)<distance_from_enemy(game, iceberg):
                n=neutral2(game, iceberg, enemy, my_iceberg)
            else:
                n=neutral1(game, iceberg, enemy, my_iceberg)
            if  n<=0:
                continue
            else:
                return False, n
        else:
            return False, 10000
    return True, 10

def risk(game):
    for group in game.get_enemy_penguin_groups():
       if group.destination.owner==game.get_myself:
            return True
    return False

def neutral1(game, iceberg, enemy, source):
    turns=distance_between_iceberges(game,source, iceberg)
    my_icebergs=sorted(game.get_my_icebergs(), key=lambda x: x.get_turns_till_arrival(iceberg))
    for i in range(turns):
        flag1=True
        arrival=i+enemy.get_turns_till_arrival(iceberg)
        if arrival<turns:
            continue
        else:
            enemy_amount=enemy.penguin_amount+i*enemy.level
            iceberg_amount=1
            if iceberg!=game.get_bonus_iceberg():
                iceberg_amount= (arrival-turns)*iceberg.penguins_per_turn+1
            if enemy_amount>=iceberg_amount:
                return enemy_amount - iceberg_amount
                
    return 0
    
def neutral2(game, iceberg, enemy, source):
    turns=distance_between_iceberges(game,source, iceberg)
    my_icebergs=sorted(game.get_my_icebergs(), key=lambda x: x.get_turns_till_arrival(iceberg))
    for i in range(turns):
        amount=0
        flag1=True
        arrival=i+enemy.get_turns_till_arrival(iceberg)
        if arrival<turns:
            continue
        else:
            enemy_amount=enemy.penguin_amount+(i+1)*enemy.level
            iceberg_amount=1
            if iceberg!=game.get_bonus_iceberg():
                iceberg_amount= 1+(arrival-turns)*iceberg.penguins_per_turn
            if enemy_amount>=iceberg_amount:
                amount= enemy_amount - iceberg_amount
                for my_iceberg in my_icebergs:
                    #for j in range(turns):
                    #my_amount=my_iceberg.penguin_amount+(i+j)*my_iceberg.level
                    my_arrival=my_iceberg.get_turns_till_arrival(iceberg)+i+1
                    if my_arrival<arrival:
                        if my_iceberg.penguin_amount>enemy.penguin_amount:
                            amount=0
                    elif my_iceberg.penguin_amount>enemy.penguin_amount+(my_arrival-arrival)*enemy.penguins_per_turn:
                        amount=0
                if amount>0:
                    return amount
                
    return amount

def sort_by_arrival(game, iceberg):
    if iceberg.owner==game.get_enemy():
        return group_turns(game, iceberg)*10+1
    return group_turns(game, iceberg)*10

#The function checks what the amount of penguins in the iceberg will be after all the groups reach it. It returns whether the iceberg neutral,
#the amount of penguins and the time the last group arrived    
def iceberg_future_params(game, curent_iceberg, initial_amount_of_penguin, level):
    last=0 #the time the last group arrived
    x=0 #the iceberg owner
    neutral_ice=False 
    last_neutral=False
    if curent_iceberg.owner==game.get_neutral():# if the iceberg is neutral
        neutral_ice=True
    all_groups=filter(lambda x: x.destination==curent_iceberg, game.get_all_penguin_groups())
    counter=initial_amount_of_penguin 
    all_penguin_groups=sorted(all_groups,key=lambda x: sort_by_arrival(game,x))
    for group in all_penguin_groups:
        if group_turns(game,group)==last and neutral_ice==False and last_neutral==True and group.owner!=last_group.owner:
            if last_group.owner==game.get_myself():
                counter= last_group.penguin_amount-group.penguin_amount
            else:
                counter= group.penguin_amount-last_group.penguin_amount
            continue
        last_neutral=neutral_ice
        x=0
        if counter>0:
            x=1
        elif counter<0:
            x=-1
        if neutral_ice: #if the iceberg is still neutral
            if group in game.get_my_penguin_groups():
                if group.penguin_amount>abs(counter): #If the glacier that was neutral, became myself
                    neutral_ice=False
                counter+=group.penguin_amount
            else:
                if group.penguin_amount>abs(counter):#If the glacier that was neutral, became the enemy
                    neutral_ice=False
                counter+=group.penguin_amount
                counter*=(-1)
        else:  #if the iceberg is not neutral
            if group in game.get_my_penguin_groups():
                counter+=group.penguin_amount+(group_turns(game,group)-last)*level*x
            else:
                counter+=(group_turns(game,group)-last)*level*x-group.penguin_amount
            
        last=group_turns(game,group)
        last_group=group
    #counter+=x
    if counter==0:
        neutral_ice==True
    return neutral_ice, last, counter


def iceberg_future_params11(game, curent_iceberg, initial_amount_of_penguin, level, distance):
    last=0 #the time the last group arrived
    x=0 #the iceberg owner
    neutral_ice=False 
    last_neutral=False
    last_group=None
    if curent_iceberg.owner==game.get_neutral():# if the iceberg is neutral
        neutral_ice=True
    all_groups=filter(lambda x: x.destination==curent_iceberg, game.get_all_penguin_groups())
    counter=initial_amount_of_penguin 
    all_penguin_groups=sorted(all_groups,key=lambda x: sort_by_arrival(game,x))
    for group in all_penguin_groups:
        print(group.penguin_amount, last_group, counter)
        if group.turns_till_arrival>distance:
                if counter<0:
                    return True, last_group.turns_till_arrival, last_group.penguin_amount, counter
                else:
                    return False, None, None, None
        if group_turns(game,group)==last and neutral_ice==False and last_neutral==True and group.owner!=last_group.owner:
            if last_group.owner==game.get_myself():
                counter= last_group.penguin_amount-group.penguin_amount
            else:
                counter= group.penguin_amount-last_group.penguin_amount
            continue
        last_neutral=neutral_ice
        x=0
        if counter>0:
            x=1
        elif counter<0:
            x=-1
        if neutral_ice: #if the iceberg is still neutral
            if group in game.get_my_penguin_groups():
                if group.penguin_amount>abs(counter): #If the glacier that was neutral, became myself
                    neutral_ice=False
                counter+=group.penguin_amount
            else:
                if group.penguin_amount>abs(counter):#If the glacier that was neutral, became the enemy
                    neutral_ice=False
                counter+=group.penguin_amount
                counter*=(-1)
        else:  #if the iceberg is not neutral
            if group in game.get_my_penguin_groups():
                counter+=group.penguin_amount+(group_turns(game,group)-last)*level*x
            else:
                counter+=(group_turns(game,group)-last)*level*x-group.penguin_amount
        last=group_turns(game,group)
        last_group=group
    #counter+=x
    if counter==0:
        neutral_ice==True
    return False, None, None, None


def sort_by_arrival_bridge(game, iceberg, source, destination):
    if iceberg.owner==game.get_enemy():
        return group_turns_new_bridge(game,iceberg, source, destination)*10+1
    return group_turns_new_bridge(game,iceberg, source, destination)*10
    
def iceberg_future_bridge_version(game, curent_iceberg, initial_amount_of_penguin, level, source):
    last=0 #the time the last group arrived
    x=0 #the iceberg owner
    last_group=None
    neutral_ice=False 
    last_neutral=False
    if curent_iceberg.owner==game.get_neutral():# if the iceberg is neutral
        neutral_ice=True
    all_groups=filter(lambda x: x.destination==curent_iceberg, game.get_all_penguin_groups())
    counter=initial_amount_of_penguin 
    all_penguin_groups=sorted(all_groups,key=lambda x: sort_by_arrival_bridge(game,x, source, curent_iceberg))
    for group in all_penguin_groups:
        if group_turns_new_bridge(game,group, source, curent_iceberg)==last and neutral_ice==False and last_neutral==True and group.owner!=last_group.owner:
            if last_group.owner==game.get_myself():
                counter= last_group.penguin_amount-group.penguin_amount
            else:
                counter= group.penguin_amount-last_group.penguin_amount
            continue
        last_neutral=neutral_ice   
        x=0
        if counter>0:
            x=1
        elif counter<0:
            x=-1
        if neutral_ice: #if the iceberg is still neutral
            if group in game.get_my_penguin_groups():
                if group.penguin_amount>abs(counter): #If the glacier that was neutral, became myself
                    neutral_ice=False
                counter+=group.penguin_amount
            else:
                if group.penguin_amount>abs(counter):#If the glacier that was neutral, became the enemy
                    neutral_ice=False
                counter+=group.penguin_amount
                counter*=(-1)
        else:  #if the iceberg is not neutral
            if group in game.get_my_penguin_groups():
                counter+=group.penguin_amount+(group_turns_new_bridge(game,group, source, curent_iceberg)-last)*level*x
            else:
                counter+=(group_turns_new_bridge(game,group, source, curent_iceberg)-last)*level*x-group.penguin_amount
        last=group_turns_new_bridge(game,group, source, curent_iceberg)
        last_group=group
    #counter+=x
    if counter==0:
        neutral_ice==True
    return neutral_ice, last, counter


 
#return for every iceberg the amount of penguins in the iceberg will be after all the groups reach it  , using the function  iceberg_future_params
def iceberg_future(game, iceberg):
    if iceberg==game.get_bonus_iceberg():
        if iceberg.owner==game.get_myself():
            return iceberg_future_params(game, iceberg, iceberg.penguin_amount, 0)
        else:
            return iceberg_future_params(game, iceberg, iceberg.penguin_amount*(-1), 0)
    if iceberg.owner==game.get_enemy():
        return iceberg_future_params(game, iceberg, iceberg.penguin_amount*(-1), iceberg.penguins_per_turn)
    if iceberg.owner==game.get_myself():
        return iceberg_future_params(game, iceberg, iceberg.penguin_amount, iceberg.penguins_per_turn)
    if iceberg.owner==game.get_neutral():
        return iceberg_future_params(game, iceberg, iceberg.penguin_amount*(-1), iceberg.penguins_per_turn)
 
def iceberg_future_bridge(game, source, destination):
    if destination==game.get_bonus_iceberg():
        if iceberg.owner==game.get_myself():
            return iceberg_future_bridge_version(game, destination, destination.penguin_amount, 0, source)
        else:
            return iceberg_future_bridge_version(game, destination, destination.penguin_amount*(-1), 0, source)
    if destination.owner==game.get_enemy():
        return iceberg_future_bridge_version(game, destination, destination.penguin_amount*(-1), destination.penguins_per_turn, source)
    if destination.owner==game.get_myself():
        return iceberg_future_bridge_version(game, destination, destination.penguin_amount, destination.penguins_per_turn, source)
    if destination.owner==game.get_neutral():
        return iceberg_future_bridge_version(game, destination, destination.penguin_amount*(-1), destination.penguins_per_turn, source) 
            
def safe_to_upgrade(game, my_iceberg):
    if my_iceberg.penguin_amount < my_iceberg.upgrade_cost:
        return False
    if iceberg_future_params(game, my_iceberg, (my_iceberg.penguin_amount - my_iceberg.upgrade_cost), my_iceberg.penguins_per_turn + 1)[2] < 0:
        return False
    enemy_icebergs=game.get_enemy_icebergs()
    for enemy_iceberg in enemy_icebergs:
        if enemy_iceberg.penguin_amount>(my_iceberg.penguin_amount-my_iceberg.upgrade_cost)+enemy_iceberg.get_turns_till_arrival(my_iceberg)*(my_iceberg.penguins_per_turn+1):
            return False
    return True    
        
def safe_to_send(game, my_iceberg, penguin_amount, destination):
    if iceberg_future_params(game, my_iceberg, my_iceberg.penguin_amount - (penguin_amount),my_iceberg.penguins_per_turn)[2] < 0:
        return False
    return True

# the average distance from enemy icebergs    
def distance_from_enemy(game, iceberg):
    counter=0
    for ice in game.get_enemy_icebergs():
        counter+=ice.get_turns_till_arrival(iceberg)/ice.penguins_per_turn
    return float(counter+1)/len(game.get_enemy_icebergs())

# the average distance from enemy icebergs
def distance_from_myself(game, iceberg): 
    counter=0
    for ice in game.get_my_icebergs():
        counter+=ice.get_turns_till_arrival(iceberg)/(ice.penguins_per_turn)
    return float(counter+1)/len(game.get_my_icebergs())

#return the distance from the closest iceberg that can help to this iceberg
def my_closest_iceberg(game, iceberg): 
    counter=0
    my_icebergs=sorted(game.get_my_icebergs(), key=lambda x: distance_between_iceberges(game,x, iceberg))
    for ice in my_icebergs:
        if ice.penguin_amount>penguins_required_real(game, iceberg, ice):
            return ice
    return my_icebergs[0]

#Returns the amount of penguins needed to conquer an iceberg by the glacier closest to it that can help it (with the function distance_from_my_closest_iceberg)
def penguins_required(game, iceberg): 
    my_iceberg=my_closest_iceberg(game, iceberg)
    return penguins_cost(game, iceberg, my_iceberg)

#Returns the amount of penguins needed to conquer an iceberg by a particular iceberg
def penguins_required_real(game, iceberg, my_iceberg):
    distance=distance_between_iceberges(game,my_iceberg, iceberg)
    return penguins_cost(game, iceberg, my_iceberg)

#Returns the amount of penguins needed to conquer an iceberg from a particular distance
def penguins_cost(game, iceberg, my_iceberg):
    distance=distance_between_iceberges(game, my_iceberg, iceberg)
    is_neutral, last, penguin_amount=iceberg_future(game, iceberg)
    if iceberg==game.get_bonus_iceberg():
        if is_neutral:
            if distance>last:
                if neutral_ice(game, iceberg, my_iceberg)[0] or penguin_amount==0:
                    return abs(penguin_amount)
                else:
                    return abs(penguin_amount)+neutral_ice(game, iceberg, my_iceberg)[1]
            else:
                return 1000
        elif distance>last and iceberg.owner!=game.get_myself():
            return abs(penguin_amount)
        else:
            return 1000
    if iceberg.owner==game.get_neutral():
        if is_neutral:
            if distance>last:
                if neutral_ice(game, iceberg, my_iceberg)[0] or penguin_amount==0:
                    return abs(penguin_amount)
                else:
                    return abs(penguin_amount)+iceberg.penguins_per_turn*(distance)+neutral_ice(game, iceberg, my_iceberg)[1]
            else:
                return 1000
        elif distance>last and iceberg.owner!=game.get_myself():
            return abs(penguin_amount)+iceberg.penguins_per_turn*(distance-last)
        else:
            return 1000
    elif iceberg.owner==game.get_myself():
        i, t, p, c=iceberg_future_params11(game, iceberg, iceberg.penguin_amount, iceberg.penguins_per_turn, distance)
        if i and c==0 :
            return 1
        if i and distance>t:
            return abs(c)+(distance-t)*iceberg.penguins_per_turn
        elif i:
            return abs(c)
    
    if distance>last:
        return abs(penguin_amount)+iceberg.penguins_per_turn*(distance+1-last)
    else:
        if iceberg.owner==game.get_myself():
            return abs(penguin_amount)
        else:
            return abs(penguin_amount)+iceberg.penguins_per_turn*(distance)
    
def iceberg_value(game, iceberg):
    distance1=distance_from_enemy(game,iceberg)
    distance2=1#distance_from_myself(game, iceberg)
    is_neutral, last, number=iceberg_future(game, iceberg)
    if iceberg==game.get_bonus_iceberg():
        return  float(penguins_required(game, iceberg)*distance2)/(float(distance1*len(game.get_my_icebergs())*game.bonus_iceberg_penguin_bonus)/game.bonus_iceberg_max_turns_to_bonus)
    elif iceberg_future(game, iceberg)[2]>0:
        return upgrade_value(game, iceberg)
    elif iceberg.owner==game.get_myself():
        level=iceberg.penguins_per_turn
        return float(0.001*penguins_required(game, iceberg)*distance2)/((distance1*level))
    else:
        level=iceberg.penguins_per_turn
        return float(penguins_required(game, iceberg)*distance2)/((distance1*level))

def upgrade_value(game, iceberg):
    distance1=distance_from_enemy(game,iceberg)
    distance2=1#distance_from_myself(game, iceberg)
    return float(distance2*abs(iceberg.upgrade_cost))/(distance1)

def distance_between_iceberges(game,source, destination):
    bridge_duration=0
    for bridge in source.bridges:
        if destination in bridge.get_edges():
            bridge_duration=bridge.duration
            break
    if bridge_duration==0:
        return source.get_turns_till_arrival(destination)
    distance=source.get_turns_till_arrival(destination)
    if distance/game.iceberg_bridge_speed_multiplier>bridge_duration:
        distance= (distance/game.iceberg_bridge_speed_multiplier-bridge_duration)*game.iceberg_bridge_speed_multiplier+ bridge_duration
    else:
        distance=distance/game.iceberg_bridge_speed_multiplier
    return int(distance)#source.get_turns_till_arrival(destination)# distance
    
def group_turns(game,group):
    bridge_duration=0
    destination=group.destination
    source=group.source
    for bridge in source.bridges:
        if destination in bridge.get_edges():
            bridge_duration=bridge.duration
            break
    if bridge_duration==0:
        return group.turns_till_arrival
    distance=group.turns_till_arrival
    if distance>bridge_duration:
        distance= (distance-bridge_duration)*game.iceberg_bridge_speed_multiplier+ bridge_duration
    else:
        distance=distance
    return int(distance)#group.turns_till_arrival## distance
    
def group_turns_new_bridge(game,group, source, destination):
    if group.destination!=destination or group.source!=source:
        return group_turns(game,group)
    bridge_duration=game.iceberg_max_bridge_duration
    destination=group.destination
    source=group.source
    distance=group.turns_till_arrival
    if distance/game.iceberg_bridge_speed_multiplier>bridge_duration:
        distance= (distance/2-bridge_duration)*2+ bridge_duration#/game.iceberg_bridge_speed_multiplier
    else:
        distance=distance/game.iceberg_bridge_speed_multiplier
    return int(distance)+1#group.turns_till_arrival## distance+1
 
def bridge_value(game, source, destination):
    #checks if the bridg is already exist
    for bridge in source.bridges:
        if destination in bridge.get_edges():
            return -1
    bridg_cost=game.iceberg_bridge_cost
    if source.penguin_amount<bridg_cost or not source.can_create_bridge(destination) or not safe_to_send(game,source, bridg_cost,destination):
        return -1
    is_neutral, last_group_bridge, value_with_bridge=iceberg_future_bridge(game, source, destination)
    if value_with_bridge<0:
        return -1
    is_neutral, last_group_not_bridge, value_without_bridge=iceberg_future(game, destination)
    value_with_bridge-=bridg_cost
    if last_group_bridge<last_group_not_bridge:
        if destination!= game.get_bonus_iceberg():
            return value_with_bridge - value_without_bridge+(last_group_not_bridge-last_group_bridge)*destination.level 
        else:
            return value_with_bridge - value_without_bridge+(last_group_not_bridge-last_group_bridge)*(len(game.get_my_icebergs())*game.bonus_iceberg_penguin_bonus)/game.bonus_iceberg_max_turns_to_bonus
    return value_with_bridge - value_without_bridge

def p_bridge(game, source, destination):
    turns=source.get_turns_till_arrival(destination)
    a=penguins_cost(game,destination, (turns-1)/2+1)+4
    if a< source.penguin_amount and safe_to_send(game, source, a, destination):
        return a-4
    b=penguins_cost(game, destination, turns)
    return b
    
################################# us ###################################
"""
This is an example for a bot.
"""
import operator
from penguin_game import *

################ Global variable ############
VULNERABLE_ICEBERG = 1
NUMBER_ADD = 1
NUMBER_STAY = 3
PRECENT_TO_HELP = 0.2
already_attacked = False
attacked = None
attackers = list()
real_shin_time = 0

################ Get closest ##############
def get_closest_natural_iceberg(game, my_iceberg):
    return min(game.get_neutral_icebergs(), key = lambda ice: ice.get_turns_till_arrival(my_iceberg))
    
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
def get_closest_natural_iceberg_not_sent_yet(game, my_iceberg):
    natural_icbergs_no_in_way = [d.destination for d in game.get_all_penguin_groups() if d.decoy == False]
    natural_icebergs_no_group_sent = [ice for ice in game.get_neutral_icebergs() if not ice in natural_icbergs_no_in_way]
    if len(natural_icebergs_no_group_sent) != 0:
        return min(natural_icebergs_no_group_sent, key = lambda ice: ice.get_turns_till_arrival(my_iceberg))
 
def get_closest_natural_iceberg_min_pinguin_not_sent_yet(game, my_iceberg):
    natural_icbergs_no_in_way = [d.destination for d in game.get_all_penguin_groups() if d.decoy == False]
    natural_icebergs_no_group_sent = [ice for ice in game.get_neutral_icebergs() if not ice in natural_icbergs_no_in_way]
    if len(natural_icebergs_no_group_sent) != 0:
        min_ice = min(natural_icebergs_no_group_sent, key = lambda ice: ice.penguin_amount)
        min_icebergs = [ice for ice in natural_icebergs_no_group_sent if ice.penguin_amount == min_ice.penguin_amount]
        return min(min_icebergs, key = lambda ice: ice.get_turns_till_arrival(my_iceberg))

def get_closest_enemy_iceberg_min_pinguin(game):
    return min(game.get_enemy_icebergs(), key = lambda ice: ice.penguin_amount)

      
def get_closest_natural_iceberg_max_level_not_sent_yet(game, my_iceberg):
    natural_icbergs_in_way = [d.destination for d in game.get_all_penguin_groups() if d.decoy == False]
    natural_icebergs_no_group_sent = [ice for ice in game.get_neutral_icebergs() if not ice in natural_icbergs_in_way]
    ice_with_max_level = [ice for ice in natural_icebergs_no_group_sent if ice.level > 1]
    if len(ice_with_max_level) != 0:
        min_dest_max_level = min(ice_with_max_level, key = lambda ice: ice.get_turns_till_arrival(my_iceberg))
        if min_dest_max_level.get_turns_till_arrival(my_iceberg) < 15:
            return min_dest_max_level
            
def change_from_max_natural_to_natural(game, my_iceberg):
    icebergs = game.get_my_icebergs()
    num_my_icebergs = len(icebergs)
    num_my_pg = len(game.get_my_penguin_groups())
    ene_pg = game.get_enemy_penguin_groups()
    if num_my_icebergs == 1 and num_my_pg == 0:
        if [pg for pg in ene_pg if pg.destination != game.get_bonus_iceberg() and pg.destination.level == 1 and pg.decoy == False] != []:
            return True
    if num_my_icebergs > 1:
        max_ice = max(icebergs, key = lambda ice : ice.penguin_amount*ice.level)
        ices = [ice for ice in icebergs if ice.penguin_amount*ice.level == max_ice.penguin_amount*max_ice.level]
        if len(ices) > 1:
            natural = get_closest_natural_iceberg_max_level_not_sent_yet(game, my_iceberg)
            max_ice = min(ices, key = lambda ice: ice.get_turns_till_arrival(natural))
        if my_iceberg != max_ice:
            return True
        if my_iceberg.level > 2 and num_my_pg == 0 and len(ene_pg) > 0:
            if num_my_icebergs == len(game.get_enemy_icebergs()):
                return True
    return False
  
def change_from_bonus_to_natural(game, my_iceberg):
    bonus = game.get_bonus_iceberg()
    if bonus and bonus.penguin_amount > 14:
        my_icebergs = game.get_my_icebergs()
        enemy_icebergs = game.get_enemy_icebergs()
        natural_penguin_amount = dict()
    
        for nat_ice in game.get_neutral_icebergs():
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
    for penguins_group in game.get_my_penguin_groups():
        if penguins_group.destination == ice and penguins_group.decoy == False:
            my_to_ice += [(penguins_group.turns_till_arrival, penguins_group.penguin_amount)]
    for penguins_group in game.get_enemy_penguin_groups():
        if penguins_group.destination == ice and penguins_group.decoy == False:
            enemy_to_ice += [(penguins_group.turns_till_arrival, -penguins_group.penguin_amount)]
    all_to_ice = sorted(my_to_ice + enemy_to_ice, key = lambda pg: pg[0])
    
    my = True if ice.owner == game.get_myself() else False
    enemy =  True if ice.owner == game.get_enemy() else False
    natural =  True if ice.owner == game.get_neutral() else False
    
    

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
            print i[0], last_turn, penguin_amount,penguins
        last_turn = i[0]
    
    num_turns = last_turn 
    if my:
        return ('my', penguin_amount, last_turn)
    if enemy:
        return ('enemy', penguin_amount, num_turns)
    if natural:
        return ('natural', penguin_amount, num_turns)


############ destination penguin amount #############

def get_destination_pinguin_amount(game, type, my_iceberg, destination, icebergs_attacked, bridges):
    destination_penguin_amount = destination.penguin_amount
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
        print destination_penguin_amount, "enemy need "
        print destination_distance, "enemy deistance"
        print owner_munp_munt, "owner_munp_munt"
        return destination_penguin_amount
            
    # enemy iceberg case
    if type == 'attack':
        # The amount of penguins attacking
        # iceberg[0]- type : iceberg
        # iceberg[1]- type : int, the number of penguins in the way to my iceberg
        
        if destination in game.get_neutral_icebergs():
            destination_penguin_amount = [att[1]+1 for att in icebergs_attacked if att[0] == destination][0]
            print destination_penguin_amount, "natural attacked need "
            print my_iceberg.penguin_amount, "i have now"
            return destination_penguin_amount

        else:
            attackers_amount = [iceberg[1] for iceberg in icebergs_attacked if iceberg[0] == destination]
     
            # The amount of penguins already sent
            sender_amount = get_sum_my_penguin_groups_to_my_icberg(game, destination)
 
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


def just_one(game, my_iceberg):
    for pg in game.get_enemy_penguin_groups():
        if pg.destination in game.get_neutral_icebergs() and len([p for p in game.get_enemy_penguin_groups() if p.destination == pg.destination]) == 1 and pg.decoy == False:
            #checks if the iceberg closts to my icebergs and not too far- because they take it from me immidiatly
            if pg.penguin_amount - pg.destination.penguin_amount == 1:
                my_to_it = sum([penguins_group.penguin_amount for penguins_group in game.get_my_penguin_groups() if penguins_group.destination == pg.destination and penguins_group.decoy == False])
               #num to send it is the diffrence between the turn that the enemy arrived to the destination, until my penguins 
                num_to_send = my_iceberg.get_turns_till_arrival(pg.destination) - pg.turns_till_arrival
                num_to_send *= pg.destination.level
                if my_to_it < num_to_send:
                    if num_to_send <= 3 and num_to_send > 1:
                        if my_iceberg.penguin_amount > num_to_send + 1:
                            return (pg.destination, num_to_send)
            if pg.penguin_amount - pg.destination.penguin_amount == 2:
                my_to_it = sum([penguins_group.penguin_amount for penguins_group in game.get_my_penguin_groups() if penguins_group.destination == pg.destination and penguins_group.decoy == False])
               #num to send it is the diffrence between the turn that the enemy arrived to the destination, until my penguins 
                num_to_send = my_iceberg.get_turns_till_arrival(pg.destination) - pg.turns_till_arrival +1 
                num_to_send *= pg.destination.level
                if my_to_it < num_to_send:
                    if num_to_send <= 3 and num_to_send > 1:
                        if my_iceberg.penguin_amount > num_to_send + 1:
                            return (pg.destination, num_to_send)

def just_one_with_bridge(game, my_iceberg):
    for pg in game.get_enemy_penguin_groups():
        if pg.destination in game.get_neutral_icebergs() and pg.decoy == False:
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
    return sum / num_ice
        
        
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
        

        if all_to_me > all_p:
            icebergs_attacked += [(iceberg,icebergs[iceberg])]

    return icebergs_attacked

def get_attack_iceberg_with_natural(game):
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
    
    natural_sent = [pg.destination for pg in game.get_my_penguin_groups() if pg.destination in game.get_neutral_icebergs() and pg.decoy == False]
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
                if des_penguin_amount_need > des_penguin_amount_actually*2.5 and len(game.get_my_icebergs()) < 6:
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
                
def effective_use_natural_bridge(game, bridges_to_natural):
    for br in bridges_to_natural:
        natural_ice = [ice for ice in br.get_edges() if ice in game.get_neutral_icebergs()][0]
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
    my_bridges = [br for br in bridges if my_iceberg in br.get_edges()]
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
        penguin_amount_need = enemy_iceberg.penguin_amount + distance*enemy_iceberg.penguins_per_turn
        if my_iceberg.penguin_amount > penguin_amount_need:
            return True
    if len(all_enemy_icebergs) == 1:
        if my_iceberg.penguin_amount > all_enemy_icebergs[0].penguin_amount + all_enemy_icebergs[0].get_turns_till_arrival(my_iceberg)*all_enemy_icebergs[0].penguins_per_turn:
            return True
        
    return False
    
################## hero iceberg #############
def i_am_hero(game, my_iceberg):
    if not game.get_bonus_iceberg():
        return False
    dice_ice_sum_distances = dict() 
    for my_ice in game.get_my_icebergs():
        sum = 0
        sum = my_ice.get_turns_till_arrival(game.get_bonus_iceberg())
        dice_ice_sum_distances[my_ice] = sum
    max_ice = max(dice_ice_sum_distances.iteritems(), key = operator.itemgetter(1))[0]
    
    if max_ice == my_iceberg and my_iceberg.level < 4:
        if len(game.get_my_icebergs()) > len(game.get_enemy_icebergs()):
            return True
    return False
    
def i_am_week(game, my_iceberg):
    if my_iceberg.level == 1:
        return True
    if my_iceberg.level < 4 and game.turn > 110:
        return True
        
        
################# win before teko - thanks oogifletzet! #####################
def best_to_conquer(game):
    '''
    # Neutral
    if game.get_neutral_icebergs():
        distances_dict = dict()
        for neutral in game.get_neutral_icebergs():
            distances_dict[neutral] = sum([x.get_turns_till_arrival(neutral) for x in game.get_my_icebergs()])
        return min(distances_dict.items(), key=lambda x: x[1])[0]
        # Enemy
    else:
        return min(game.get_enemy_icebergs(), key=lambda x: x.penguin_amount)
    '''
    distances_dict = dict()
    for iceberg in game.get_enemy_icebergs() + game.get_neutral_icebergs():
        dist = min([iceberg.get_turns_till_arrival(my_iceberg) for my_iceberg in game.get_my_icebergs()])
        if dist not in distances_dict:
            distances_dict[dist] = []
        distances_dict[dist] += [iceberg]

    min_distance = min(distances_dict)
    neutrals = filter(lambda x: x.owner == game.get_neutral(), distances_dict[min_distance])
    if neutrals:
        return min(neutrals, key=lambda x: x.penguin_amount)
    return min(distances_dict[min_distance], key=lambda x: x.penguin_amount)


def game_over(game):
    destination = best_to_conquer(game)
    global attackers
    for attacker in attackers:
        attacker[0].send_penguins(destination, attacker[1])
    #   iceberg.send_penguins(twin_from_twins(iceberg), iceberg.penguin_amount)

def get_attacking_groups(game, iceberg):
    return [group for group in game.get_enemy_penguin_groups() if group.destination == iceberg]

def get_attackers(game):
    destination = best_to_conquer(game)
    my_icebergs = sorted(game.get_my_icebergs(), key=lambda x: x.get_turns_till_arrival(destination))

    amount_to_conquer = destination.penguin_amount + 1

    my_attackers = list()

    current_amount = 0
    will_born_penguins = 0
    current_dist = my_icebergs[0].get_turns_till_arrival(destination)

    while my_icebergs and (amount_to_conquer + will_born_penguins >= current_amount):
        my_amount = my_icebergs[0].penguin_amount
        if destination.owner == game.get_enemy():
            my_amount -= my_icebergs[0].bridge_cost + 1
        my_amount -= sum([g.penguin_amount for g in filter(lambda g: g.turns_till_arrival < current_dist, get_attacking_groups(game, my_icebergs[0]))])
        if my_amount > 0:
            if destination.owner == game.get_neutral() and my_amount > amount_to_conquer:
                my_amount = amount_to_conquer
            my_attackers.append([my_icebergs[0], my_amount])
            if destination.owner == game.get_enemy():
                will_born_penguins = destination.penguins_per_turn * max([attacker[0].get_turns_till_arrival(destination) for attacker in my_attackers])
            current_dist = my_icebergs[0].get_turns_till_arrival(destination)
            current_amount = sum([attacker[1] for attacker in my_attackers])
        my_icebergs.pop(0)
    #print "amount_to_conquer + will_born_penguins:", amount_to_conquer + will_born_penguins
    if current_amount < amount_to_conquer + will_born_penguins:
        return None
    return my_attackers


def shin_time(game):
    '''
    return game.max_turns - max([iceberg.get_turns_till_arrival(best_to_conquer(game)) for iceberg in game.get_my_icebergs()])
    '''
    my_attackers = get_attackers(game)
    destination = best_to_conquer(game)
    if my_attackers:
        max_dist = max([attacker[0].get_turns_till_arrival(destination) for attacker in my_attackers])
        if destination.owner == game.get_enemy():
            return game.max_turns - ((max_dist - 1) // 2 + 1) 
        else:
            return game.max_turns - max_dist
    #elif attackers:
    #    return game.max_turns - attackers[-1].get_turns_till_arrival(best_to_conquer(game)) // 2
    return game.max_turns + 1
    
ice_end = None
nat1_end =None
nat2_end = None
distance1_end = None
distance2_end = None
def finish_time(game, my_iceberg):

    global ice_end 
    global nat1_end 
    global nat2_end 
    global distance1_end
    global distance2_end

    ###### ICE1 ########
    #if not ice1_end:
    ice = game.get_my_icebergs()[0]
    print ice, ice.penguin_amount
    nat1 = get_closest_natural_iceberg_not_sent_yet(game, ice)
    distance1 = ice.get_turns_till_arrival(nat1) 
    print nat1, nat1.penguin_amount, distance1
    
    ####### ICE1 ########
    if game.turn == game.max_turns-distance1:
        ice_end = ice
        nat1_end = nat1
        distance1_end = distance1
        ice_end.create_bridge(nat1_end)
        return True
    
    elif distance1_end and game.turn == game.max_turns-distance1_end+1:
        print "need to send"
        ice_end.send_penguins(nat1_end, int((nat1_end.penguin_amount)*1.5))
        return True
    
    elif distance1_end and game.turn == game.max_turns-distance1_end+ice_end.max_bridge_duration-1:
        ice_end.create_bridge(nat1_end)
        return True
    
    


bridges_to_natural = dict()
not_relevant_bridges_to_natural = dict()
first_des = None
second_des = None
def tricky(game):
    """
    Makes the bot run a single turn.

    :param game: the current game state.
    :type game: Game
    """
     
    avoid_duplicate_sent_mine = True
    avoid_duplicate_bonus = True 
    avoid_duplicate_sent_natural = True
    avoid_duplicate_defence = True  
    
    dict_icebergs_num_briges = intialize_number_bridges_from_my_icebergs_to_this_destination(game)

    send = []
    upgrades = []
    
    for my_iceberg in game.get_my_icebergs():
        
        if game.turn > 280:
            if finish_time(game, my_iceberg):
                return
        # The amount of penguins in my iceberg.
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
            print destination, "attack "
            destination_penguin_amount = get_destination_pinguin_amount(game, 'attack', my_iceberg, destination, icebergs_attacked, bridges)
        
        elif is_win(game, my_iceberg):
            destination = game.get_enemy_icebergs()[0]
            is_make_me_winner = True
            print destination, "got winner "
            destination_penguin_amount = get_destination_pinguin_amount(game, 'winner', my_iceberg, destination, icebergs_attacked, bridges)
            
        elif my_iceberg in bridges_to_natural.keys() and bridges_to_natural[my_iceberg]:
            destination = get_my_partner_in_bridge(game, my_iceberg, my_iceberg.bridges[0])
            is_bridge = True
            print destination, "bridge "
            bridges_to_natural[my_iceberg] = False
            not_relevant_bridges_to_natural[my_iceberg] = destination
            destination_penguin_amount = get_destination_pinguin_amount(game, 'natural', my_iceberg, destination, icebergs_attacked, bridges)
        
        elif len(bridges) > 0:
            destination = get_my_partner_in_bridge(game, my_iceberg, bridges[0])
            is_bridge = True
            print destination, "bridge "
            destination_penguin_amount = get_destination_pinguin_amount(game, 'bridge', my_iceberg, destination, icebergs_attacked, bridges)
            
        elif len(vulnerable_icebergs) != 0 and my_iceberg not in vulnerable_icebergs:
            destination = get_closest_vulnerable_iceberg(game, my_iceberg, vulnerable_icebergs)
            is_defence = True
            print destination, "defence "
            destination_penguin_amount = get_destination_pinguin_amount(game, 'defence', my_iceberg, destination, icebergs_attacked, bridges)

        elif get_closest_natural_iceberg_max_level_not_sent_yet(game, my_iceberg):
            destination = get_closest_natural_iceberg_max_level_not_sent_yet(game, my_iceberg)
            is_natural = True
            is_max_level = True
            print destination, " max level natural"
            destination_penguin_amount = get_destination_pinguin_amount(game, 'natural', my_iceberg, destination, icebergs_attacked, bridges)
            
        elif get_closest_enemy_iceberg(game, my_iceberg):
            destination = get_closest_enemy_iceberg(game, my_iceberg)
            is_enemy = True
            print destination, " enemy"
            destination_penguin_amount = get_destination_pinguin_amount(game, 'enemy', my_iceberg, destination, icebergs_attacked, bridges)
     
        else:
            if len(game.get_my_icebergs()) > 2:
                destination = get_closest_natural_iceberg_not_sent_yet(game, my_iceberg) # type: Iceberg
            else:
                destination = get_closest_natural_iceberg_min_pinguin_not_sent_yet(game, my_iceberg) # type: Iceberg
            is_natural = True
            print destination, " natural"
            destination_penguin_amount = get_destination_pinguin_amount(game, 'natural', my_iceberg, destination, icebergs_attacked, bridges)
    
        """if is_max_level and change_from_max_natural_to_natural(game, my_iceberg):
            is_max_level = False
            destination = get_closest_natural_iceberg_min_pinguin_not_sent_yet(game, my_iceberg) # type: Iceberg
            if destination:
                is_natural = True
                print destination, " natural"
                destination_penguin_amount = get_destination_pinguin_amount(game, 'natural', my_iceberg, destination, icebergs_attacked, bridges) + 1
        
        #if is_bonus and change_from_bonus_to_natural(game, my_iceberg):
        #   is_bonus = False
        #   destination = get_closest_natural_iceberg_min_pinguin_not_sent_yet(game, my_iceberg) # type: Iceberg
        #   if destination:
        #       is_natural = True
        #       print destination, " natural"
        #       destination_penguin_amount = get_destination_pinguin_amount(game, 'natural', my_iceberg, destination, icebergs_attacked, bridges) + 1
        
        if (my_penguin_amount < destination_penguin_amount and is_bonus) or (is_attack and destination_penguin_amount == 0):
            if get_closest_natural_iceberg_not_sent_yet(game, my_iceberg):
                destination = get_closest_natural_iceberg_not_sent_yet(game, my_iceberg)
                destination_penguin_amount = destination.penguin_amount 
                is_natural = True
                is_attack = False
                is_bonus = False
                print destination, " natural"
            else:
                is_attack = False
                is_bonus = False
        
        if my_penguin_amount <= destination_penguin_amount and is_enemy and len(game.get_my_icebergs()) <= 3:
            nat = get_closest_natural_iceberg_min_pinguin_not_sent_yet(game, my_iceberg)
            if nat:
                destination = nat
                destination_penguin_amount = destination.penguin_amount 
                is_natural = True
                is_enemy = False
                print destination, " natural"
        
        if is_enemy and len(game.get_my_icebergs()) == len(game.get_enemy_icebergs()) and [pg for pg in game.get_enemy_penguin_groups() if pg.destination in game.get_neutral_icebergs() and pg.decoy == False] != []:
            nat = get_closest_natural_iceberg_min_pinguin_not_sent_yet(game, my_iceberg)
            if nat:
                destination = nat
                destination_penguin_amount = destination.penguin_amount 
                is_natural = True
                is_enemy = False
                print destination, " natural"
                
        if is_enemy and (i_am_hero(game, my_iceberg) or i_am_week(game, my_iceberg)):
            is_hero = True
            is_enemy = False"""
            
        if len(game.get_enemy_icebergs()) == 1 and len(game.get_my_icebergs()) == 1 and not is_make_me_winner:
            if len(game.get_enemy_penguin_groups()) == 0:
                if my_iceberg.can_upgrade():
                    my_iceberg.upgrade()
                    return
                else:
                    return
            
            elif len(game.get_enemy_penguin_groups()) == 1:
                is_enemy = False
            
        if is_enemy and len(game.get_my_icebergs()) < 3:
            is_enemy = False
        
        if is_attack and my_iceberg != destination:
            if sum([pg.penguin_amount for pg in game.get_enemy_penguin_groups() if pg.destination == destination]) >= sum([pg.penguin_amount for pg in game.get_my_penguin_groups() if pg.destination == destination]):
                if [my_iceberg,destination] not in [br.get_edges() for br in [br for br in my_iceberg.bridges]]:
                    my_iceberg.create_bridge(destination)
                    print "no bridge"
                    print  [br.get_edges() for br in [br for br in my_iceberg.bridges]]
                    return
                
        #if i do just one and he created a bridges
        if len(game.get_my_penguin_groups()) == 1:
            if len(game.get_enemy_penguin_groups()) == 1:
                my = game.get_my_penguin_groups()[0]
                enemy = game.get_enemy_penguin_groups()[0]
                if my.destination == enemy.destination:
                    bridges = enemy.destination.bridges
                    if len(bridges) == 1 and bridges[0].owner == game.get_enemy():
                        my_iceberg.create_bridge(my.destination)
                        return
                        
            
            
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
            send += [[my_iceberg, destination, destination_penguin_amount+1, destination_penguin_amount, "winner"]]
            
        elif (len(game.get_enemy_penguin_groups()) == 0 or is_natural) and my_iceberg.can_upgrade() == True and not is_bridge:
            if danger_to_upgrade(game, my_iceberg, my_iceberg.upgrade_cost, my_iceberg.level+1) != True:
                print my_iceberg, "upgrade from ", my_iceberg.level, " to", (my_iceberg.level + 1)
                my_iceberg.upgrade() 
                upgrades += [my_iceberg]
        
        elif my_penguin_amount > destination_penguin_amount and  is_bonus and avoid_duplicate_bonus:
            if danger_to_send_pinguins(game, my_iceberg, destination_penguin_amount+1) != True:
                print my_iceberg, "sends", (destination_penguin_amount +1), "penguins to", destination
                send += [[my_iceberg, destination, destination_penguin_amount+1, destination_penguin_amount, "bonus"]]
                #avoid_duplicate_bonus = False
                
        elif is_bridge:
            if danger_to_send_pinguins(game, my_iceberg, destination_penguin_amount+1) != True:
                print my_iceberg, "sends", (destination_penguin_amount+1), "penguins to", destination
                send += [[my_iceberg, destination, destination_penguin_amount+1, destination_penguin_amount, "bridge"]]

        # if the target is enemy- We will send some penguins including what will be created with him at this time
        elif my_penguin_amount > destination_penguin_amount and is_enemy:
            # Send penguins to the target.
            if danger_to_send_pinguins(game, my_iceberg, destination_penguin_amount + NUMBER_ADD) != True:
                print my_iceberg, "sends", (destination_penguin_amount + NUMBER_ADD), "penguins to", destination
                send += [[my_iceberg, destination, destination_penguin_amount+NUMBER_ADD, destination_penguin_amount, "enemy"]]
                #my_iceberg.send_penguins(destination, destination_penguin_amount + NUMBER_ADD)
        
        elif is_attack and my_iceberg.level == 1 and len(game.get_my_icebergs()) > 4:
            if my_iceberg.can_upgrade() == True:
                if danger_to_upgrade(game, my_iceberg, my_iceberg.upgrade_cost, my_iceberg.level+1) != True:
                    print my_iceberg, "upgrade from ", my_iceberg.level, " to", (my_iceberg.level + 1)
                    my_iceberg.upgrade()
                    upgrades += [my_iceberg]
                
         # if the target is attack iceberg- We sent some penguins that he lacked to deal with the enemy
        elif my_penguin_amount > destination_penguin_amount and is_attack and avoid_duplicate_sent_mine:
            # Send penguins to the target.
            if destination_penguin_amount != 0 and danger_to_send_pinguins(game, my_iceberg, destination_penguin_amount + NUMBER_ADD) != True:
                print my_iceberg, "sends", (destination_penguin_amount + NUMBER_ADD), "penguins to", destination, "regularrr"
                send += [[my_iceberg, destination, destination_penguin_amount+NUMBER_ADD, destination_penguin_amount, "attack"]]
                #my_iceberg.send_penguins(destination, destination_penguin_amount + NUMBER_ADD)
                avoid_duplicate_sent_mine = False
         
        elif is_defence and avoid_duplicate_defence and len(game.get_my_icebergs())+1 >= len(game.get_enemy_icebergs()):
            # Send penguins to the target.
            if destination_penguin_amount != 0 and danger_to_send_pinguins(game, my_iceberg, destination_penguin_amount + NUMBER_ADD) != True:
                print my_iceberg, "sends", (destination_penguin_amount + NUMBER_ADD), "penguins to", destination, "regularrr"
                send += [[my_iceberg, destination, destination_penguin_amount+NUMBER_ADD, destination_penguin_amount, "attack"]]
                avoid_duplicate_defence = False
                
        elif my_penguin_amount > destination_penguin_amount and is_natural and avoid_duplicate_sent_natural:
            # Send penguins to the target.
            if danger_to_send_pinguins(game, my_iceberg, destination_penguin_amount + 1) != True:
                print my_iceberg, "sends", (destination_penguin_amount + 1), "penguins to", destination
                send += [[my_iceberg, destination, destination_penguin_amount + 1, destination_penguin_amount, "natural"]]
                #my_iceberg.send_penguins(destination, destination_penguin_amount + NUMBER_ADD)
                avoid_duplicate_sent_natural = False
                        
        elif is_attack and my_iceberg.can_upgrade() == False:
            if danger_to_send_pinguins(game, my_iceberg, my_penguin_amount-NUMBER_STAY) != True:
                print my_iceberg, "sends", (my_penguin_amount-NUMBER_STAY), "penguins to", destination
                send += [[my_iceberg, destination, my_penguin_amount-NUMBER_STAY, destination_penguin_amount, "att"]]
                #my_iceberg.send_penguins(destination, my_penguin_amount - NUMBER_STAY)
        
        elif is_enemy and my_iceberg.can_upgrade() == False:
            if my_penguin_amount-NUMBER_STAY > 1 and len(game.get_my_icebergs()) < 4:
                if danger_to_send_pinguins(game, my_iceberg, my_penguin_amount- NUMBER_STAY) != True:
                    print my_iceberg, "sends", (my_penguin_amount-NUMBER_STAY), "penguins to", destination
                    send += [[my_iceberg, destination, my_penguin_amount-NUMBER_STAY, destination_penguin_amount, "ene"]]
                    #my_iceberg.send_penguins(destination, my_penguin_amount - NUMBER_STAY)

        elif my_iceberg.can_upgrade() == True:
            if danger_to_upgrade(game, my_iceberg, my_iceberg.upgrade_cost, my_iceberg.level+1) != True:
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
 
        if just_one(game, my_ice): 
            just_1 = just_one(game, my_ice)
            dest = just_1[0]
            dest_penguin_amount = just_1[1] + 1
            all_he_sent = sum([d[2] for d in send if d[0] == my_ice])
            if my_ice.penguin_amount - 3 > all_he_sent:
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


