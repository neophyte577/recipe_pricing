from warnings import simplefilter
simplefilter(action='ignore', category=Warning)
import numpy as np
import pandas as pd

# Classes

class ingr():
    
    def __init__(self, name, cost, unit):
        self.name = name
        self.cost = cost
        self.unit = unit
    
class recipe():
    
    def __init__(self, name, rec_df, makes_list):
        self.name = name
        self.qty_dict = qty_dict_constructor(rec_df)
        self.cost = rec_cost(self)
        self.makes = makes_list
        self.breakdown = [[k.name, self.qty_dict[k], ingr_dict[k.name].unit] for k in self.__dict__['qty_dict']]
        
class item():
    
    def __init__(self, name, qty, unit, rec):
        self.name = name
        self.qty = qty
        self.unit = unit
        self.recipe = rec
        self.cost = item_cost(self)
        self.price = round(item_price(self), 2)
        
    def specs(self):
        print('Name:' , self.name, '\nPortion:', self.qty, self.unit, '\nCost: $' + str(round(self.cost, 2)),
              '\nPrice: $' + str(self.price))


# Dictionaries

count_dict = {'ea':1, 'dozen':1/12, 'doz':1/12, 'dz':1/12, 'score':1/20, 'gross':1/144}

weight_dict = {'g':1, 'lb':1/453.592, 'lbm':1/453.592, 'lbs':1/453.592, 'oz':1/28.3495}

vol_dict = {'c':1, 'cup':1, 'ml':236.5882365, 'oz':8, 'floz':8, 'tbsp':16, 'tsp':48, 'gal':1/16, 'qt':1/4, 'pt':1/2}

dict_list = [count_dict, weight_dict, vol_dict]

ingr_list, ingr_dict = [], {}

rec_list, rec_dict = [], {}


# Functions

def rec_cost(recipe):
    
    rec_cost = 0
    
    for ingr in recipe.qty_dict:
        
        rec_cost += recipe.qty_dict[ingr] * ingr.cost
    
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

                    converted_unit = cost_converter(df['cost'][k], df['unit'][k], {v:k for (k,v) in d.items()}[1])[1]
        
                    ingr_dict[df['name'][k]] = ingr(df['name'][k], converted_cost, converted_unit) 
                
                else:
                    pass
                                  
        else:
            print(df['unit'][k])
            print('WRONG!')

    return ingr_dict


def recipe_converter(rec_df):
    
    df = rec_df.copy(deep=True)
    
    for k in range(df.shape[0]):
        
        if any(dfc['unit'][k] in d for d in dict_list):
            
            for d in dict_list:
                
                if dfc['unit'][k] in d:
                    
                    dfc['qty'][k], dfc['unit'][k] = unit_converter(dfc['qty'][k], dfc['unit'][k],
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

        
def item_cost(item):
    
    recipe_qty = unit_converter(item.recipe.makes[0], item.recipe.makes[1], item.unit)[0]

    item_cost = ( item.qty / recipe_qty ) * unit_converter(item.recipe.cost, 
                                                                     item.recipe.makes[1], item.unit)[0]
    
    return item_cost
    
    
def item_price(item, scale_factor=3):
    
    item_price = scale_factor * item.cost
    
    return item_price

