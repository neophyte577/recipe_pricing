from warnings import simplefilter
simplefilter(action='ignore', category=Warning)
import numpy as np
import pandas as pd
import os


class ingr():
    
    def __init__(self, name, cost, unit):
        self.name = name
        self.cost = cost
        self.unit = unit
    
class recipe():
    
    def __init__(self, name, df, makes_list):
        self.name = name
        self.ingr_dict = rec_ingr_dict_constructor(df)
        self.cost = rec_cost(self)
        self.makes = makes_list
        self.breakdown = [(k.name, eval(k.name).cost, eval(k.name).unit) for k in self.__dict__['ingr_dict']]
        
class sale_item():
    
    def __init__(self, name, qty, unit, rec):
        self.name = name
        self.qty = qty
        self.unit = unit
        self.recipe = rec
        self.cost = sale_item_cost(self)
        self.price = round(sale_item_price(self), 2)
        
    def specs(self):
        print('Name:' , self.name, '\nPortion:', self.qty, self.unit, '\nCost: $' + str(round(self.cost, 2)),
              '\nPrice: $' + str(self.price))



count_dict = {'ea':1, 'dozen':1/12, 'score':1/20, 'gross':1/144}

weight_dict = {'g':1, 'lb':1/453.592, 'oz':1/28.3495}

vol_dict = {'c':1, 'ml':236.5882365, 'floz':8, 'tbsp':16, 'tsp':48, 'gal':1/16, 'qt':1/4, 'pt':1/2}

dict_list = [count_dict, weight_dict, vol_dict]


def rec_cost(recipe):
    
    rec_cost = 0
    
    for ingr in recipe.ingr_dict:
        
        rec_cost += recipe.ingr_dict[ingr] * ingr.cost
        
    #cost = round(cost, 2)
    
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
        print(unit)
        print('WRONG!')
    
    return converted_cost, target_unit


def ingr_list_constructor(df):
    
    ingr_list = []
    
    for k in range(df.shape[0]):
        
        ingr_list.append(ingr(df['name'], default_converter(df['cost'])[0], default_converter(df['cost'])[1]))
        

def recipe_converter(df):
    
    dfc = df.copy(deep=True)
    
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
            
    return dfc


def rec_ingr_dict_constructor(df):

    ingr_dict = {}

    for k in range(df.shape[0]):
        ingr_dict[eval(df['ingr'][k])] = df['qty'][k]
    
    return ingr_dict

        
def sale_item_cost(sale_item):
    
    recipe_qty = unit_converter(sale_item.recipe.makes[0], sale_item.recipe.makes[1], sale_item.unit)[0]

    sale_item_cost = ( sale_item.qty / recipe_qty ) * unit_converter(sale_item.recipe.cost, 
                                                                     sale_item.recipe.makes[1], sale_item.unit)[0]
    
    return sale_item_cost
    
    
def sale_item_price(sale_item, scale_factor=3):
    
    sale_item_price = scale_factor * sale_item.cost
    
    return sale_item_price
