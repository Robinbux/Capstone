from bip_utils import Bip39MnemonicGenerator, Bip39WordsNum
import hashlib


def generate_random_seed_phrase() -> (str, bytes):
    # Generate a random mnemonic string of 12 words with default language (English)
    mnemonic = Bip39MnemonicGenerator().FromWordsNumber(Bip39WordsNum.WORDS_NUM_12)
    sha512_hash = hashlib.sha512(str(mnemonic).encode("utf-8")).digest()
    return mnemonic, sha512_hash
