import requests
import warnings
import time

def scry(card_names):
    ''' Sends requests to the Scryfall API and returns a list containing a response
     for each card name in card_names. Warns when api calls are unsuccessful.
    
    Parameters
    ----------
        card_name: iterable
            must be an iterable of strings.
    
    Returns
    -------
        a list of scryfall api responses
    '''
    output = []
    unsuccessful = 0
    
    for card in card_names:
        response = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + card)

        # test for unsuccessful requests but do not raise an error
        try:
            response.raise_for_status()
        except(requests.exceptions.HTTPError):
            unsuccessful += 1

        output.append(response)
        time.sleep(0.1) # avoid flooding scryfall with requests, as per their guidance
    
    if unsuccessful > 0:
        warnings.warn('Warning: ' + str(unsuccessful) + ' requests to scryfall API')
    
    return output