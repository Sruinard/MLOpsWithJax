from typing import Any, Dict, Tuple
import numpy as np
import jax
import jax.numpy as jnp

Array = Any


class CharacterTable:

    def __init__(self, chars, max_len_query_digit: int = 3) -> None:
        self._chars = sorted(set(chars))
        # reserve index 0 and 1 for special tokens
        self._char_indices = {
            ch: idx + 2 for idx, ch in enumerate(self._chars)}
        self._indices_char = {
            idx + 2: ch for idx, ch in enumerate(self._chars)}
        self._indices_char[self.pad_id] = '_'
        self._indices_char[self.eos_id] = "|"
        # Maximum length of a single input digit.
        self._max_len_query_digit = max_len_query_digit

    @property
    def pad_id(self) -> int:
        return 0

    @property
    def eos_id(self) -> int:
        return 1

    @property
    def vocab_size(self) -> int:
        # All characters + pad token and eos token.
        return len(self._chars) + 2

    @property
    def max_input_len(self) -> int:
        """Returns the max length of an input sequence."""
        # The input has the form "digit1+digit2<eos>", so the max input length is
        # the length of two digits plus two tokens for "+" and the EOS token.
        return self._max_len_query_digit * 2 + 2

    @property
    def max_output_len(self) -> int:
        """Returns the max length of an output sequence."""
        # The output has the form "=digit<eos>". If `digit` is the result of adding
        # two digits of max length x, then max length of `digit` is x+1.
        # Additionally, we require two more tokens for "=" and "<eos".
        return self._max_len_query_digit + 3

    def one_hot(self, tokens: np.ndarray) -> np.ndarray:
        vectors = np.zeros((tokens.size, self.vocab_size), dtype=np.float32)
        vectors[np.arange(tokens.size), tokens] = 1
        # you can think of the np.arange(token.size) as the timesteps
        # and tokens as the number of features (as it is one hot encoded)
        return vectors

    def encode(self, string_input):
        return np.array([self._char_indices[char] for char in string_input] + [self.eos_id])

    def encode_one_hot(self, batch_inputs: str) -> np.ndarray:
        # query --> tokens --> padded tokens
        def encode_str(string_input):
            tokens = self.encode(string_input)
            n_tokens_to_pad = self.max_input_len - len(tokens)
            tokens_with_padding = np.pad(tokens, [(0, n_tokens_to_pad)])
            assert tokens_with_padding.shape == (self.max_input_len, )
            one_hot_encoded_tokens = self.one_hot(tokens_with_padding)
            assert one_hot_encoded_tokens.shape == (
                self.max_input_len, self.vocab_size)
            return one_hot_encoded_tokens
        return np.array([encode_str(inp) for inp in batch_inputs])

    def generate_samples(self, n_samples, step: int):
        rngs = jax.random.split(jax.random.PRNGKey(step), n_samples)
        for rng_key in rngs:

            max_digit = pow(10, self._max_len_query_digit) - 1
            # generate random values
            first_value = jax.random.randint(rng_key, [1], 0, 99)[0]
            second_value = jax.random.randint(rng_key, [1], 0, max_digit)[0]
            inputs = f'{first_value}+{second_value}'
            # Preprend output by the decoder's start token.
            outputs = '=' + str(first_value + second_value)
            yield (inputs, outputs)

    def get_batch(self, batch_size: int, step: int) -> Dict[str, np.ndarray]:
        """Returns a batch of example of size @batch_size."""
        inputs, outputs = zip(*self.generate_samples(batch_size, step=step))
        return {
            'query': self.encode_one_hot(inputs),
            'answer': self.encode_one_hot(outputs),
        }

    def decode(self, inputs: Array) -> str:
        """Decodes from list of integers to string."""
        chars = []
        for elem in inputs.tolist():
            if elem == self.eos_id:
                break
            chars.append(self._indices_char[elem])
        return ''.join(chars)

    def decode_onehot(self, batch_inputs: Array) -> np.ndarray:
        """Decodes a batch of one-hot encoding to strings."""
        def decode_inputs(inputs): return self.decode(inputs.argmax(axis=-1))
        return np.array(list(map(decode_inputs, batch_inputs)))

    @property
    def encoder_input_shape(self) -> Tuple[int, int, int]:
        return (1, self.max_input_len, self.vocab_size)

    @property
    def decoder_input_shape(self) -> Tuple[int, int, int]:
        return (1, self.max_output_len, self.vocab_size)


def mask_sequences(sequence_batch: Array, lengths: Array) -> Array:
    """Sets positions beyond the length of each sequence to 0."""
    return sequence_batch * (
        lengths[:, np.newaxis] > np.arange(sequence_batch.shape[1])[np.newaxis])


def get_sequence_lengths(sequence_batch: jnp.ndarray, eos_id: int) -> Array:
    # as we are dealing with a one hot encoded variable and we now the eos_id, we can select the column
    # representing the eos_id and find it's argmax. Because if we find it's argmax
    # we know everything after that index will be padded.
    eos_row = sequence_batch[:, :, eos_id]
    # get the first occurence when we get the end of sentence id
    eos_idx = jnp.argmax(eos_row, axis=-1)
    return jnp.where(
        eos_row[jnp.arange(eos_row.shape[0]), eos_idx],
        # the +1 makes sure we include the eos token, which will also be needed during inference to know when to stop generating.
        eos_idx + 1,
        # if no eos id is present, use the entire sequence as target
        sequence_batch.shape[1]
    )
