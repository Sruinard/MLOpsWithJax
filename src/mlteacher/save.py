
# model trained in https://github.com/Sruinard/machine_learning_novice/blob/main/introduction_to_deep_learning_with_jax/ml_with_jax_part_4.ipynb
import jax.random as jrandom
import functools
import jax
import jax.numpy as jnp
import flax.linen as nn
from typing import Tuple, Any

import tensorflow as tf
import tree
from jax.experimental import jax2tf
import sonnet as snt
Array = Any
PRNGKey = Any


def create_variable(path, value):
    name = '/'.join(map(str, path)).replace('~', '_')
    return tf.Variable(value, name=name)


class JaxModule(snt.Module):
    def __init__(self, params, apply_fn, name=None):
        super().__init__(name=name)
        self._params = tree.map_structure_with_path(create_variable, params)
        self._apply = jax2tf.convert(lambda p, x: apply_fn(
            {"params": p}, x, rngs={"lstm": jrandom.PRNGKey(1)}))

        self._apply = tf.autograph.experimental.do_not_convert(self._apply)

    def __call__(self, inputs):
        return self._apply(self._params, inputs)


class DecoderLSTM(nn.Module):
    """DecoderLSTM Module wrapped in a lifted scan transform.
    Attributes:
      teacher_force: See docstring on Seq2seq module.
      vocab_size: Size of the vocabulary.
    """
    teacher_force: bool
    vocab_size: int

    @nn.compact
    def __call__(self, x: Array) -> Array:
        """Applies the DecoderLSTM model."""
        logits = nn.Dense(features=self.vocab_size)(x)
        # Sample the predicted token using a categorical distribution over the
        # logits.
        categorical_rng = self.make_rng('lstm')
        predicted_token = jax.random.categorical(categorical_rng, logits)
        # Convert to one-hot encoding.
        prediction = jax.nn.one_hot(
            predicted_token, self.vocab_size, dtype=jnp.float32)

        return prediction


teacher_force = False
hidden_size = 512
# eos_id = char_lookup_table.eos_id
# vocab_size = char_lookup_table.vocab_size
eos_id = 10
vocab_size = 3
batch_size = 1
max_input_sequence_len = 2
max_output_sequence_len = 2
model = DecoderLSTM(
    teacher_force=teacher_force,
    vocab_size=vocab_size
)
rng = jax.random.PRNGKey(0)
params_key, lstm_key = jax.random.split(rng)
# max_input_sequence_len = char_lookup_table.max_input_len
# max_output_sequence_len = char_lookup_table.max_output_len
variables = model.init(
    {
        "params": params_key,
        "lstm": lstm_key
    },
    jnp.ones((batch_size, vocab_size), dtype=jnp.float32)
)

net = JaxModule(variables['params'], model.apply)
[v.name for v in net.trainable_variables]


def _get_serving_default():
    batch_size = 1
    input_signatures = [
        tf.TensorSpec((batch_size, vocab_size), tf.float32),
    ]
    return input_signatures


serving_spec = _get_serving_default()


@tf.function  # (autograph=False, input_signature=serving_spec)
def forward(x):
    return net(x)


signatures = {}
serving_spec = _get_serving_default()
signatures[tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY] = forward.get_concrete_function(
    serving_spec[0])


to_save = tf.Module()
to_save.forward = forward
to_save.params = list(net.variables)

tf.saved_model.save(to_save, "./models/brain/123", signatures=signatures)
