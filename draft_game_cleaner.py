import pandas as pd
import numpy as np
from os import path

def draft_game_cleaner(file_path):
    ''' '''
    #get list of columns we want to keep, by excluding columns we don't want:
    game_data_sample = pd.read_csv(file_path, nrows=100) #read in sample file to get columns
    drop_cols = game_data_sample.columns.drop(list(game_data_sample.filter(regex='drawn_|opening_hand_')))

    # card count columns can be int 8 (reduces memory footprint)
    int8_cols = list(game_data_sample.filter(regex='deck_|sideboard_'))
    data_types = {}
    for x in int8_cols:
        data_types[x] = 'int8'

    #read filtered game_data in chunks
    gen = pd.read_csv(file_path, chunksize = 100000, dtype = data_types)
    game_data = pd.concat((x[drop_cols] for x in gen), ignore_index=True)

    #Use the draft_id as the index
    game_data.set_index('draft_id', drop = True, inplace = True)
    
    #add column for number of games per match based on premier draft vs traditional (i.e., traditional is Best of 3)
    game_data['games_per_match'] = game_data['event_type'].apply(lambda x: 1 if x == 'PremierDraft' else 3)
    
    #To find who won each match, first find # of games won in each match
    wins_in_match = game_data.groupby(['draft_id','match_number'])['won'].sum()
    wins_in_match.name = 'wins_in_match'
    
    #create column for number of game wins in match
    game_data = game_data.join(wins_in_match, on = ['draft_id','match_number']).copy()
    #create column for whether they won the match
    game_data['won_match'] = game_data['wins_in_match'] > ( game_data['games_per_match'] / 2)
    
    # Find number of matches, match wins, losses for each draft ...
    num_matches = game_data.groupby('draft_id')['match_number'].max()
    num_matches.name = 'num_matches'
    match_wins = game_data.groupby('draft_id')['won_match'].sum()
    match_wins.name = 'match_wins'
    match_losses = num_matches - match_wins
    match_losses.name = 'match_losses'
    
    # ... and add them as columns to game_data
    game_data = game_data.join(num_matches, how='left').copy()
    game_data = game_data.join(match_wins, how='left').copy()
    game_data = game_data.join(match_losses, how='left').copy()
    
    #Validate number of cards in deck and add 'deck_size' column
    deck_cols = list(game_data.filter(regex='deck_'))
    basic_land_cols = ['deck_Island','deck_Swamp','deck_Forest','deck_Plains','deck_Mountain']

    game_data.loc[:,'num_cards'] = pd.Series(game_data[deck_cols].sum(axis=1))
    game_data.loc[:,'num_basic_lands'] = pd.Series(game_data[basic_land_cols].sum(axis=1))
    if min(game_data['num_cards']) < 40:
        raise ValueError('Found deck with less than 40 cards')
        
    #We want to get 1 row per draft_id, and we want to use only the first game of the final match in each draft.
    # (This is because by the final match they may have optimally adjusted their main deck vs sideboard,
    # but won't be strategically adjusting their deck to react to their opponent as they may in game 2 or 3 in a match)

    #Drop all games that are not the first game of the match
    game_data = game_data[game_data['game_number'] == 1].copy()
    
    #filter to final matches only
    game_data = game_data[game_data['match_number'] == game_data['num_matches']]
    
    #drop suspicious drafts (More than 9 matches) There were only ~7 of these in the SNC premier draft set
    game_data = game_data.drop(game_data[game_data['num_matches'] > 9].index).copy()
    
    #identify incomplete drafts
    inc_drafts = game_data[(game_data['match_losses'] < 3) * (game_data['match_wins'] < 7 )].copy()
    #drop them
    game_data.drop(inc_drafts.index, inplace = True)
    
    #Create pool_ columns which show all the cards drafted (sum of deck and sideboard)
    deck_cols = list(game_data.filter(regex='deck_'))
    sideboard_cols = list(game_data.filter(regex='sideboard_'))
    assert(len(deck_cols) == len(sideboard_cols))

    pool_col_names = [x.replace('deck_', 'pool_') for x in deck_cols]
    
    pool_data = pd.DataFrame(
    game_data.loc[:,deck_cols].to_numpy() + game_data.loc[:,sideboard_cols].to_numpy(),
    index = game_data.index,
    columns = pool_col_names
    )
    
    game_data = game_data.join(pool_data, how='left')

    #but zero the land columns - we don't consider those as part of the pool
    for col in ['pool_Island','pool_Mountain','pool_Swamp','pool_Plains','pool_Forest']:
        game_data.loc[:][col].values[:] = 0
    
    #Save to CSV
    game_data.to_csv(path.dirname(file_path) + '\\CLEANED_' + path.basename(file_path))