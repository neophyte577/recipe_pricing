from warnings import simplefilter
simplefilter(action='ignore', category=Warning)
import numpy as np
import pandas as pd
import funcy as fc

# Classes

class ingr():
    
    def __init__(self, name, unit_cost, unit, each_dict={}, **density):
        self.name = name
        self.unit = unit
        self.unit_cost = unit_cost
        self.each = each_converter(each_dict)
        
    def cost(self, qty=1, target_unit=None):
        if target_unit == None:
            ingr_cost = qty * self.unit_cost
        elif target_unit in fc.join(dict_list):
            ingr_cost = qty * cost_converter(self.unit_cost, self.unit, target_unit)
        else:
            print(target_unit)
            print('WRONG!')
        return ingr_cost
    
    def price(self, qty=1, target_unit=None, scale_factor=3):
        if target_unit == None:
            ingr_price = scale_factor * qty * self.unit_cost
        elif target_unit in fc.join(dict_list):
            ingr_price = scale_factor * qty * self.cost(target_unit)
        else:
            print(target_unit)
            print('WRONG!')
        return ingr_price
    
    
class recipe():
    
    def __init__(self, name, rec_df, makes_dict):
        self.name = name
        self.qty_dict = qty_dict_constructor(recipe_converter(rec_df))
        self.cost = rec_cost(self)
        self.makes = makes_dict
        self.breakdown = [{k.name:[self.qty_dict[k], ingr_dict[k.name].unit]} for k in self.__dict__['qty_dict']]

        
class item():
    
    def __init__(self, name, rec, sizes_list):
        self.name = name
        self.sizes = sizes_list
        self.recipe = rec
        
    def specs(self):
        print('Name:' , self.name, '\nPortion:', self.qty, self.unit, '\nCost: $' + str(round(self.cost, 2)),
              '\nPrice: $' + str(self.price))
        
    def cost(self, size='portion'):
        if size in (item_sizes and self.sizes):
            item_cost = self.recipe.cost / self.recipe.makes[size]
            return item_cost
        else:
            print(size)
            print('WRONG!')      
            
    def price(self, size='portion', scale_factor=3):
        if size in (item_sizes and self.sizes):
            item_price = round(scale_factor * self.cost(size), 2)
            return item_price
        else:
            print(size)
            print('WRONG!')


# Lists and Dictionaries

count_dict = {'ea':1, 'dozen':1/12, 'doz':1/12, 'dz':1/12, 'score':1/20, 'gross':1/144}

weight_dict = {'g':1, 'lb':1/453.592, 'lbm':1/453.592, 'lbs':1/453.592, 'oz':1/28.3495}

vol_dict = {'c':1, 'cup':1, 'L':0.2365882365, 'mL':236.5882365, 'floz':8, 'tbsp':16, 'tsp':48, 'gal':1/16, 
            'qt':1/4, 'pt':1/2}

dict_list = [count_dict, weight_dict, vol_dict]

item_sizes = ['portion', 'whole', 'full pan', 'half pan', 'quarter pan']

ingr_list, ingr_dict = [], {}

rec_list, rec_dict = [], {}


# Functions

def each_converter(each_dict):
    
    if each_dict == {}:
        
        each = {}
    
    elif any(list(each_dict.keys())[0] in d for d in dict_list):
        
        for d in dict_list:
            
            if list(each_dict.keys())[0] in d:
                
                each = { k : ( d[list(each_dict.keys())[0]] / d[k]  ) * list(each_dict.values())[0]  for (k,v) in d.items()}
                break
                
            else:
                pass  

    else:
        print(list(each_dict.keys())[0])
        print('WRONG!')
    
    return each


def rec_cost(recipe):
    
    rec_cost = 0
    
    for ingr in recipe.qty_dict:
        
        #print(ingr.name, ingr.cost, recipe.qty_dict[ingr], ingr.unit, recipe.qty_dict[ingr] * ingr.cost)
        
        rec_cost += recipe.qty_dict[ingr] * ingr.unit_cost
    
    return rec_cost


def unit_converter(qty, unit, target_unit):
    
    converted_qty = 0
    
    if any(unit and target_unit in d for d in dict_list): 
        
        for d in dict_list:
            
            if unit in d:
                converted_qty = ( d[target_unit] / d[unit] ) * qty
                break
            else:
                pass
        
    else:
        print(unit)
        print('WRONG!')
    
    return converted_qty, target_unit


def cost_converter(cost, per_unit, target_unit):
    
    converted_cost = 0
    
    if any(per_unit and target_unit in d for d in dict_list): 
        
        for d in dict_list:
            
            if per_unit in d:
                #print(d[per_unit], d[target_unit], cost)
                converted_cost = ( d[per_unit] / d[target_unit] ) * cost
                break
            else:
                pass
        
    else:
        print(per_unit)
        print('WRONG!')
    
    return converted_cost, target_unit


def ingr_dict_constructor(ingr_df):
    
    df = ingr_df.copy(deep=True)

    df['cost'] = df['cost'] / df['qty'] 

    df.drop('qty', axis='columns', inplace=True)

    ingr_dict = {}
    
    for k in range(df.shape[0]):

        if any(df['unit'][k] in d for d in dict_list):

            for d in dict_list:

                if df['unit'][k] in d:

                    converted_cost = cost_converter(df['cost'][k], df['unit'][k], {v:k for (k,v) in d.items()}[1])[0]

                    converted_unit = unit_converter(df['cost'][k], df['unit'][k], {v:k for (k,v) in d.items()}[1])[1]
        
                    ingr_dict[df['name'][k]] = ingr(df['name'][k], converted_cost, converted_unit) 
                    
                    break
                
                else:
                    pass
                                  
        else:
            print(df['unit'][k])
            print('WRONG!')

    return ingr_dict


def recipe_converter(rec_df):
    
    df = rec_df.copy(deep=True)
    
    for k in range(df.shape[0]):
        
        if any(df['unit'][k] in d for d in dict_list):
            
            for d in dict_list:
                
                if df['unit'][k] in d:
                    
                    df['qty'][k], df['unit'][k] = unit_converter(df['qty'][k], df['unit'][k],
                                                                    {v:k for k,v in d.items()}[1])  
                else:
                    pass
        
        else:
            print('WRONG!')
            
    return df


def qty_dict_constructor(rec_df):

    qty_dict = {}

    for k in range(rec_df.shape[0]):
        qty_dict[ingr_dict[rec_df['ingr'][k]]] = rec_df['qty'][k]
    
    return qty_dict

