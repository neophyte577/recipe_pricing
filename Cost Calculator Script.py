from warnings import simplefilter
simplefilter(action='ignore', category=Warning)
import numpy as np
import pandas as pd
import funcy as fc
import os

import traceback
from time import time


# Classes

class Ingredient():
    
    def __init__(self, name, unit_cost, unit, density=np.pi, each_list=[]):
        self.name = name
        self.unit = unit
        self.unit_cost = unit_cost
        self.density = density
        self.each_list = each_list
        self.each = self.each_converter(each_list) 
        
        
    def cost(self, qty=1, target_unit=None):

        if target_unit == None:
            ingr_cost = qty * self.unit_cost
        elif target_unit in fc.join(dict_list):
            if any((u in d for u in [target_unit, self.unit]) for d in dict_list):
                ingr_cost = qty * cost_converter(self.unit_cost, self.unit, target_unit)
            elif (target_unit in weight_dict) and (self.unit in vol_dict):
                ingr_cost = qty * cost_converter( (1 / self.density) * self.unit_cost, 'g', target_unit)
            elif (target_unit in vol_dict) and (self.unit in weight_dict):
                ingr_cost = qty * cost_converter( self.density * self.unit_cost, 'c', target_unit)
            elif ((target_unit in count_dict) and (self.unit not in count_dict)) or ((target_unit not in count_dict) and (self.unit in count_dict)):
                print('WRONG!!! Cannot convert between volume/weight and count!')
            else:
                print('watt')
        else:
            print(target_unit)
            print('WRONG! ingr cost')

        return ingr_cost, target_unit
    
    
    def price(self, qty=1, target_unit=None, scale_factor=3):

        if target_unit == None:
            ingr_price = scale_factor * qty * self.unit_cost
        elif target_unit in fc.join(dict_list):
            ingr_price = scale_factor * qty * self.cost(target_unit)
        else:
            print(target_unit)
            print('WRONG! ingr price')

        return ingr_price
  

    def each_converter(self, each_list):
    
        if each_list == []:
            each = {}
        elif any(each_list[1] in d for d in dict_list):
            for d in dict_list:
                if each_list[1] in d:
                    each = { k : ( d[k] / d[each_list[1]]  ) * each_list[0] for (k,v) in d.items() }
                    break
                else:
                    pass
        else:
            print(each_list[1])
            print('WRONG! ingr each_converter')

        return each
    
    
    def each_cost(self, each_unit=None):

        if each_unit == None:
            each_unit = self.each_list[1]
        
        if self.each != {}:
            if self.each_list[1] not in count_dict:
                each_cost = self.each_list[0] * cost_converter(self.unit_cost, self.unit, self.each_list[1])
                return each_cost, self.each_list[0] * (1 / self.each[each_unit]) * self.each_list[0], each_unit
            else:
                print('ALREADY EACH!!!')
        else:
            print('WRONG! each_cost')

    
class Recipe():
    
    def __init__(self, name, rec_df):
        self.name = name
        self.qty_dict = self.qty_dict_constructor(self.recipe_converter(rec_df))
        self.cost = self.rec_cost()
        self.breakdown = pd.DataFrame.from_dict( fc.join([ {rec_df['ingr'][k]:[ [rec_df['qty'][k], rec_df['unit'][k]], 
                            self.qty_dict[ingr_dict[rec_df['ingr'][k]]] ]} 
                               for k in range(rec_df.shape[0]) ]), orient='index', columns=['given', 'converted'] ).rename_axis(name.upper())
        self.makes = {}

        makes_df = rec_df[rec_df[['makes','size']].notnull().all(axis='columns')][['makes','size']]

        for row in makes_df.itertuples(index=False):
            if (row[1] in size_list) or (row[1] in fc.join(dict_list)):
                self.makes.update({row[1]:row[0]})


    def recipe_converter(self, rec_df):

        df = rec_df.copy(deep=True)

        for j, ingr_unit in rec_df['unit'].items():
            if ingr_unit in fc.join(dict_list):
                for d in dict_list:
                    if ingr_unit in d:
                        base_unit = {v:k for k,v in d.items()}[1]
                        df['qty'][j] = unit_converter(rec_df['qty'][j], ingr_unit, base_unit) 
                        df['unit'][j] = base_unit
                        break
                    else:
                        pass
            else:
                print(ingr_unit)
                print('WRONG! invalid unit for recipe conversion')
                
        return df


    def qty_dict_constructor(self, rec_df):

        qty_dict = {}

        for k, row in enumerate(rec_df.itertuples(index=False)):

            ingredient = ingr_dict[rec_df['ingr'][k]]
            ingr_unit = ingredient.unit
            rec_unit = rec_df['unit'][k]

            if (rec_unit in weight_dict) and (ingr_unit in weight_dict):
                qty_dict[ingredient] = [ rec_df['qty'][k], 'g' ]
            elif (rec_unit in vol_dict) and (ingr_unit in vol_dict):
                qty_dict[ingredient] = [ rec_df['qty'][k], 'c' ]
            elif (rec_unit in vol_dict) and (ingr_unit in weight_dict) and (ingredient.density != np.pi):
                qty_dict[ingredient] = [ ingredient.density * rec_df['qty'][k], 'g' ]
            elif (rec_unit in weight_dict) and (ingr_unit in vol_dict) and (ingredient.density != np.pi):
                qty_dict[ingredient] = [ ( 1 / ingredient.density ) * rec_df['qty'][k], 'c' ]
            elif (rec_unit in count_dict) and (ingr_unit in count_dict):
                qty_dict[ingredient] = [ rec_df['qty'][k], 'ea' ]
            elif (rec_unit in count_dict) and (ingr_unit in vol_dict):
                if ingredient.each != {}:
                    qty_dict[ingredient] = [ ingredient.each['c'] * rec_df['qty'][k] , 'c' ]
                else:
                    print('NO EACH!!!1 in', ingredient.name, 'no volume unit in each')
            elif (rec_unit in count_dict) and (ingr_unit in weight_dict):
                if ingredient.each != {}:
                    qty_dict[ingredient] = [ ingredient.each['g'] * rec_df['qty'][k] , 'g' ]
                else:
                    print('NO EACH!!!1 in', ingredient.name, 'no weight unit in each')
            else:
                print('DENSITY ERROR IN', self.name, ':', ingredient.name)

        return qty_dict
    

    def rec_cost(self):
    
        rec_cost = 0
        
        for ingr in self.qty_dict:
            rec_cost += self.qty_dict[ingr][0] * ingr.unit_cost
        
        return rec_cost
    

    def to_ingr(self, density=np.pi, each_list=[]):

        if any(s in fc.join(dict_list) for s in list(self.makes.keys())):
            for s in list(self.makes.keys()):
                if s in weight_dict:
                    yield_unit = s
                    ingr_unit = 'g'
                    converted_yield = unit_converter(self.makes[s], yield_unit, ingr_unit)
                    unit_cost = (1 / converted_yield) * cost_converter(self.cost, yield_unit, ingr_unit)
                    break
                elif s in vol_dict:
                    yield_unit = s
                    ingr_unit = 'c'
                    converted_yield = unit_converter(self.makes[s], yield_unit, ingr_unit)
                    unit_cost = (1 / converted_yield) * cost_converter(self.cost, yield_unit, ingr_unit)
                    break
                elif s in count_dict:
                    yield_unit = s
                    ingr_unit = 'ea'
                    converted_yield = unit_converter(self.makes[s], yield_unit, ingr_unit)
                    unit_cost = (1 / converted_yield) * cost_converter(self.cost, yield_unit, ingr_unit)
                else:
                    pass
            ingr_dict.update({self.name : Ingredient(self.name, unit_cost, ingr_unit, density, each_list)})

        else:
            print('WRONG! cannot to_ingr without volume, weight, or count yield')


class Item():
    
    def __init__(self, name, recipe, additional_sizes=[]):
        self.name = name
        self.sizes = list(recipe.makes.keys()) + additional_sizes
        self.recipe = recipe
        
    def specs(self):
        print('Name:' , self.name, '\nPortion:', self.qty, self.unit, '\nCost: $' + str(round(self.cost, 2)),
              '\nPrice: $' + str(self.price))
       
    def cost(self, size='portion'):
        if size in self.sizes:
            item_cost = self.recipe.cost / self.recipe.makes[size]
            return item_cost
        elif size in size_dict:
            if any(k in size_dict for k in self.recipe.makes):
                makes_dict = {k:self.recipe.makes[k] for k in [sz for sz in self.recipe.makes if sz in size_dict]}
                makes_sz = list(makes_dict.keys())[0]
                makes_qty = makes_dict[makes_sz]
                converted_makes_qty = unit_converter(makes_qty, makes_sz, size)
                item_cost = self.recipe.cost / converted_makes_qty
                return item_cost
            else:
                print(size)
                print('WRONG! no serving size in recipe')
        elif size in vol_dict:
            if any(k in vol_dict for k in self.recipe.makes):
                yield_dict = {k:self.recipe.makes[k] for k in [unit for unit in self.recipe.makes if unit in vol_dict]}
                yield_unit = list(yield_dict.keys())[0]
                yield_qty = yield_dict[yield_unit]
                converted_yield_qty = unit_converter(yield_qty, yield_unit, size)
                item_cost = self.recipe.cost / converted_yield_qty
                return item_cost
            else:
                print(size)
                print('WRONG! no volumetric yield in recipe')
        elif size in weight_dict:
            if any(k in weight_dict for k in self.recipe.makes):
                yield_dict = {k:self.recipe.makes[k] for k in [unit for unit in self.recipe.makes if unit in weight_dict]}
                yield_unit = list(yield_dict.keys())[0]
                yield_qty = yield_dict[yield_unit]
                converted_yield_qty = unit_converter(yield_qty, yield_unit, size)
                item_cost = self.recipe.cost / converted_yield_qty
                return item_cost
            else:
                print(size)
                print('WRONG! no mass yield in recipe')        
        else:
            print(size)
            print('WRONG! invalid size for item cost computation')     


    def price(self, size='portion', scale_factor=3):
        try:
            item_price = round(scale_factor * self.cost(size), 2)
            return item_price
        except Exception as error:
            print('Error in', self.name + '.price():', error)


# Lists and Dictionaries (Global)

count_dict = {'ea':1, 'each':1, 'dozen':1/12, 'doz':1/12, 'dz':1/12, 'score':1/20, 'gross':1/144}

weight_dict = {'g':1, 'kg':0.001, 'lb':1/453.592, 'lbm':1/453.592, 'lbs':1/453.592, 'oz':1/28.3495}

vol_dict = {'c':1, 'cup':1, 'L':0.2365882365, 'ml':236.5882365, 'mL':236.5882365, 'floz':8, 'tbsp':16, 'tsp':48, 
            'dash':384, 'gal':1/16, 'ga':1/16, 'gallon':1/16, 'bushel':1/128, 'qt':1/4, 'quart':1/4, 'pt':1/2, 'pint':1/2}

size_dict = {'portion':1, 'quarter pan':1/7.5, 'half pan':1/15, 'full pan':1/30}

parts_dict = {'whole':1, 'half':2, 'quarter':4}

size_list = list(size_dict.keys()) + list(parts_dict.keys())

size_to_vol_dict = {}

vol_dict.update(size_to_vol_dict)

dict_list = [count_dict, weight_dict, vol_dict]

big_dict_list = dict_list + [size_dict]

ingr_dict, rec_dict, item_dict = {}, {}, {}


# Functions

def unit_converter(qty, given_unit, target_unit):
    
    if any(given_unit and target_unit in d for d in big_dict_list): 
        
        for d in big_dict_list:
            
            if given_unit in d:
                converted_qty = ( d[target_unit] / d[given_unit] ) * qty
                return converted_qty
            else:
                pass 

    else:
        print(given_unit)
        print('WRONG! invalid unit for conversion')


def cost_converter(cost, per_unit, target_unit):
    
    if any(per_unit and target_unit in d for d in dict_list): 
        
        for d in dict_list:
            if per_unit in d:
                converted_cost = ( d[per_unit] / d[target_unit] ) * cost
                return converted_cost
            else:
                pass
        
    else:
        print(per_unit)
        print('WRONG! invalid unit for cost conversion')


def ingr_df_cleaner(ingr_df):

    df = ingr_df.copy(deep=True)

    df.dropna(axis='index', how='any', subset=['name', 'qty', 'cost', 'unit'])

    #df = df[df[['qty','cost']].apply(pd.to_numeric, errors='coerce').notnull()].dropna(subset=['qty','cost'], how='any')

    #print(df[df[['qty','cost']].apply(pd.to_numeric, errors='coerce').notnull()].dropna(subset=['qty','cost'], how='any'))

    df = df[pd.to_numeric(df['qty'], errors='coerce').notnull()]

    df = df[pd.to_numeric(df['cost'], errors='coerce').notnull()]

    df[['qty','cost']] = df[['qty','cost']].astype(float)

    df[['name', 'unit']] = df[['name', 'unit']].astype(str)

    df.drop(df[(df['qty'] <= 0) | (df['cost'] < 0) | (df['density'] <= 0 | (df['each_qty'] <= 0))].index, inplace=True)

    return df


def ingr_dict_constructor(ingr_df):
    
    df = ingr_df.copy(deep=True)

    df['cost'] = df['cost'] / df['qty'] 

    df.drop('qty', axis='columns', inplace=True)

    ingr_dict = {}
    
    for j, given_unit in df['unit'].items():

        if given_unit in fc.join(dict_list):

            for d in dict_list:

                if given_unit in d:

                    base_unit = {v:k for (k,v) in d.items()}[1]

                    converted_cost = cost_converter(df['cost'][j], given_unit, base_unit)
                    
                    if pd.isna(df['each_qty'][j]) and pd.isna(df['each_unit'][j]):
                        each_list = []
                    else:
                        each_list = [df['each_qty'][j], df['each_unit'][j]]
            
                    if pd.isna(df['density'][j]):
                        ingr_dict[df['name'][j]] = Ingredient(df['name'][j], converted_cost, base_unit, np.pi, each_list)
                    else:
                        ingr_dict[df['name'][j]] = Ingredient(df['name'][j], converted_cost, base_unit, df['density'][j], each_list)
                    
                    break

                else:
                    pass
                                  
        else:
            print('WRONG!', df['name'][j], 'not added to ingredient dictionary')
            print()
    
    return ingr_dict


def get_recipes(recipes_loc):

    recipe_directory = os.fsencode(recipes_loc)

    rec_df_dict = {}

    for file in os.listdir(recipe_directory):

        filename = os.fsdecode(file)
        
        try:
            rec_df = pd.read_csv(recipes_loc + '/' + filename)

        except Exception as error:
            print(error, 'in', filename)
            print(filename.partition('.')[0], 'recipe not added to recipe dictionary')
            continue

        name = filename.replace('.csv','')

        rec_df_dict.update({name : rec_df})

    return rec_df_dict

    
def rec_dict_constructor(rec_df_dict):

    rec_dict_main = {}

    for name, rec_df in rec_df_dict.items():

        if rec_df['ingr'].isin(list(ingr_dict.keys())).all():

            try:
                rec_dict_main[name] = Recipe(name.lower(), rec_df)
                if any(s in fc.join(dict_list) for s in list(rec_dict_main[name].makes.keys())):
                    rec_dict_main[name].to_ingr()

            except Exception as error:
                print('WRONG!', error, name, 'recipe not added to recipe dictionary')
                continue

        else:
            ingr_errors = list(rec_df[~rec_df['ingr'].isin(list(ingr_dict.keys()))]['ingr'])
            print('WRONG! Ingredient Error in ' + name + ':', ingr_errors)
            print()
            print(name, 'recipe not added to recipe dictionary')

    return rec_dict_main


def item_dict_constructor(rec_dict):

    item_dict = {}

    for recipe_name in rec_dict:

        item_dict.update({ recipe_name : Item(recipe_name, rec_dict[recipe_name]) })
    
    return item_dict


def output_template(name, size, scale_factor=3):

    print()
    print(rec_dict[name].breakdown)
    print()
    print('Recipe cost:', rec_dict[name].cost)
    print()
    print('Item cost per', size + ':', item_dict[name].cost(size))
    print()
    print('Item price per', size, 'with scale factor of', str(scale_factor) + ':', item_dict[name].price(size, scale_factor))
    print()
    print('---------------------')
    print()


def main():

    try:
        
        ingredients_loc = 'C:/Users/Paul/Documents/City Chef/Ingredients'

        ingredients_directory = os.fsencode(ingredients_loc)

        ingr_dfs = []

        for file in os.listdir(ingredients_directory):
            filename = os.fsdecode(file)
            print(ingredients_loc + '/' + filename)
            df = pd.read_csv(ingredients_loc + '/' + filename)
            ingr_dfs.append(df)
        
        ingr_df = pd.concat(ingr_dfs, ignore_index=True)

        cleaned_ingr_df = ingr_df_cleaner(ingr_df)
        
        ingr_dict.update(ingr_dict_constructor(cleaned_ingr_df))

    except Exception as error:
        print(error)
        print('NO INGREDIENTS!!!1')

    try:

        recipes_loc = 'C:/Users/Paul/Documents/City Chef/Ingredient Recipes'

        rec_df_dict = get_recipes(recipes_loc)

        rec_dict_main = rec_dict_constructor(rec_df_dict)
            
        rec_dict.update(rec_dict_main)

    except Exception as error:
        print(error)
        print(traceback.format_exc())
        print('NO INGREDIENT RECIPES!!!1')

    try:

        recipes_loc = 'C:/Users/Paul/Documents/City Chef/Recipes'

        rec_df_dict = get_recipes(recipes_loc)

        rec_dict_main = rec_dict_constructor(rec_df_dict)
            
        rec_dict.update(rec_dict_main)

    except Exception as error:
        print(error)
        print(traceback.format_exc())
        print('NO RECIPES!!!1')

    #######################################################
    try:
        item_dict.update(item_dict_constructor(rec_dict))
    except Exception as error:
        print(error)
        print(traceback.format_exc())
        print('NO ITEMS!!!1')
    #######################################################

    output_template('crab bisque', 'portion', 2.5)
        

        

#TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT
def test():

    try:
        
        ingredients_loc = 'C:/Users/Paul/Documents/City Chef/Test Ingredients'

        ingredients_directory = os.fsencode(ingredients_loc)

        ingr_dfs = []

        for file in os.listdir(ingredients_directory):
            filename = os.fsdecode(file)
            print(ingredients_loc + '/' + filename)
            df = pd.read_csv(ingredients_loc + '/' + filename)
            ingr_dfs.append(df)
        
        ingr_df = pd.concat(ingr_dfs, ignore_index=True)

        cleaned_ingr_df = ingr_df_cleaner(ingr_df)
        
        ingr_dict.update(ingr_dict_constructor(cleaned_ingr_df))

    except Exception as error:
        print(error)
        print('NO INGREDIENTS!!!1')

    try:

        recipes_loc = 'C:/Users/Paul/Documents/City Chef/Test Recipes'

        rec_df_dict = get_recipes(recipes_loc)

        rec_dict_main = rec_dict_constructor(rec_df_dict)
            
        rec_dict.update(rec_dict_main)

    except Exception as error:
        print(error)
        print(traceback.format_exc())
        print('NO RECIPES!!!1')

    #################################################
    item_dict.update(item_dict_constructor(rec_dict))
    #################################################

    print(ingr_dict['test_ingr_2'].unit)
    print(ingr_dict['test_ingr_2'].density)
    print(rec_dict['test recipe 1'].breakdown)
    print(rec_dict['test recipe 1'].cost)
    print(item_dict['test recipe 1'].price('portion'))
#TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT


start = time()

if __name__ == '__main__':
    main()

end = time()

print('Execution time:', end - start)
print()


'''
print(rec_dict['shrimp etouffee'].breakdown)
print()
print(rec_dict['shrimp etouffee'].cost)
print()
print(item_dict['shrimp etouffee'].price('portion'))
print(item_dict['shrimp etouffee'].price('full pan'))
print()
print(rec_dict['zobo'].breakdown)
print()
print(16 * item_dict['zobo'].cost('floz'))
print()
print(item_dict['zobo'].price('gal'))
print()
'''

'''
print(rec_dict['crab cake'].breakdown)
print(rec_dict['crab cake'].cost)
print()
print(item_dict['crab cake'].cost('portion'))
print(item_dict['crab cake'].price('portion'))
'''

'''
print(rec_dict['jerk turkey'].breakdown)
print(rec_dict['jerk turkey'].cost)
print(rec_dict['jerk turkey'].makes)
print(item_dict['jerk turkey'].cost('whole'))
print(item_dict['jerk turkey'].price('whole'))
print()
print(rec_dict['cabbage'].breakdown)
print()
print(item_dict['cabbage'].price('portion'))
print()
print(rec_dict['fried turkey'].breakdown)
print(item_dict['fried turkey'].cost('whole'))
print(item_dict['fried turkey'].price('whole'))
print()
'''

'''
print()
print(ingr_dict['beef frank'].unit_cost)
print(ingr_dict['hot dog roll'].unit_cost)
print(ingr_dict['beef frank'].each)
print(rec_dict['hot dog'].breakdown)
print(item_dict['hot dog'].cost('portion'))
print(item_dict['hot dog'].price('portion', scale_factor=2.5))
print(item_dict['hot dog'].price('portion', scale_factor=2.5))
print()
print(ingr_dict['hot beef sausage'].unit_cost)
print(ingr_dict['hot dog roll'].unit_cost)
print(ingr_dict['hot beef sausage'].each)
print(rec_dict['half smoke'].breakdown)
print(item_dict['half smoke'].cost('portion'))
print(item_dict['half smoke'].price('portion', scale_factor=2))
print(item_dict['half smoke'].price('portion', scale_factor=2)*150)
print()
print(ingr_dict['slider patty'].unit_cost)
print(ingr_dict['cheese slice, american'].unit_cost)
print(ingr_dict['slider bun'].unit_cost)
print(ingr_dict['slider patty'].each)
print(rec_dict['slider'].breakdown)
print(item_dict['slider'].cost('portion'))
print(item_dict['slider'].price('portion', scale_factor=2.5))
print(item_dict['slider'].price('portion', scale_factor=2.5)*200)
print()

print(item_dict['hot dog'].price('portion', scale_factor=2.5) *150
        + item_dict['half smoke'].price('portion', scale_factor=2) * 150
        + item_dict['slider'].price('portion', scale_factor=2.5) * 200 )
'''



'''
print(ingr_dict['salmon'].cost(1,'lb'))
print(ingr_dict['salmon'].each)
print(ingr_dict['salmon'].each_cost('lb'))
print(rec_dict['salmon'].makes)
print(rec_dict['salmon'].breakdown)
print(item_dict['salmon'].price('portion'))
'''

'''
print(rec_dict['jerk chicken'].cost)
print(rec_dict['jerk chicken'].makes)
print(Item('jerk chicken', rec_dict['jerk chicken'], ['portion']).price('portion'))
'''

'''
print(rec_dict['jerk turkey'].breakdown)
print(rec_dict['jerk turkey'].cost)
print(rec_dict['jerk turkey'].makes)
print(item_dict['jerk turkey'].cost('whole'))
print(item_dict['jerk turkey'].price('whole'))
'''

'''
print(ingr_dict['test_ingr_2'].unit)
print(ingr_dict['test_ingr_2'].density)
print(rec_dict['test recipe 1'].breakdown)
print(rec_dict['test recipe 1'].qty_dict)
print(rec_dict['test recipe 1'].cost)
print(Item('test item 1', rec_dict['test recipe 1'], ['portion']).price())
'''


'''
# Obtener ingredientes y recetas

try:
    ingredients_loc = 'C:/Users/Paul/Documents/City Chef/Ingredients'

    #ingredients_loc = 'C:/Users/Paul/Documents/City Chef/Test Ingredients'

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
    print('NO INGREDIENTS!!!1')

try:
    recipes_loc = 'C:/Users/Paul/Documents/City Chef/Recipes'

    #recipes_loc = 'C:/Users/Paul/Documents/City Chef/Test Recipes'

    recipe_directory = os.fsencode(recipes_loc)

    rec_dict = {}

    for file in os.listdir(recipe_directory):
        filename = os.fsdecode(file)
        rec_df = pd.read_csv(recipes_loc + '/' + filename)
        makes_dict = {}
        for k in range(rec_df[rec_df[['makes', 'size']].notnull().all(1)][['makes', 'size']].shape[0]):
            makes_dict[rec_df['size'][k]] = rec_df['makes'][k]
        rec_df.drop(['makes', 'size'], axis='columns', inplace=True)
        name = filename.replace('.csv','')
        rec_dict[name] = Recipe(name, rec_df, makes_dict)
        if any(s in fc.join(dict_list) for s in list(rec_dict[name].makes.keys())):
            rec_dict[name].to_ingr()

except Exception as error:
    print(error)
    print(traceback.format_exc())


###########################################
item_dict = item_dict_constructor(rec_dict)
###########################################
'''