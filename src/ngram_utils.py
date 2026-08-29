import re
import math
import joblib

TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:[./-][a-z0-9]+)*")
EPSILON = 1e-300

def tokenize(text):
    text = "" if text is None else str(text).lower().strip()
    return TOKEN_PATTERN.findall(text)

class NGramScorer:
    def __init__(self, artifact_path):
        self.artifacts = joblib.load(artifact_path)
        self.vocabulary = set(self.artifacts["vocabulary"])
        self.class_models = {int(k): v for k, v in self.artifacts["class_models"].items()}
        self.class_priors = {int(k): float(v) for k, v in self.artifacts["class_priors"].items()}
        self.unigram_alpha = float(self.artifacts["unigram_alpha"])
        self.vocabulary_size = int(self.artifacts["vocabulary_size"])

    def map_tokens(self, tokens):
        return [t if t in self.vocabulary else "<UNK>" for t in tokens]

    def _unigram_probability(self, model, word):
        V = self.vocabulary_size + 1
        return (model["unigram_counts"].get(word, 0) + self.unigram_alpha) / (
            model["unigram_total"] + self.unigram_alpha * V
        )

    def _continuation_probability(self, model, word):
        total_types = model["total_bigram_types"]
        if total_types == 0:
            return self._unigram_probability(model, word)
        p = model["continuation_counts"].get(word, 0) / total_types
        return p if p > 0 else self._unigram_probability(model, word)

    def _bigram_probability(self, model, history, word):
        context_count = model["bigram_context_counts"].get(history, 0)
        if context_count == 0:
            return self._continuation_probability(model, word)

        count = model["bigram_counts"].get((history, word), 0)
        D = model["bigram_discount"]
        first = max(count - D, 0.0) / context_count
        n1plus = model["bigram_unique_continuations"].get(history, 0)
        lam = D * n1plus / context_count
        return first + lam * self._continuation_probability(model, word)

    def _trigram_probability(self, model, h1, h2, word):
        context = (h1, h2)
        context_count = model["trigram_context_counts"].get(context, 0)
        if context_count == 0:
            return self._bigram_probability(model, h2, word)

        count = model["trigram_counts"].get((h1, h2, word), 0)
        D = model["trigram_discount"]
        first = max(count - D, 0.0) / context_count
        n1plus = model["trigram_unique_continuations"].get(context, 0)
        lam = D * n1plus / context_count
        return first + lam * self._bigram_probability(model, h2, word)

    def score(self, tokens, class_label, order):
        if order not in (1, 2, 3):
            raise ValueError("order must be 1, 2, or 3")

        label = int(class_label)
        model = self.class_models[label]
        tokens = self.map_tokens(tokens)
        ll = 0.0

        if order == 1:
            for word in tokens:
                ll += math.log(max(self._unigram_probability(model, word), EPSILON))
            return ll

        if order == 2:
            seq = ["<BOS>"] + tokens + ["<EOS>"]
            for i in range(1, len(seq)):
                p = self._bigram_probability(model, seq[i-1], seq[i])
                ll += math.log(max(p, EPSILON))
            return ll

        seq = ["<BOS>", "<BOS>"] + tokens + ["<EOS>"]
        for i in range(2, len(seq)):
            p = self._trigram_probability(model, seq[i-2], seq[i-1], seq[i])
            ll += math.log(max(p, EPSILON))
        return ll

    def log_prior(self, class_label):
        return math.log(max(self.class_priors[int(class_label)], EPSILON))
