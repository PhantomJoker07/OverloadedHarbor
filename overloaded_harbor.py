# IMPORTS #

from logger import *
from distributions import *
from numpy.random import choice
from queue import Queue
from queue import PriorityQueue


class Overloaded_Harbor():

    def __init__(self):

        # PROBLEM's PARAMETERS #
        self.dock_count = 3
        self.tugboat_count = 1

        self.lambda_ship_arrival = 1/8

        self.small_ship = 9,1       #format: size_ship = u , o^2
        self.medium_ship = 12,2
        self.large_ship = 18,3

        self.small_prob = 0.25
        self.medium_prob = 0.25
        self.large_prob = 0.5

        self.lambda_tow_to_dock = 1/2 
        self.lambda_tow_to_port = 1/1  

        self.lambda_tugboat_alone = 1/0.25

        self.time_lapse = 1
        self.current_time = 0

        # STATES #
        self.tugboat_state = 0         # 0 -> Waiting in docks, 1 -> Traveling to port, 2 -> Traveling to dock  3 -> Waiting in port
        self.tugboat_scort = 0         # 0 -> the tugboat is traveling alone, ID -> the tugboat is scorting a ship with said ID
        self.tugboat_arrived = False   # True -> tugboat arrived at a destination, used only when the event of arrival is triggered
        self.st_ship_waiting = False   # False -> Port is empty, True -> There is at least one ship in port
        self.st_load_finished = False  # False -> There is no ship waiting in a dock, True -> There is at least one ship waiting in a dock
        self.st_docks_free = True      # False -> There is no free dock, True -> There is at least a free dock
    
        # OTHER VARIABLES #
        self.answer = 0
        self.dock_avaliability = [] # The avaliability of each dock,  0 -> Avaliable, 1 -> Loading, 2 -> Finished
        self.docked_ships = []      # The Id of the ship docked in the i-th dock, 0 means no ship is docked
        self.docked_times = []      # The time when a ship was docked to the i-th dock, 0 means no ship is docked
        self.port_queque = Queue()  # Queue of ships with values [ID, SIZE, ARRIVAL TIME] that represent the ship id, size and arrival time
        self.docks_queque = PriorityQueue()  # (priority,dock_id), priority Queue of the docks with a ship that finished loading, the priority is given by the time of the finished load
        self.ships_dict = {}   #Key is the ship ID and value is the [size, arrival_time], only contains ships that are being attended (not the ones that left or are waiting in port)
        self.size_params = {}  #Key is the ship size: (small, medium, large) and value is the pair u, o^2
        self.wait_times = []   #An array with the wait time of each ship that reach the port and is scorted to the docks
        self.Events = PriorityQueue()
        # priority queue of the events Events, each event is a duple (T,[ID,Data]) that describes the event that ocurred in the time T (in minutes) since the start:  
        # IDs:
        # 0 -> none
        # 1 -> a new ship arrives
        # 2 -> tugboat arrives to a destination
        # 3 -> a ship's load/unload process ends
        # Data: 
        # - if ID = 1. Data is ID,size (id and size of said ship)
        # - if ID = 3, Data is the ship 'id' 


    def compute_answer(self):
        sum = 0
        j = 0
        for i in self.wait_times:
            sum += i
            j += 1
        if j==0: self.answer = 0
        else: self.answer = sum/j


    def generate_ship_arrival_events(self):

        time_intervals = exponential_distr(self.lambda_ship_arrival,self.time_lapse)
        i = 1
        j = 0
        while (i < self.time_lapse - 1):
            size = choice(["small","medium", "large"], p = [self.small_prob, self.medium_prob, self.large_prob])
            self.Events.put((i,[1,j+1,size]))
            i += time_intervals[j]
            j += 1


    def check_out_ship_from_dock (self):

        dock = self.docks_queque.get()[1]
        self.dock_avaliability[dock] = 0
        self.st_docks_free = True
        ans = self.docked_ships[dock] 
        self.docked_ships[dock] = 0
        wait_time = self.current_time - self.docked_times[dock]
        self.wait_times.append(wait_time)
        self.docked_times[dock] = 0
        debug_log(self.current_time, "checked out ship with id = " + str(ans) + " from dock " + str (dock))  
        debug_log(self.current_time, "docks: " + str (self.docked_ships))
        if self.docks_queque.empty():
            self.st_load_finished = False    
        return ans         


    def check_in_ship_to_dock(self,id):

        self.st_docks_free = False
        mark = 0
        for i in range (0,self.dock_count):
            if self.dock_avaliability[i] == 0:
                self.dock_avaliability [i] = 1
                self.docked_ships[i] = id
                self.docked_times[i] = self.current_time
                debug_log(self.current_time, "checked in ship wit id = " + str(id) + " in dock " + str (i))     
                ship_type = self.ships_dict[id][0] 
                params = self.size_params[ship_type]
                load_time = normal_distr (params[1],params[0])
                debug_log(self.current_time, "wait time: " + str(load_time))
                debug_log(self.current_time, "docks: " + str (self.docked_ships))   
                index = self.current_time + load_time
                self.Events.put((index,[3,i]))
                mark = i
                break
        for i in range(mark,self.dock_count):
            if self.dock_avaliability[i] == 0:
                self.st_docks_free = True
                

    def next_event(self):

        event = self.Events.get()
        self.current_time = event[0]
        evt_type = event[1][0]

        if evt_type == 1:
            ship_id = event[1][1]
            ship_size = event[1][2]
            params = [ship_id, ship_size, self.current_time] 
            self.port_queque.put(params)
            self.st_ship_waiting = True
            debug_log(self.current_time, "the " + str(ship_size) + " ship with id = " + str (ship_id) + " arrives to port")
            #debug_log(self.current_time, "port queue: " + str(self.port_queque.queue))
                
        if evt_type == 2:
            if self.tugboat_state == 1:
                self.tugboat_arrived = True
                debug_log(self.current_time, "tugboat arrives to port")
            elif self.tugboat_state == 2:
                self.tugboat_arrived = True
                debug_log(self.current_time, "tugboat arrives to docks")

        if evt_type == 3:
            dock = event[1][1]
            self.st_load_finished = True
            self.dock_avaliability[dock] = 2
            id = self.docked_ships[dock]
            self.docks_queque.put((self.current_time,dock))
            debug_log(self.current_time, "ship " + str(id) + " finished loading/unloading")


    def tugboat_action(self):

        # Tugboat is bussy right now
        if self.tugboat_state != 0 and self.tugboat_state != 3 and self.tugboat_arrived == False: return

        #Tugboat is still waiting in port
        if self.tugboat_state == 3 and not self.st_ship_waiting: return

        # Tugboat arrived to port or is waiting in port and a ship arrives
        if ((self.tugboat_state == 1 and self.tugboat_arrived == True) or self.tugboat_state == 3):
            # arrived with scort
            if self.tugboat_scort != 0 and self.tugboat_state != 3:
                self.tugboat_state = 2
                del self.ships_dict[self.tugboat_scort]
                #with port empty and at least a dock bussy
                if self.st_ship_waiting == False and self.ships_dict:
                    self.tugboat_scort = 0
                    travel_time = exponential_distr(self.lambda_tugboat_alone)
                    debug_log(self.current_time,"traveling to docks alone for " + str(travel_time) + " hours")
                    index = self.current_time + travel_time
                    self.Events.put((index,[2]))  
                    self.tugboat_arrived = False
                    return        
                #with port and docks empty
                if self.st_ship_waiting == False and not self.ships_dict:
                    self.tugboat_scort = 0
                    self.tugboat_state = 3
                    debug_log(self.current_time, "nothing to do, tugboat is waiting in port")
                    return
            self.tugboat_state = 2
            new_ship = self.port_queque.get()
            id = new_ship [0]
            ship_type = new_ship [1]
            arrival_date = new_ship [2]
            self.ships_dict[id] = [ship_type,arrival_date]
            self.tugboat_scort = id
            travel_time = exponential_distr(self.lambda_tow_to_dock)
            debug_log(self.current_time, "traveling to docks scorting ship " + str(self.tugboat_scort) + " for " + str(travel_time) + " hours")
            index = self.current_time + travel_time
            self.Events.put((index,[2]))  
            self.tugboat_arrived = False
            if self.port_queque.empty():
                self.st_ship_waiting = False
            return

        # Tugboat arrives to docks
        if self.tugboat_state == 2 and self.tugboat_arrived:
            #while scorting a ship
            if self.tugboat_scort != 0:
                self.check_in_ship_to_dock(self.tugboat_scort) 
            self.tugboat_scort = 0
            self.tugboat_state = 0      

        # A dock is free, the tugboat is waiting in the docks and a ship is waiting his turn in the port
        if self.tugboat_state == 0 and self.st_ship_waiting and self.st_docks_free == True and self.st_load_finished == False:
            self.tugboat_state = 1
            travel_time = exponential_distr(self.lambda_tugboat_alone)
            debug_log(self.current_time,"traveling to port alone for " + str(travel_time) + " hours")
            index = self.current_time + travel_time
            self.Events.put((index,[2]))  
            self.tugboat_arrived = False

        # A ship ends loading/unloading and the tugboat is waiting in the docks
        elif self.tugboat_state == 0 and self.st_load_finished:
            self.tugboat_state = 1
            self.tugboat_scort = self.check_out_ship_from_dock()
            travel_time = exponential_distr(self.lambda_tow_to_port)
            debug_log(self.current_time, "traveling to port scorting ship " + str(self.tugboat_scort) + " for " + str(travel_time) + " hours")
            index = self.current_time + travel_time
            self.Events.put((index,[2]))  
            self.tugboat_arrived = False
        return


    def main_loop(self):
        
        self.current_time = 0
        debug_log(self.current_time, "RUNNIG SIMULATION FOR " + str(self.time_lapse) + " HOURS")
        
        while (not self.Events.empty()):
            self.next_event()
            self.tugboat_action() 
        debug_log(self.current_time, "SIMULATION FINISHED")
        debug_log(self.current_time, '')
        self.compute_answer()


    def build(self):

        self.current_time = 0     
        self.tugboat_state = 3  
        self.tugboat_scort = False  
        self.dock_avaliability = [0 for i in range (0,self.dock_count)]    
        self.docked_ships = [0 for i in range (0,self.dock_count)]    
        self.docked_times = [0 for i in range (0,self.dock_count)]   
        self.port_queque = Queue()
        self.docks_queque = PriorityQueue(maxsize=self.dock_count)
        self.Events = PriorityQueue()
        self.size_params ["small"] = self.small_ship
        self.size_params["medium"] = self.medium_ship
        self.size_params["large"] = self.large_ship


    def run (self, time = 10000):
        
        self.build()
        self.time_lapse = time
        self.generate_ship_arrival_events()
        self.main_loop()