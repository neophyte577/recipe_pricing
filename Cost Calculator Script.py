from warnings import simplefilter
simplefilter(action='ignore', category=Warning)
import numpy as np
import pandas as pd
import os


class ingr():
    
    def __init__(self, name, unit_cost, unit):
        self.name = name
        self.unit_cost = unit_cost
        self.unit = unit
    
class recipe():
    
    def __init__(self, name, ingr_dict, makes_list):
        self.name = name
        self.ingr_dict = ingr_dict
        self.cost = cost(self)
        self.makes = makes_list
        
class sale_item():
    
    def __init__(self, name, qty, unit, rec):
        self.name = name
        self.qty = qty
        self.unit = unit
        self.recipe = rec
        self.cost = sale_item_cost(self)
        self.price = sale_item_price(self)



count_dict = {'ea':1, 'dozen':12, 'score':20, 'gross':144}

weight_dict = {'g':1, 'lb':453.592, 'oz':28.3495}

vol_dict = {'c':1, 'ml':1/236.5882365, 'floz':1/8, 'tbsp':1/16, 'tsp':1/48, 'gal':16, 'qt':4, 'pt':2}

dict_list = [count_dict, weight_dict, vol_dict]


def cost(recipe):
    
    cost = 0
    
    for ingr in recipe.ingr_dict:
        
        cost += recipe.ingr_dict[ingr] * ingr.unit_cost
        
    cost = round(cost, 2)
    
    return cost


def default_converter(qty, unit):
    
    converted_qty, converted_unit = 0, 0
    
    if any(unit in d for d in dict_list): 
        
        for d in dict_list:
            
            if unit in d:
                converted_qty = qty * d[unit] 
                converted_unit = {v:k for k,v in d.items()}[1]
                break
            else:
                pass
        
    else:
        print(unit)
        print('WRONG!')
    
    return converted_qty, converted_unit


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


def ingr_list_constructor(df):
    
    ingr_list = []
    
    for k in range(df.shape[0]):
        
        ingr_list.append(ingr(df['name'], default_converter(df['unit_cost'])[0], default_converter(df['unit_cost'])[1]))
        

def recipe_converter(df):
    
    dfc = df.copy(deep=True)
    
    for k in range(df.shape[0]):
        
        dfc['qty'][k], dfc['unit'][k] = default_converter(df['qty'][k], df['unit'][k])
            
    return dfc


def recipe_constructor(name, df, makes_list):

    ingr_dict = {}

    for k in range(df['ingr'].shape[0]):
        ingr_dict[eval(df['ingr'][k])] = df['qty'][k]

    rec = recipe(name, ingr_dict, makes_list)
    
    return rec
        
def sale_item_cost(sale_item):
    
    recipe_qty = unit_converter(sale_item.recipe.makes[0], sale_item.recipe.makes[1], sale_item.unit)[0]

    sale_item_cost = ( sale_item.qty / recipe_qty ) * unit_converter(sale_item.recipe.cost, 
                                                                     sale_item.recipe.makes[1], sale_item.unit)[0]
    
    return sale_item_cost
    
    
def sale_item_price(sale_item, scale_factor=3):
    
    sale_item_price = scale_factor * sale_item.cost
    
    return sale_item_price