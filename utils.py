import numpy as np
from itertools import combinations


class Classic_Grid:
    def __init__(self, list_input, dims = 9):
        self.dims = dims
    
        self.containers = {}
        self.containers["rows"] = [Classic_Container(self) for i in range(self.dims)]
        self.containers["cols"] = [Classic_Container(self) for i in range(self.dims)]
        self.containers["subgrids"] = [Classic_Container(self) for i in range(self.dims)]
        
        self.entries = [[Classic_Entry(list_input[i][j], i, j, self) for j in range(self.dims)] for i in range(self.dims)]
        
        self.update_entries()
        self.update_containers()
        
        
        
    def check_entries_and_possible_vals(self):
        for e_lst in self.entries:
            for entry in e_lst:
                if entry.get_solved():
                    assert entry.get_val != 0, "Solved Entry has a zero value"
                    assert len(entry.get_possible_vals) == 0, "Solved Entry has a nonempty possible vals set"
                    assert entry.row.get_solved_vals()[entry.get_val()] is entry
                    assert entry.col.get_solved_vals()[entry.get_val()] is entry
                    assert entry.subgrid.get_solved_vals()[entry.get_val()] is entry
                    
                        
                    
                else:
                    assert entry.get_val == 0, "Unsolved Entry has a nonzero value"
                    assert len(entry.get_possible_vals) > 0, "Unsolved Entry has an empty possible vals set"
                    
    
    def update_entries(self):
        for e_lst in self.get_entries():
            for entry in e_lst:
                entry.update_possible_vals()
    
    def update_containers(self):
        for container_lst in self.get_containers().values():
            for c in container_lst:
                c.update_possible_entries()
    
    def get_entries(self):
        return self.entries

    def get_containers(self):
        return self.containers
    
    def get_all_containers(self):
        return self.containers['rows'] + self.containers['cols'] + self.containers['subgrids']
    
        
    def visualize(self):
        for lst in self.entries:
            print([entry.get_val() if entry.get_solved() else 0 for entry in lst])
        print()




class Classic_Container:
    def __init__(self, grid):
        self.grid = grid
        self.entries = [] # Add entries as they are created
        
        # if value i is solved then solved_vals[i - 1] should point to the entry that has value i
        self.solved_vals = [None] * grid.dims
        self.possible_entries = [set([]) for i in range(grid.dims)]
    
    def update_possible_entries(self): # iterate through all contained entries, update possible entries as necessary
        for entry in self.entries:
            if entry.get_solved():
                self.solved_vals[entry.get_val() - 1] = entry
                self.possible_entries[entry.get_val() - 1] = set([])
            else:
                for val in entry.get_possible_vals():
                    self.possible_entries[val - 1].add(entry)
                    
    def solve_entry(self, solved_val, entry):
        self.solved_vals[solved_val - 1] = entry

        for possbile_val in self.possible_entries:
            if entry in possbile_val:
                possbile_val.remove(entry)
            #self.possible_entries[val - 1].discard(entry)
        
        for entry in self.entries:
            entry.remove_possible_val(solved_val)

    def remove_possible_entry(self, entry, val):
        if entry in self.possible_entries[val - 1]:
            self.possible_entries[val - 1].remove(entry)
        #self.possible_entries[val - 1].discard(entry)
    
    def subgrid_lock(self, lock_entries, val):
        for entry in self.entries:
            if entry.get_solved() or entry in lock_entries:
                continue
            entry.remove_possible_val(val)
        
        
    
    def get_entries(self):
        return self.entries
    
    def get_unsolved_entries(self):
        return [entry for entry in self.entries if not entry.get_solved()]
    
    def get_solved_vals(self):
        return self.solved_vals
    
    def get_possible_entries(self):
        return self.possible_entries
    
    def add_entry(self, entry):
        self.entries.append(entry)




class Classic_Entry:
    def __init__(self, val, row, col, grid : Classic_Grid):
       self.grid = grid
       
       self.position = (row, col, 3 * (row // 3) + col // 3)
       self.row = self.grid.get_containers()["rows"][self.position[0]]
       self.col = self.grid.get_containers()["cols"][self.position[1]]
       self.subgrid = self.grid.get_containers()["subgrids"][self.position[2]]
       
       self.row.add_entry(self)
       self.col.add_entry(self)
       self.subgrid.add_entry(self)
       
       self.val = val
       self.solved = bool(val)
       
       possible_vals = set([]) # Will update this after the grid has been initialized!
       
       
    def update_possible_vals(self): # iterate through all entries in shared containers and update possible vals as necessary
        if self.solved:
            return
        
        solved_vals = set([])
        for entry in self.row.get_entries():
            if entry.get_solved():
                solved_vals.add(entry.get_val())
        for entry in self.col.get_entries():
            if entry.get_solved():
                solved_vals.add(entry.get_val())
        for entry in self.subgrid.get_entries():
            if entry.get_solved():
                solved_vals.add(entry.get_val())
        
        self.possible_vals = set([i for i in range(1, self.grid.dims + 1) if i not in solved_vals])
    
    
    def solve(self, value):
        self.solved = True
        self.val = value
        
        self.row.solve_entry(value, self)
        self.col.solve_entry(value, self)
        self.subgrid.solve_entry(value, self)
        
        self.possible_vals = set([])

    def remove_possible_val(self, bad_val):
        if self.solved:
            return
        if bad_val in self.possible_vals:
            self.possible_vals.remove(bad_val)
        #self.possible_vals.discard(solved_val)
        self.row.remove_possible_entry(self, bad_val)
        self.col.remove_possible_entry(self, bad_val)
        self.subgrid.remove_possible_entry(self, bad_val)
        
        
    def get_possible_vals(self):
        return self.possible_vals
    def get_position(self):
        return self.position
    def get_solved(self):
        return self.solved
    
    def get_val(self):
        return self.val
        
    def get_containers(self):
        return [self.row, self.col, self.subgrid]
    
    


class Solver:
    def __init__(self, grid):
        self.grid = grid
    
    def solve(self):
        updated = True
        while updated:
            updated = self.single_possible_val() or self.single_possible_entry() or self.subgrid_lock()
    
    def single_possible_val(self):
        updated = False
        for entry_lst in self.grid.get_entries():
            for entry in entry_lst:
                if (not entry.get_solved()) and len(entry.get_possible_vals()) == 1:
                    val = entry.get_possible_vals().pop()
                    entry.solve(val)
                    updated = True
        return updated
    
    def single_possible_entry(self):
        updated = False
        for container in self.grid.get_all_containers():
            for i, entries in enumerate(container.get_possible_entries()):
                if len(entries) == 1:
                    entry = entries.pop()
                    entry.solve(i + 1)
                    updated = True
        return updated
    
    def subgrid_lock(self):
        updated = False
        
        for linear_container in self.grid.get_containers()["rows"] + self.grid.get_containers()["cols"]:
            for i, possible_entries in enumerate(linear_container.get_possible_entries()):
                lst = list(possible_entries)
                if len(lst) == 2 and lst[0].get_position()[2] == lst[1].get_position()[2]:
                    lst[0].subgrid.subgrid_lock(possible_entries, i + 1)
                    updated = True
                elif (len(lst) == 3 
                      and lst[0].get_position()[2] == lst[1].get_position()[2] 
                      and lst[1].get_position()[2] == lst[2].get_position()[2]):
                    lst[0].subgrid.subgrid_lock(possible_entries, i + 1)
                    updated = True
        return updated
                    
