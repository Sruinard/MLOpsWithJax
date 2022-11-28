
from typing import Callable, Dict


import jax
from jax.experimental import jax2tf
import numpy as np

from datetime import datetime
import os
import tensorflow as tf


# The transformed feature names

# Type abbreviations: (B is the batch size)
_Array = np.ndarray
_InputBatch = Dict[str,
                   _Array]  # keys are _FEATURE_KEYS_XF and values f32[B, 1]


class _SavedModelWrapper(tf.train.Checkpoint):
    """Wraps a function and its parameters for saving to a SavedModel.
    Implements the interface described at
    https://www.tensorflow.org/hub/reusable_saved_models.
    This class contains all the code needed to convert a Flax model to a
    TensorFlow saved model.
    """

    def __init__(self,
                 tf_graph: Callable[[_InputBatch], _Array],
                 param_vars: Dict[str, tf.Variable]):
        """Builds the tf.Module.
        Args:
          tf_graph: a tf.function taking one argument (the inputs), which can be be
            tuples/lists/dictionaries of np.ndarray or tensors. The function may
            have references to the tf.Variables in `param_vars`.
          param_vars: the parameters, as tuples/lists/dictionaries of tf.Variable,
            to be saved as the variables of the SavedModel.
        """
        super().__init__()
        # Implement the interface from
        # https://www.tensorflow.org/hub/reusable_saved_models
        self.variables = tf.nest.flatten(param_vars)
        self.trainable_variables = [v for v in self.variables if v.trainable]
        self._tf_graph = tf_graph

    @tf.function
    def __call__(self, inputs):
        return self._tf_graph(inputs)


def create_tensorflow_graph(model, training_params):
    def predict_fn(params, input): return model.apply(
        {"params": params}, *input, rngs={"lstm": jax.random.PRNGKey(1)})
    tf_fn = jax2tf.convert(predict_fn, with_gradient=False, enable_xla=True)

    param_vars = tf.nest.map_structure(
        # Due to a bug in SavedModel it is not possible to use tf.GradientTape
        # on a function converted with jax2tf and loaded from SavedModel.
        # Thus, we mark the variables as non-trainable to ensure that users of
        # the SavedModel will not try to fine tune them.
        lambda param: tf.Variable(param, trainable=False),
        training_params)
    tf_graph = tf.function(
        lambda inputs, decoder_inputs: tf_fn(
            param_vars, (inputs, decoder_inputs)),
        autograph=False,
        experimental_compile=True)
    return tf_graph, param_vars


def save_model(model, params, ctable, serving_dir, model_name):
    def _get_serving_default(ctable):
        batch_size = 1
        input_signatures = [
            tf.TensorSpec((batch_size,) + (ctable.max_input_len,
                          ctable.vocab_size), tf.float32),
            tf.TensorSpec((batch_size,) + (ctable.max_output_len,
                          ctable.vocab_size), tf.float32)
        ]
        return input_signatures

    signatures = {}
    serving_spec = _get_serving_default(ctable)
    tf_graph, param_vars = create_tensorflow_graph(model, params)
    signatures[tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY] = tf_graph.get_concrete_function(
        serving_spec[0], serving_spec[1])

    latest_model_subpath = datetime.now().strftime("%Y%m%d%H%M%S")
    tf_model = _SavedModelWrapper(tf_graph, param_vars)
    model_serving_path = os.path.join(
        serving_dir, model_name, latest_model_subpath)
    tf.saved_model.save(tf_model, model_serving_path, signatures=signatures)
    return model_serving_path
