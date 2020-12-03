'''
Created on Oct 31, 2016

@author: haeejuut
'''
import time
import sys
import os

import ply.lex as lex
from ply.yacc import yacc

class FB():    
    def __init__(self, feedback, kohde, player, huonenro):
        self.huonenro = huonenro
        self.feedback = feedback
        self.kohde = kohde
        self.player = player
        self.weapons_ranged = {None: 0, 'laspistol': 4, 'heavy stubber': 5, 'lasrifle': 7}
        self.weapons_melee = {'hands': 1, 'bayonet': 3, 'chainsword': 6, 'power sword': 9}
        self.armor_list = {None: 0, 'flak': 5, 'carapace': 10}
    def set_nro(self, nro):
        self.huonenro = nro
    def get_nro(self):
        return self.huonenro
    def set_feedback(self, fb):
        self.feedback = fb
    def get_feedback(self):
        return self.feedback
    def set_kohde(self, kohde):
        self.kohde = kohde
    def get_kohde(self):
        return self.kohde
    def set_verbi(self, verbi):
        self.verbi = verbi
    def get_verbi(self):
        return self.verbi
    def player_add(self, luokka, item):
        self.player[luokka] = str(item)       
    def player_get(self):
        return self.player
    
# rakentaa sanaston ja tekee tokenizen syotteelle
# param1: kayttajan antama syote
# return: syote pilkottuna tokeneilla
def build_lex(syote):
    tokens = ['VERBI','DET','KOHDE']
    t_VERBI = r'go|look|take|inspect'
    t_ignore  = ' \t'
    t_DET = r'in|to|at'
    t_KOHDE = r'hall|locker|bunk|around|lasgun|armor|valkyrie|vulture|themis'

    def t_error(t):
        pass
    oma_lex = lex.lex()
    data = syote
    oma_lex.input(data)
        
    while True:
        tok = oma_lex.token()
        if not tok: 
            break
        print(tok)
    return oma_lex

# kielioppi ja parsiminen, yacc
# erittain simppeli kielioppi, jossa lahinna verbi ja kohde + mahdollinen valisana (D)
# S' -> lause | empty
# lause -> verbi kohde
# verbi -> VERBI
# det -> DET
# kohde -> det KOHDE
# kohde -> KOHDE
# Tarkemmin 'parser.out' tiedostossa
# parametri1: sanasto
def build_yacc(oma, syote):
    tokens = [] 
    for i in oma.lextokens:
        tokens.append(i)
    def p_lause(p):
        '''lause : verbi kohde ''' 
        p[0] = str(p[1]) + ' ' + str(p[2]) 
    def p_verbi(p):
        '''verbi : VERBI'''
        p[0] = str(p[1])
        f.set_verbi(str(p[1]))
    def p_det(p):
        '''det : DET'''  
        p[0] = str(p[1])
    def p_kohde_det(p):
        '''kohde : det KOHDE'''
        p[0] = str(p[1])+ ' ' + str(p[2])
        for i in room_objects_get(f.get_nro()):
            if str(p[2]) == i[0]:
                f.set_kohde(i[1])
                break
            else:
                f.set_kohde('Couldnt find what you meant')
    def p_kohde(p):
        '''kohde : KOHDE'''
        p[0] = str(p[1])
        for i in room_objects_get(f.get_nro()):
            if str(p[1]) == i[0]:
                f.set_kohde(i[1])
                break
            else:
                f.set_kohde('Couldnt find what you meant')                  
    def p_error(p):
        pass
    
    parser = yacc()    
    result = parser.parse(syote) 
    return result

# Kysyy syotteen ja ajaa sen lexin ja parserin lapi.
# Jos menee lapi, antaa pelaajalle palautteen syotteesta
# param1: pelaajan antama syote
def cfg_feedback(syote):
    previous = syote
    try: 
        if build_yacc(build_lex(syote), syote):     
            f.set_feedback(f.get_kohde())       
            if f.get_verbi() == 'take':
                lisaa_item(f.get_kohde())    
            elif f.get_verbi() == 'go':
                if f.get_nro() == 0: 
                    room(1,'')
                elif f.get_nro() == 1:
                    room(2,'')
                elif f.get_nro() == 2:
                    game_win()
                elif f.get_nro() == 3:
                    room(3,'')
            room(f.get_nro(), previous)
    except lex.LexError:
        f.set_feedback("Not a valid input! Try 'inspect', 'look' or 'take' ")
        room(f.get_nro(),previous)
    
def typewrite(text):
    for x in text:
        print(x, end="", flush=True)
        time.sleep(0.01)
        #0.05 hyva

def clear():
    name = os.name
    if name == 'posix':
        os.system('clear')
    elif name == 'nt' or name == 'dos':
        os.system('cls')
    else:
        print("\n" * 30)    

def ask(question):
    answer = input(question +" [y/n] > ")
    return answer in ['y', 'Y', 'Yes', 'YES', 'yes']

def lisaa_item(itemi):
    for i in room_objects_get(f.get_nro()):
        if i[1] == itemi:
            f.player_add(i[2], i[0])
            break

def tulosta():
    clear()
    print('*** STATS ***')
    print('    HEALTH: ' + f.player_get()['health'])
    print('    SANITY: ' + f.player['sanity'])
    print('*** INVENTORY ***')    
    print('    ARMOR: ' + f.player_get()['armor'])
    print('    MELEE: ' + f.player['weapon_melee'])
    print('    RANGED: ' + f.player['weapon_range'])
    print('    ITEMS: ', f.player['extra'], sep=' ', flush=True)
    print('---------------------------')

def prologi():
    clear()
    print('                       ZMMM                 MMMMMMMMMMMMMMMMMMMMM')            
    print('MMMMMMMMMMMMMMMMMMMMMMMMMM                    MMMMMMMMMMMMMMMMMMMMMMMMMM')     
    print('MMMM           .DMMMMMM    MMMMM      MMMM    MMMMMMMMMMMM8')                 
    print(' MMMMMMMMMMMMMMMM .MMM    MM. MMMM .MMMM+MM   ZMMM? MMMMMMMMMMMMMMMM,')       
    print('   MMMMMN   .MMMMMMMMMM         MMMMMM        MMM  MMMMMMM.   MMMMM')         
    print('       MMMMMMMMMM MMMMMM    MMMM  M  MMMMMMMMMMMMMMMM  MMMMMMMMMM')           
    print('      MMMMMMM  MMMM MMMMMMMMMMMMNMMM MMMMMMMMMMMMM MMMMMM  MMMM')             
    print('        M   MMMMM MMM MMMMMMM MM MMMMMM MMMMMMMMMMMM MMMMMMM')                
    print('          MMMMM  MMM MM MMMM MM MMMMM MM MMMMMMMM MMM   MMMM')                
    print('            M  MMMM MMMMM M MMMMMMMMMM~MM M MM MMM MMMM')                     
    print('              MMMM MMM MM    M MMMMMMM M    MMMMMMM MMM')                     
    print('                  MMM M       MMMMMMMMM         MMMM')                        
    print('                             , MMMMMM')                                      
    print('                             MM MMMM M M')                                    
    print('                          MMMM MM M MMM MMMM ')                               
    print('                           MMMM MMMMM  MMM M')                                
    print('                          MM     MM.    M M')
    print()
    typewrite('It is the 41st Millennium. For more than a hundred centuries the Emperor \n')
    typewrite('of Mankind has sat immobile on the Golden Throne of Earth. He is the  \n')
    typewrite('master of mankind by the will of the gods and master of a million worlds \n ')
    typewrite('by the might of his inexhaustible armies. He is a rotting carcass writhing \n')
    typewrite('invisibly with power from the Dark Age of Technology. He is the Carrion Lord \n')
    typewrite('of the vast Imperium of Man for whom a thousand souls are sacrificed every day \n')
    typewrite('so that he may never truly die.\n\nYet even in his deathless state, the Emperor ')
    typewrite('continues his eternal vigilance.\nMighty battlefleets cross the daemon-infested ')
    typewrite('miasma of the Warp, the only\nroute between distant stars, their way lit by the')
    typewrite(' Astronomican, the\npsychic manifestation of the Emperors will. Vast armies give')
    typewrite(' battle in His\nname on uncounted worlds.\n\nGreatest amongst his soldiers are the')
    typewrite(' Adeptus Astartes, the Space Marines,\nbio-engineered super-warriors. Their ')
    typewrite('comrades in arms are legion:\nthe Imperial Guard. \n\n')
    typewrite('Forget the power of technology and science, for so much has been forgotten, \n')
    typewrite('never to be relearned.\n\n')
    typewrite('Forget the promise of progress and understanding, \nfor in the grim dark future there is only war.\n\n')
    ip = str(input('Type "start" to continue or "test" to test yacc\n> '))
    if ip == 'start':
        room(0,'')
    elif ip == 'test':
        testi()
    else:
        clear()
        print('You quit')
        quit     

def room_objects_get(huonenro):
    room0_objects = {
        ('around', 'You see your locker next to your bunk. Theres an open doorway to the hall.'),
        ('hall', 'A hallway bustling with sound and movement'),
        ('bunk', 'Just a regular bed'),
        ('locker', 'Your personal locker, has your standard issue flak armor and lasgun in it'),
        ('armor', 'Flak armour made from synthetic fibres', 'armor'),
        ('lasgun','Standard guard-issue mk2 lasgun, slightly used and\ntagged with your regiment symbols','weapon_range')
        }
    room2_objects = {
        ('around', 'You see guardsmen standing in lines and a few Valkyrie-, and\nVulture-class aircraft.\nFurther ahead you see your CO, sergeant Themis'),
        ('valkyrie','Transport aircraft. They use vectored thrust to travel quickly at low altitudes.'),
        ('vulture','Gunship, used as a heavy air support vehicle for Imperial Guard ground units and the Valkyrie transport.'),
        ('themis','A sergeant for a squadron of Elysian Drop Troop. A well built man with a long beard')
        }
    room3_objects = {
        ('around','Theres a table in the middle of the room and a cabinet in the back'),
        ('map','Map of the world Davos IV'),
        ('table','You spot a map on the table along with some hastily written notes'),
        ('cabinet','You open the cabinet doors and see a half-empty bottle'),
        ('notes','Notes about the planets local habitants and fauna'),
        ('bottle','Bottle of the regiments own homebrewn sacra')        
        }
    
    if f.get_nro() == 0:
        huone = room0_objects
    elif f.get_nro() == 2:
        huone = room2_objects
        
    lista = []
    for item in huone:
        lista.append(item)
    return lista
def game_over():
    if ask("You're dead. Try again "):
        room(0,'')
    exit
    
def game_win():
    clear()
    pelaaja = f.player_get()
    if pelaaja['weapon_range'] == 'lasgun' and pelaaja['armor'] == 'armor':
        typewrite('Youve completed the game\n')
        time.sleep(4)
    if ask(' Play again ? '):
        prologi()
    sys.exit()
    
def room(nro, prev):  
    print(f.get_feedback())  
    if nro == 0:
        room0(f.player_get(), '')
    if nro == 1:
        room1(f.player_get(), '')
    if nro == 2:
        if prev == '':
            f.set_feedback('A hangar bay filled with imperial troops and equipment')
        room2(f.player_get(), prev)
    if nro == 3:
        if prev == '': 
            f.set_feedback('Dimly lit room with a circular table in the middle. Several officers standing around the table')        
        room3(f.player_get(), prev)

def room0(player, previous):
    tulosta()
    print('BARRACKS')
    typewrite('You are an imperial guardsman onboard a space marine cruiser\ncalled "The Necessary Evil".')
    typewrite(' You wake up at your quarters in\nthe guardsman barracks to a noise coming from the hall.\n')
    print('---------------------------')
    print('Previous input: ' + previous + '\n---------------------------')
    typewrite(f.get_feedback())
    print('\n---------------------------')
    user_input = str(input('> '))
    syote = user_input
    cfg_feedback(syote)
    
def room1(player, previous):
    f.set_nro(1)
    tulosta()
    print('HALLWAY')
    if previous == '':
        typewrite('You stand in the doorway and see many guardsmen running towards\nthe deplyoment area.')
        typewrite(' One of the veterans "Olgierd" seems to not be\nin a hurry and is leaning on a railing.\n')
        typewrite('You think of talking to Olgierd, but this seems like an emergency\nand you should')
        typewrite(' probably start going where the others are as well\n')
    if ask('\nDo you keep going ?'):
        room(2,'')
    typewrite('You stop to talk to the old vet. He turns to you when you approach him.\n')
    if ask('\n"Do you know whats going on lad?"'):
        typewrite('\n"Better follow the rest of the boys then. Take this, just in case."\n')
        typewrite('- Ration added -')
        f.player_add('extra', 'ration')
        time.sleep(3)
        room(2,'')
    typewrite('Seems to me they are preparing for planetfall. You probably should find\n')
    typewrite('your CO for more information. Try heading for the Officers quarters.')
    if ask('\n Do you want to follow the vets advice ?'):
        room(3,'')
    room(2,'')
    
def room2(player, previous):
    f.set_nro(2)
    tulosta()
    print('HANGAR BAY')
    print('---------------------------')
    print('Previous input: ' + previous + '\n---------------------------')
    typewrite(f.get_feedback())
    print('\n---------------------------')
    user_input = str(input('> '))
    syote = user_input
    cfg_feedback(syote)
    
def room3(player, previous):
    f.set_nro(3)
    tulosta()
    print('OFFICERS QUARTERS')
    print('---------------------------')
    print('Previous input: ' + previous + '\n---------------------------')
    typewrite(f.get_feedback())
    print('\n---------------------------')
    user_input = str(input('> '))
    syote = user_input
    cfg_feedback(syote)

def pelkka_parser(syote):
    try:
        oma = build_lex(syote)
        if oma:
            print('sanasto ok')
        if build_yacc(oma, syote):
            print('yacc/parser ok')
        else:
            print('Ei kieliopin mukainen')
        print('---------------------')
    except lex.LexError:
        print('sanastovirhe')
    
def testi(): 
    print('koeta syotetta')
    print('''    
    VERBI = r'go|look|take|inspect'
    DET = r'in|to|at'
    KOHDE = r'hall|locker|around|lasgun|armor|valkyrie|vulture|themis
    ''')
    pelkka_parser(input('\n> '))
    testi()
    
if __name__ == '__main__':
    clear()    
    f = FB(feedback='Tip: Try "look around"',
           kohde='', 
           player={
            'health':None,
            'sanity':None,
            'weapon_melee':'hands',
            'weapon_range':None,              
            'armor':None,
            'extra':[]
            },
           huonenro=0
        )
    os.system("mode con cols=85 lines=50")
    commands = ['look', 'go', 'inspect', 'take']
    f.player_add('health', 100)
    f.player_add('sanity', 100)
    f.player_add('weapon_melee', 'hands')
    f.player_add('weapon_range', 'none')
    f.player_add('armor', 'robe')
    #testi()
    prologi()      
