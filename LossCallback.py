#From https://stackoverflow.com/questions/52038651/loss-does-not-decrease-during-training-word2vec-gensim

from gensim.models.callbacks import CallbackAny2Vec
from gensim.models import Word2Vec
import logging

# init callback class
class LossCallback(CallbackAny2Vec):
    """
    Callback to log loss to file after each epoch.
    
    """
    def __init__(self, log_file):
        self.epoch = 0
        self.log_file = log_file
        logging.basicConfig(filename=log_file, level=logging.INFO)

    def on_epoch_end(self, model):
        loss = model.get_latest_training_loss()
        if self.epoch == 0:
            log_str = f'Loss after epoch {self.epoch}: {loss}'
        else:
            print_loss = loss-self.loss_previous_step
            log_str = f'Loss after epoch {self.epoch}: {print_loss}'
        logging.info(log_str)
        self.epoch += 1
        self.loss_previous_step = loss