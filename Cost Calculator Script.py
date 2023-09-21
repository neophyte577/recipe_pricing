from warnings import simplefilter
simplefilter(action='ignore', category=Warning)
import numpy as np
import pandas as pd
import funcy as fc
import os
import traceback


# Classes

class Ingr():
    
    def __init__(self, name, unit_cost, unit, density=np.pi, each_dict={}):
        self.name = name
        self.unit = unit
        self.unit_cost = unit_cost
        self.each = each_converter(each_dict)
        self.density = density
        
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
    
    
class Recipe():
    
    def __init__(self, name, rec_df, makes_dict):
        self.name = name
        self.qty_dict = self.qty_dict_constructor(self.recipe_converter(rec_df))
        self.cost = self.rec_cost()
        self.makes = makes_dict
        self.breakdown = pd.DataFrame.from_dict( fc.join([ {rec_df['ingr'][k]:[ [rec_df['qty'][k], rec_df['unit'][k]], 
                            self.qty_dict[ingr_dict[rec_df['ingr'][k]]] ]} 
                               for k in range(rec_df.shape[0]) ]), orient='index', columns=['given', 'converted'] )
    
    def recipe_converter(self, rec_df):

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

    def qty_dict_constructor(self, rec_df):

        qty_dict = {}

        for k in range(rec_df.shape[0]):

            ingredient = ingr_dict[rec_df['ingr'][k]]

            ingr_unit = ingredient.unit

            rec_unit = rec_df['unit'][k]

            if (rec_unit in weight_dict) and (ingr_unit in weight_dict):
                #print('1')
                qty_dict[ingredient] = [ rec_df['qty'][k], 'g' ]

            elif (rec_unit in vol_dict) and (ingr_unit in vol_dict):
                #print('2')
                qty_dict[ingredient] = [ rec_df['qty'][k], 'c' ]

            elif (rec_unit in vol_dict) and (ingr_unit in weight_dict) and (ingredient.density != np.pi):
                #print('3')
                qty_dict[ingredient] = [ ingredient.density * rec_df['qty'][k], 'g' ]

            elif (rec_unit in weight_dict) and (ingr_unit in vol_dict) and (ingredient.density != np.pi):
                #print('4')
                qty_dict[ingredient] = [ ( 1 / ingredient.density ) * rec_df['qty'][k], 'c' ]

            elif rec_unit in count_dict:
                #print('5')
                qty_dict[ingredient] = [ rec_df['qty'][k], 'ea' ]

            else:
                print('no diggity')

        return qty_dict

    def rec_cost(self):
    
        rec_cost = 0
        
        for ingr in self.qty_dict:
            
            rec_cost += self.qty_dict[ingr][0] * ingr.unit_cost
        
        return rec_cost
    

class Item():
    
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

vol_dict = {'c':1, 'cup':1, 'L':0.2365882365, 'ml':236.5882365, 'mL':236.5882365, 'floz':8, 'tbsp':16, 
            'tsp':48, 'gal':1/16, 'qt':1/4, 'pt':1/2}

dict_list = [count_dict, weight_dict, vol_dict]

item_sizes = ['portion', 'whole', 'full pan', 'half pan', 'quarter pan']

ingr_dict = {}

rec_dict = {}


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

                    converted_unit = unit_converter(df['cost'][k], df['unit'][k], {v:k for (k,v) in d.items()}[1])[1]
                    
                    if pd.isna(df['density'][k]):
                        ingr_dict[df['name'][k]] = Ingr(df['name'][k], converted_cost, converted_unit)
                    else:
                        ingr_dict[df['name'][k]] = Ingr(df['name'][k], converted_cost, converted_unit, df['density'][k])
                    
                    break
                
                else:
                    pass
                                  
        else:
            print(df['unit'][k])
            print('WRONG!')

    return ingr_dict


# Obtener ingredientes y recetas

try:
    ingredients_loc = 'C:/Users/Paul/Documents/City Chef/Ingredients'

    ingredients_directory = os.fsencode(ingredients_loc)

    ingr_dfs = []

    for file in os.listdir(ingredients_directory):
        filename = os.fsdecode(file)
        df = pd.read_csv(ingredients_loc + '/' + filename)
        ingr_dfs.append(df)
    
    ingr_df = pd.concat(ingr_dfs, ignore_index=True)

    ingr_dict = ingr_dict_constructor(ingr_df)

except Exception as error:
    print(error)
    print('No sweat, just rememeber to read the ingredients in manually')

try:
    recipes_loc = 'C:/Users/Paul/Documents/City Chef/Recipes'

    #recipes_loc = 'C:/Users/Paul/Documents/City Chef/Test Recipes'

    recipe_directory = os.fsencode(recipes_loc)

    recipe_dict = {}

    for file in os.listdir(recipe_directory):
        filename = os.fsdecode(file)
        rec_df = pd.read_csv(recipes_loc + '/' + filename)
        makes_dict = {}
        for k in range(rec_df[rec_df[['makes', 'size']].notnull().all(1)][['makes', 'size']].shape[0]):
            #print(rec_df['size'][k])
            makes_dict[rec_df['size'][k]] = rec_df['makes'][k]
        rec_df.drop(['makes', 'size'], axis='columns', inplace=True)
        #print(rec_df.head())
        recipe_dict[filename.replace('.csv','')] = Recipe(filename, rec_df, makes_dict)

except Exception as error:
    print(error)
    print(traceback.format_exc())


print(recipe_dict['salmon'].breakdown)
print(Item('salmon', recipe_dict['salmon'], ['portion']).price('portion'))

'''
print(recipe_dict['jerk chicken'].breakdown)
print(Item('jerk chicken', recipe_dict['jerk chicken'], ['portion']).price('portion'))
'''

'''
print(ingr_dict['test_ingr_2'].unit)
print(ingr_dict['test_ingr_2'].density)
print(recipe_dict['test recipe 1'].breakdown)
print(recipe_dict['test recipe 1'].qty_dict)
print(recipe_dict['test recipe 1'].cost)
print(Item('test item 1', recipe_dict['test recipe 1'], ['portion']).price())
'''


