import os
import logging
from argparse import ArgumentParser

from vocab import Vocab
from lmdataset import LMDataset
from lm import NeuralLM
from deepy.dataset import SequentialMiniBatches
from deepy.trainers import MomentumTrainer, SGDTrainer, LearningRateAnnealer
from deepy.layers import RNN, IRNN


logging.basicConfig(level=logging.INFO)

model_path = "/tmp/rnn_lm_params12.gz"
resource_dir = os.path.abspath(os.path.dirname(__file__)) + os.sep + "resources"

train_path = os.path.join(resource_dir, "ptb.train.txt")
train_small_path = os.path.join(resource_dir, "ptb.train.10k.txt")
valid_path = os.path.join(resource_dir, "ptb.valid.txt")
vocab = Vocab(char_based=True)
vocab.load(train_path, fixed_size=1000)

model = NeuralLM(input_dim=vocab.size, input_tensor=3)
model.stack_layers(
    IRNN(hidden_size=100, output_size=vocab.size, output_type="all_output"))


if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument("model", default=os.path.join(os.path.dirname(__file__), "models", "char_irnn_model1.gz"))
    args = ap.parse_args()

    if os.path.exists(args.model):
        model.load_params(args.model)

    lmdata = LMDataset(vocab, train_small_path, valid_path, history_len=-1, char_based=True, max_tokens=300)
    batch = SequentialMiniBatches(lmdata, batch_size=20)

    trainer = SGDTrainer(model)
    annealer = LearningRateAnnealer(trainer)

    trainer.run(batch, controllers=[annealer])

    model.save_params(args.model)