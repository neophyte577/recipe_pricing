from warnings import simplefilter
simplefilter(action='ignore', category=Warning)
import numpy as np
import pandas as pd
import funcy as fc
import os, sys
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

    
    def cost(self, qty=1, target_unit=None):

        if target_unit == None:

            ingr_cost = qty * self.unit_cost
            return ingr_cost, qty, target_unit
        
        elif target_unit in unit_list:

            if any(all(u in d for u in [target_unit, self.unit]) for d in unit_dict_list):
                ingr_cost = qty * cost_converter(self.unit_cost, self.unit, target_unit)
                return ingr_cost, qty, target_unit
            
            elif (target_unit in weight_dict) and (self.unit in vol_dict):
                ingr_cost = qty * cost_converter((1 / self.density) * self.unit_cost, 'g', target_unit)
                return ingr_cost, qty, target_unit
            
            elif (target_unit in vol_dict) and (self.unit in weight_dict):
                ingr_cost = qty * cost_converter(self.density * self.unit_cost, 'c', target_unit)
                return ingr_cost, qty, target_unit

            elif ((target_unit in count_dict) and (self.unit not in count_dict)):           
                ingr_cost = qty * unit_converter(1, target_unit, 'ea') * self.each_cost()
                return ingr_cost, qty, target_unit
            elif ((target_unit not in count_dict) and (self.unit in count_dict)):
                ingr_cost = qty * (1 / self.each_converter(target_unit)) * self.unit_cost
                return ingr_cost, qty, target_unit
                
            else:
                print('watt')

        else:
            print(target_unit)
            print('InvalidTargetUnitError in', self.name + '.cost()')
    
    
    def price(self, qty=1, target_unit=None, scale_factor=3):

        if target_unit == None:
            ingr_price = scale_factor * qty * self.unit_cost

        elif target_unit in unit_list:
            ingr_price = scale_factor * qty * self.cost(target_unit)

        else:
            print(target_unit)
            print('InvalidTargetUnitError in', self.name + 'ingr.price()')

        return ingr_price


    def each_converter(self, target_unit):
    
        if self.each_list != []:
            each_qty = self.each_list[0]
            each_unit = self.each_list[1]
            if any(all(u in d for u in [target_unit, each_unit]) for d in [weight_dict, vol_dict]):
                for d in [weight_dict, vol_dict]:
                    if each_unit and target_unit in d:
                        converted_each_qty = each_qty * ( d[target_unit] / d[each_unit]  ) 
                        return converted_each_qty
                    else:
                        pass
            else:
                if self.density != np.pi:
                    if (target_unit in weight_dict) and (each_unit in vol_dict):
                        each_qty_in_g = self.density * unit_converter(each_qty, each_unit, 'c')
                        converted_each_qty = unit_converter(each_qty_in_g, 'g', target_unit)
                        return converted_each_qty
                    elif (target_unit in vol_dict) and (each_unit in weight_dict):
                        each_qty_in_c = (1 / self.density) * unit_converter(each_qty, each_unit, 'g')
                        converted_each_qty = unit_converter(each_qty_in_c, 'c', target_unit)
                        return converted_each_qty
                else:
                    print('NoDensityError in', self.name + '.each_converter()')
        else:
            print('NoEachError in', self.name + '.each_converter()')
 
    
    def each_cost(self):

        each_unit = self.each_list[1]
        
        if self.each_list != []:
            if any(all(u in d for u in [self.unit, each_unit]) for d in [weight_dict, vol_dict]):
                each_cost = self.each_list[0] * cost_converter(self.unit_cost, self.unit, each_unit)
                return each_cost
            elif (self.unit in weight_dict) and (each_unit in vol_dict):
                each_cost = self.each_list[0] * cost_converter(self.density * self.unit_cost, 'c', each_unit)
                return each_cost
            elif (self.unit in vol_dict) and (each_unit in weight_dict):
                each_cost = self.each_list[0] * cost_converter((1 / self.density) * self.unit_cost, 'g', each_unit)
                return each_cost
            else:
                print('UnitConversionError in,', self.name + '.each_cost()')
        else:
            print('NoEachError in,', self.name + '.each_cost()')

    
class Recipe():
    
    def __init__(self, name, rec_df):
        self.name = name
        self.rec_df = rec_df
        self.makes = {}

        makes_df = rec_df[rec_df[['makes','size']].notnull().all(axis='columns')][['makes','size']]

        for k, row in makes_df.iterrows():
            if (row['size'] in size_list) or (row['size'] in unit_list):
                self.makes.update({row['size']:row['makes']})


    def qty_dict_constructor(self):
        
        qty_dict = {}

        for k, row in self.rec_df.iterrows():

            ingredient = ingr_dict[row['ingr']]
            quantity = row['qty']
            unit = row['unit']

            qty_dict[ingredient] = [quantity, unit]

        return qty_dict
    

    def cost(self):
    
        rec_cost = 0
        
        qty_dict = self.qty_dict_constructor()
        
        for ingredient in qty_dict:
            rec_cost += ingredient.cost(qty_dict[ingredient][0], qty_dict[ingredient][1])[0]
        
        return rec_cost
    

    def to_ingr(self, density=np.pi, each_list=[]):

        if any(s in unit_list for s in list(self.makes.keys())):
            
            for s in list(self.makes.keys()):
                yield_qty = self.makes[s]
                yield_unit = s
                for d in unit_dict_list:
                    if yield_unit in d:
                        ingr_unit = get_base_unit(d)
                        given_unit_cost = self.cost() / yield_qty
                        unit_cost = cost_converter(given_unit_cost, yield_unit, ingr_unit)
                        ingr_dict.update({self.name : Ingredient(self.name, unit_cost, ingr_unit, density, each_list)})
                        return
                  
        else:
            print('NoYieldError in', self.name + '.to_ingr()')


    def breakdown(self):

        cost = []

        for k, row in self.rec_df.iterrows():
            cost.append(round(ingr_dict[row['ingr']].cost(row['qty'], row['unit'])[0], 2))

        frame_dict = {'qty':list(self.rec_df['qty']), 'unit':list(self.rec_df['unit']), 'cost':cost}

        breakdown = pd.DataFrame(frame_dict, index=self.rec_df['ingr']).rename_axis(self.name.upper())

        return breakdown


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
            item_cost = self.recipe.cost() / self.recipe.makes[size]
            return item_cost
        elif size in size_dict:
            if any(k in size_dict for k in self.recipe.makes):
                makes_dict = {k:self.recipe.makes[k] for k in [sz for sz in self.recipe.makes if sz in size_dict]}
                makes_sz = list(makes_dict.keys())[0]
                makes_qty = makes_dict[makes_sz]
                converted_makes_qty = unit_converter(makes_qty, makes_sz, size)
                item_cost = self.recipe.cost() / converted_makes_qty
                return item_cost
            else:
                print(size)
                print('ConversionError in', self.name + '.cost(): No serving size in recipe.')
        elif size in vol_dict:
            if any(k in vol_dict for k in self.recipe.makes):
                yield_dict = {k:self.recipe.makes[k] for k in [unit for unit in self.recipe.makes if unit in vol_dict]}
                yield_unit = list(yield_dict.keys())[0]
                yield_qty = yield_dict[yield_unit]
                converted_yield_qty = unit_converter(yield_qty, yield_unit, size)
                item_cost = self.recipe.cost() / converted_yield_qty
                return item_cost
            else:
                print(size)
                print('ConversionError in', self.name + '.cost(): No volumetric yield in recipe.')
        elif size in weight_dict:
            if any(k in weight_dict for k in self.recipe.makes):
                yield_dict = {k:self.recipe.makes[k] for k in [unit for unit in self.recipe.makes if unit in weight_dict]}
                yield_unit = list(yield_dict.keys())[0]
                yield_qty = yield_dict[yield_unit]
                converted_yield_qty = unit_converter(yield_qty, yield_unit, size)
                item_cost = self.recipe.cost() / converted_yield_qty
                return item_cost
            else:
                print(size)
                print('ConversionError in', self.name + '.cost(): No mass yield in recipe.')       
        else:
            print(size)
            print('InvalidTargetUnitError in', self.name + '.cost()')     


    def price(self, size='portion', scale_factor=3):
        try:
            item_price = round(scale_factor * self.cost(size), 2)
            return item_price
        except Exception as error:
            print('Error in', self.name + '.price():', error)


# Lists and Dictionaries (Global)

count_dict = {'ea':1, 'each':1, 'dozen':1/12, 'dz':1/12, 'score':1/20, 'gross':1/144}

weight_dict = {'g':1, 'kg':0.001, 'lb':1/453.592, 'lbm':1/453.592, 'lbs':1/453.592, 'oz':1/28.3495}

vol_dict = {'c':1, 'cup':1, 'L':0.2365882365, 'liter':0.2365882365, 'ml':236.5882365, 'floz':8, 'tbsp':16, 'tsp':48, 'pinch':768,
            'dash':384, 'gal':1/16, 'gallon':1/16, 'bushel':1/128, 'qt':1/4, 'quart':1/4, 'pt':1/2, 'pint':1/2}

base_dict = {'ea':count_dict, 'g':weight_dict, 'c':vol_dict}

size_dict = {'portion':1, 'quarter pan':1/7.5, 'half pan':1/15, 'full pan':1/30}

parts_dict = {'whole':1, 'half':2, 'quarter':4}

piece_dict = {'piece':1}

size_list = list(size_dict.keys()) + list(parts_dict.keys()) + list(piece_dict.keys()) + list(vol_dict.keys())

size_to_vol_dict = {}

vol_dict.update(size_to_vol_dict)

unit_dict_list = [count_dict, weight_dict, vol_dict]

unit_list = list(fc.join(unit_dict_list).keys())

ingr_dict, rec_dict, item_dict = {}, {}, {}


# Functions

def unit_converter(qty, given_unit, target_unit, ingr_name=None):

    big_unit_dict_list = unit_dict_list + [size_dict]
    
    if any(all(u in d for u in [given_unit, target_unit]) for d in big_unit_dict_list): 
        
        for d in big_unit_dict_list:
            
            if given_unit in d:
                converted_qty = ( d[target_unit] / d[given_unit] ) * qty
                return converted_qty
            else:
                pass 

    elif ingr_name != None:

        ingredient = ingr_dict[ingr_name]

        density = ingredient.density

        if given_unit in count_dict:

            unit_converter(qty, given_unit, 'ea')

            return ingredient.each_converter(target_unit)

        else:

            if density != np.pi:

                if given_unit in weight_dict and target_unit in vol_dict:

                    in_grams = unit_converter(qty, given_unit, 'g')

                    in_cups = in_grams / density

                    return unit_converter(in_cups, 'c', target_unit)

                elif given_unit in vol_dict and target_unit in weight_dict:            

                    in_cups = unit_converter(qty, given_unit, 'c')

                    in_grams = in_cups * density

                    return unit_converter(in_grams, 'g', target_unit)
            
            else:

                print('NoDensityError in unit_converter')

    else:
        print(given_unit, '-->', target_unit)
        print('InvalidUnitError in unit_converter()')


def cost_converter(cost, per_unit, target_unit):
    
    if any(all(u in d for u in [per_unit, target_unit]) for d in unit_dict_list):
        
        for d in unit_dict_list:
            if per_unit in d:
                converted_cost = ( d[per_unit] / d[target_unit] ) * cost
                return converted_cost
            else:
                pass
        
    else:
        print(per_unit)
        print('InvalidUnitError in cost_converter()')


def get_base_unit(unit_or_dict):

    if type(unit_or_dict) == str:
        unit = unit_or_dict
        if unit in unit_list:
            for base_unit in base_dict:
                if unit in base_dict[base_unit]:
                    return base_unit
                else:
                    pass
        else:
            print('InvalidUnitError in get_base_unit(): Input unit not contained in any global conversion dictionary.')

    elif type(unit_or_dict) == dict:
        dictionary = unit_or_dict
        if dictionary in unit_dict_list:
            for base_unit in base_dict:
                if dictionary == base_dict[base_unit]:
                    return base_unit
                else:
                    pass
        else:
            print('InvalidInputError in get_base_unit(): Input conversion dictionary must be vol_dict, weight_dict, or count_dict.')


def ingr_df_cleaner(ingr_df):

    df = ingr_df.copy(deep=True)

    df.dropna(axis='index', how='any', subset=['name', 'qty', 'cost', 'unit'])

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

        if given_unit in unit_list:

            for d in unit_dict_list:

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
            print('InvalidUnitError in ingr_dict_constructor():', df['name'][j], 
                  "not added to ingredient dictionary due to invalid unit '" + df['unit'][j] + "'")
            print()
    
    return ingr_dict


def get_recipes(recipes_loc):

    recipe_directory = os.fsencode(recipes_loc)

    rec_df_dict = {}

    for file in os.listdir(recipe_directory):

        filename = os.fsdecode(file)
        
        if filename.endswith('csv'):

            try:
                rec_df = pd.read_csv(recipes_loc + '/' + filename)

            except Exception as error:
                print(error, 'in', filename)
                print(filename.partition('.')[0], 'recipe not added to recipe dictionary')
                continue

            name = filename.replace('.csv','')

            rec_df_dict.update({name : rec_df})
        
        else:
            pass

    return rec_df_dict

    
def rec_dict_constructor(rec_df_dict):

    rec_dict = {}

    # First pass to read simple recipes (containing only primary ingredients from initial ingr_dict) and ingredient recipes (e.g., sauces) 

    for name, rec_df in rec_df_dict.items():

        try:

            if rec_df['ingr'].isin(list(ingr_dict.keys())).all():

                try:
                    rec_dict[name] = Recipe(name.lower(), rec_df)
                    if any(s in unit_list for s in list(rec_dict[name].makes.keys())):
                        rec_dict[name].to_ingr()

                except Exception as error:
                    print(error, 'in first iteration of recipe_dict_constructor().')

            else:
                pass

        except Exception as error:
            print('Error in rec_dict_constructor():', error)
            print(traceback.format_exc())
            print(name, 'recipe not added to recipe dictionary')
            continue

    # Second pass to read compound recipes, i.e., those recipes containing other recipes' Items as ingredients

    for name, rec_df in rec_df_dict.items():

        try:

            if (rec_df['ingr'].isin(list(ingr_dict.keys())).all()) and (name not in rec_dict):

                try:
                    rec_dict[name] = Recipe(name.lower(), rec_df)

                except Exception as error:
                    print('Error in second iteration of rec_dict_constructor():', error)
                    print(traceback.format_exc())
                    print(name, 'recipe not added to recipe dictionary')
                    continue

            elif name in rec_dict:
                pass

            else:
                ingr_errors = list(rec_df[~rec_df['ingr'].isin(list(ingr_dict.keys()))]['ingr'])
                print()
                print('IngredientError with', name, 'in readRecipes:', ingr_errors)
                print(name, 'recipe not added to recipe dictionary')
                print()
                continue

        except Exception as error:
            print('Error in rec_dict_constructor():', error)
            print(traceback.format_exc())
            print(name, 'recipe not added to recipe dictionary')
            continue

    return rec_dict


def item_dict_constructor(rec_dict):

    item_dict = {}

    for recipe_name in rec_dict:

        item_dict.update({ recipe_name : Item(recipe_name, rec_dict[recipe_name]) })
    
    return item_dict


def output_template(name, size='portion', scale_factor=3):

    output = '\n' + str(rec_dict[name].breakdown()) + '\n\n' + 'Recipe cost: ' + str(round(rec_dict[name].cost(),2)) + '\n\n' + 'Item cost per ' + size + ': ' + str(round(item_dict[name].cost(size),2)) + '\n\n' + 'Item price per ' + size +  ' with scale factor of ' + str(scale_factor) + ': ' + str(item_dict[name].price(size, scale_factor))

    print()
    print(rec_dict[name].breakdown())
    print()
    print('Recipe cost:', round(rec_dict[name].cost(),2))
    print()
    print('Item cost per', size + ':', round(item_dict[name].cost(size),2))
    print()
    print('Item price per', size, 'with scale factor of', str(scale_factor) + ':', item_dict[name].price(size, scale_factor))
    print()
    print('---------------------')
    print()

    #print(output)

    return output


def resolve_path(relative_path):

    try:
        root_path = sys._MEIPASS
        
    except Exception:
        root_path = os.path.abspath(".")

    path = os.path.join(root_path, relative_path)

    return path


def main():

    try:
        
        global ingr_df

        ingredients_path = resolve_path('dep/Ingredients/ingredients.csv')

        ingr_df = ingr_df_cleaner(pd.read_csv(ingredients_path))
        
        ingr_dict.update(ingr_dict_constructor(ingr_df))

    except Exception as error:
        print(error)
        print('NO INGREDIENTS!!!1')
        print('Better luck next time')
        exit()

    try:

        #recipes_loc = 'Recipes'

        recipes_loc = resolve_path('dep/Recipes')

        rec_df_dict = get_recipes(recipes_loc)

        global rec_dict

        rec_dict = rec_dict_constructor(rec_df_dict)

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
    ########################################################

start = time()

if __name__ == '__main__':
    main()

stop = time()

print()
print('Execution time:', stop - start)
print()


