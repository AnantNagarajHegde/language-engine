# Paridhwani — NLP Component

## 1. Project Overview

Paridhwani is a language-learning game designed to help learners understand and practise Kannada through Kanglish (Kannada written using English letters), Kannada script, and English-supported interactions.

The NLP component processes a learner's text answer, normalizes its spelling and format, identifies relevant language patterns, matches the answer against expected responses, and helps determine whether the answer should be accepted or how it should be handled.

The goal is to make answer evaluation more flexible than strict character-by-character comparison, especially when learners use different spellings or informal text.

## 2. Objectives of the NLP Component

The NLP component is designed to:

- Normalize text before comparing answers.
- Handle common spelling and transliteration variations.
- Identify the language or language style of an input.
- Match learner answers against expected answers.
- Apply structural rules when evaluating answers.
- Produce evaluation outputs used by the learning game.
- Support testing of normal inputs, unusual inputs, and edge cases.

## 3. NLP Processing Pipeline

The following is the conceptual processing flow of the NLP component.

```text
Learner's Text Answer
          |
          v
     Text Normalizer
          |
          v
   Spelling Normalizer
          |
          v
    Language Detector
          |
          v
 Answer Matcher and
  Structural Rules
          |
          v
 Evaluation Result
          |
          v
 Learning Game Uses the Result
```

The exact execution order of individual modules depends on how they are called inside the implementation. The diagram represents their overall roles, not a guarantee that every input passes through every module in this exact order.

### Step 1: Text Normalization

The normalizer prepares text for consistent processing.

Implemented in: `src/normalizer.py`

Main function:
- `normalize_text(text)`

Its current normalization operations include:

- Unicode normalization using NFKC.
- Converting text to lowercase.
- Removing leading and trailing whitespace.
- Replacing punctuation and other non-letter symbols with spaces.
- Collapsing repeated whitespace.
- Reducing excessively repeated characters.
- Reducing repeated vowel sequences.

These operations help reduce irrelevant differences between text inputs before matching.

### Step 2: Spelling Normalization

Implemented in: `src/spelling_normalizer.py`

Main class:
- `SpellingNormalizer`

This component uses the spelling-variant data to help handle alternative spellings of words. This is useful when learners write Kannada words in English letters, since the same word may be represented in multiple ways.

The spelling data is stored in `data/spelling_variants.csv`.

Spelling normalization is intended to improve matching consistency without requiring learners to use one exact spelling for every word.

### Step 3: Language Detection

Implemented in: `src/language_detector.py`

Main class:
- `LanguageDetector`

This component examines an input and identifies its language category or writing style according to the project's implemented detection logic.

The component uses vocabulary loaded from `data/responses_train.csv`.

The detected category can help the rest of the NLP system handle Kannada, English, Kanglish, mixed-language inputs, and inputs that do not contain meaningful text.

The detector's labels and classification rules are implementation-specific.

### Step 4: Answer Matching

Implemented in: `src/matcher.py`

Main class:
- `AnswerMatcher`

This is the central answer-evaluation component. It evaluates learner responses against the project's expected-answer data and returns structured evaluation information.

The implementation includes spelling-aware handling and output-field correction logic. It also contains additional matching logic for certain answer patterns and spelling variations.

The matcher works with the project's data directory, which contains the training responses and spelling variants.

The evaluation output includes fields such as:

- `outcome` — whether the answer was accepted or not accepted.
- `answer_id` — the identifier associated with an expected answer, when applicable.
- `error_category` — the category assigned to an error, when applicable.
- `correction_type` — the type of correction indicated by the evaluator, when applicable.
- `reaction_id` — an identifier for the response or reaction associated with the evaluation, when applicable.

The exact output values depend on the implemented rules and the input answer.

### Step 5: Structural Rule Matching

Implemented in: `src/structural_rules.py`

This module contains structural answer-matching and unmatched-answer diagnosis functions:

- `match_structural_rule`
- `diagnose_unmatched_answer`

Structural rules help the system recognize supported answer patterns that may not be handled adequately by a simple exact text comparison.

The module also uses the shared text-normalization function.

## 4. Project Structure

```text
Paridhwani-NLP/
│
├── data/
│   ├── responses_train.csv
│   ├── responses_test.csv
│   ├── spelling_variants.csv
│   └── translit_pairs.csv
│
├── src/
│   ├── normalizer.py
│   ├── spelling_normalizer.py
│   ├── language_detector.py
│   ├── matcher.py
│   └── structural_rules.py
│
├── tests/
│   ├── test_normalizer.py
│   ├── test_spelling_normalizer.py
│   ├── test_language_detector.py
│   ├── test_matcher.py
│   └── test_structural_rules.py
│
├── .gitignore
├── requirements.txt
└── README.md
```

## 5. Data Files

### `responses_train.csv`

Contains response data used by the language detector and answer-evaluation logic.

### `responses_test.csv`

Contains test cases used to evaluate answer-matching behavior and verify expected output fields.

### `spelling_variants.csv`

Contains spelling-variant data used by the spelling normalizer and spelling-aware matching logic.

### `translit_pairs.csv`

Contains transliteration-pair data retained as part of the NLP dataset. Transliteration pairs can represent corresponding forms of words across writing systems or representations. The file is retained for the project's language-processing data; its direct use by the current implementation should be verified separately.

## 6. Technologies Used

- **Python** — implementation of NLP processing and evaluation logic.
- **pandas** — loading and working with CSV-based data.
- **pytest** — automated testing of NLP modules.
- **Unicode normalization and regular expressions** — text preprocessing.
- **CSV datasets** — training responses, test cases, and spelling variants.

## 7. Installation and Setup

### Requirements

Python and the packages listed in `requirements.txt` are required.

From the project root, install dependencies with:

```bash
python -m pip install -r requirements.txt
```

### Run the Tests

Execute the complete test suite from the project root:

```bash
python -m pytest -v tests
```

Run an individual test module when debugging:

```bash
python -m pytest -v tests/test_normalizer.py
python -m pytest -v tests/test_spelling_normalizer.py
python -m pytest -v tests/test_language_detector.py
python -m pytest -v tests/test_matcher.py
python -m pytest -v tests/test_structural_rules.py
```

## 8. Testing Strategy

The NLP component has separate test modules for its major responsibilities.

| Test file | Purpose |
|---|---|
| `test_normalizer.py` | Checks text-normalization behavior. |
| `test_spelling_normalizer.py` | Checks spelling-variant normalization. |
| `test_language_detector.py` | Checks language classification behavior. |
| `test_matcher.py` | Checks answer evaluation and matching. |
| `test_structural_rules.py` | Checks structural rule matching and diagnosis. |

Testing should include:

- Empty strings and whitespace-only input.
- `None` and other unusual inputs where supported.
- Uppercase and lowercase variations.
- Repeated characters and punctuation.
- Kannada-script text.
- Kanglish text.
- English and mixed-language inputs.
- Known spelling variations.
- Very long inputs.
- Answers that should be accepted and answers that should not be accepted.

Automated tests help identify regressions when normalization or matching rules change. Passing tests establishes correctness for the tested cases, not for every possible learner response.

## 9. Design Considerations

### Flexible Text Handling

Learners may enter the same word in different forms. Normalization and spelling-aware matching help reduce unnecessary mismatches.

### Modular Design

Each major responsibility is implemented in a separate module. This makes the NLP component easier to test, maintain, and improve.

### Data-Driven Processing

CSV files hold response examples and spelling variants separately from the Python implementation, allowing supported data to be maintained independently of the core code.

### Edge-Case Handling

Unusual inputs should be tested explicitly so that the NLP component behaves predictably instead of failing unexpectedly.

## 10. Scope and Limitations

- Language detection follows the project's implemented rules and vocabulary; it should not be assumed to be a general-purpose language-identification model.
- Spelling normalization depends on the supported spelling variants and implemented logic.
- Structural rules cover patterns explicitly supported by the project and may not handle every possible sentence.
- An accepted answer indicates that the evaluator's rules accepted it; it does not necessarily mean that a general-purpose semantic model verified its meaning.
- The component's behavior is limited by the quality and coverage of its datasets and test cases.

## 11. Future Improvements

Possible improvements include:

- Expanding spelling-variant and transliteration coverage.
- Adding more examples of Kannada, Kanglish, English, and mixed-language responses.
- Improving handling of unseen spellings and unfamiliar words.
- Adding more edge-case and regression tests.
- Measuring precision, recall, and other appropriate evaluation metrics on a separate held-out dataset.
- Improving documentation of individual functions, input formats, and output schemas.

These are potential extensions rather than claims that the features are already implemented.

## 12. Responsibility and Integration

This repository contains the NLP component of Paridhwani. Its responsibility is text preprocessing, language detection, spelling-aware matching, structural rule evaluation, and the associated tests and datasets.

Integration with the complete game, application-level behavior, and overall project documentation are handled separately by the relevant project team members.

### Structured assessment boundary and verification

The evaluator now loads authored lesson policies alongside the training/spelling
CSVs, normalizes rule vocabularies consistently, supports reviewed item/name
templates, and rejects unsupported inputs without character-similarity acceptance.
An arbitrary bare name needs matching `player.name` context; formatted name answers
support unfamiliar alphabetic names. The game's progression and saves remain local.

See [assessment v1](docs/ASSESSMENT_V1.md) for the implemented socket-free JSON
boundary, strict schema, fixtures, validation and a standalone C# consumer. It is
separate from the game's existing text-only dialogue contract; no live service or
gameplay integration is claimed. Unknown spellings and general Kannada semantics
still need reviewed coverage.

Run `python -I -B verification/verify.py` for original tests, new regressions,
held-out comparisons, authored-policy sweeps and JSON Schema checks. It supports
direct invocation without pytest; `pandas` and `jsonschema` must already be present.
No runner downloads dependencies. See [recorded results](verification/RESULTS.md).

---

**Project:** Paridhwani — NLP Component  
**Primary language:** Python  
**Testing framework:** pytest
