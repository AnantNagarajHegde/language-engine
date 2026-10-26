# Learning Design

The learning-design part of `language-engine`, owned by Member 2. It holds the Kannada curriculum and learning content for the MVP (Chapters 1–3): vocabulary, notebook pages, hints, approved answers, error categories, feedback, and the English → Kanglish → Kannada progression.

Everything is plain JSON; there is no code. Learning objectives and progression are in [`CURRICULUM.md`](CURRICULUM.md).

## Structure

```
learning-design/
├── README.md               this file
├── CURRICULUM.md           objectives, levels, vocabulary and grammar progression
└── content/
    ├── vocabulary.json     all 140 words: Kannada, Kanglish, English, role, first quest
    ├── topics/             8 notebook pages
    ├── quests/             learning content of the 11 quests (q1_1 … q3_4)
    ├── feedback.json       answer rules, error categories, NPC reactions
    ├── progression.json    levels, English shown per level, help, notebook rules, "word learned" rule
    └── address_terms.json  player names in both scripts; how NPCs address the player
```

### Vocabulary

Each word has these fields:

| Field | Meaning |
|---|---|
| `word_id` | Id used everywhere else, e.g. `w_chaha` |
| `kannada`, `kanglish`, `english` | The word in three forms |
| `role` | `say` (the player produces it), `understand` (the player only needs to understand it) or `name` |
| `first_quest` | The quest where the word first appears |
| `note` | Optional explanation |

### Notebook pages

Each topic file has:

| Field | Meaning |
|---|---|
| `title` | Page title |
| `introduction` | Short text at the top of the page |
| `words` | Word ids from `vocabulary.json`. Optional: `english` gives a page-specific meaning; `added_in` means the word appears from a later quest |
| `sentences` | Useful sentences, each in Kannada, Kanglish and English |
| `remember` | Short tips |
| `first_opens_in` | The quest that first opens the page |

### Quests

Each quest has a `topic_id`, an `objective`, a `quick_hint` and one or more `steps`. All answers are typed in Kanglish.

**Step types:**

| Type | The player… |
|---|---|
| `respond` | Types an answer |
| `collect_word` | Drags a word into the notebook |
| `read_word` | Taps a word written in Kannada script |

**Step fields:**

| Field | Meaning |
|---|---|
| `speaker`, `npc_line` | What the NPC says. Level 3 lines also carry `english_keywords`; `english_hidden` hides the English (Quest 2.2) |
| `task` | What the player must do |
| `accepted` | Approved answers, with `also_accepted` alternatives. A `reaction_id` here means the answer is accepted but the NPC corrects it |
| `anticipated_errors` | Expected mistakes, each with an `error_category` and a `reaction_id` |
| `topic_highlight` | Word or sentence ids to highlight when the page is reopened |
| `full_example` | The "Need more help?" answer |
| `target_words` | Words the step practises |
| `npc_reply` | What the NPC says after a correct answer |

### Conventions

- **Ids:**

  | Prefix | Used for |
  |---|---|
  | `q1_1` | Quest |
  | `q1_1_a` | Step |
  | `w_` | Word |
  | `s_` | Sentence |
  | `a_` | Accepted answer |
  | `e_` | Anticipated error |
  | `r_` | NPC reaction |

- **Speakers:** `conductor`, `manjunatha`, `somanna`, `shanthakka`, `basavaraju`.
- **`{player_name}`:** replace with the name from `address_terms.json`, Arun/Aditi in Kanglish and English fields, ಅರುಣ್/ಅದಿತಿ in Kannada fields.

## Integration

| Who | Uses | For |
|---|---|---|
| **Game** (`game`, Member 1) | `quests/`, `topics/`, `vocabulary.json`, `progression.json`, `address_terms.json`, reactions in `feedback.json` | Showing NPC lines, the typing box, the notebook pages, hints and NPC reactions |
| **NLP** (NLP part of `language-engine`, Member 3) | `accepted`, `also_accepted` and `anticipated_errors` in `quests/`; `answer_rules` and `error_categories` in `feedback.json` | Judging typed Kanglish answers by meaning, with any spelling. Returns which answer id matched, or an error category |
| **Integration** (`integration-pipeline`) | Quest and step ids, `target_words`, the "word learned" rule | Connecting the game to the NLP part, and testing the whole system |

### One player turn

1. The game shows the step's `npc_line` (or `task`), with English according to `progression.json`.
2. The player types an answer, or first opens the notebook on the quest's topic.
3. The game sends `quest_id`, `step_id` and the typed text through the integration layer to the NLP part.
4. The NLP part returns the matched answer id, or an error category.
5. The game reacts using this content:
   - **Correct:** shows the `npc_reply` and goes to the next step.
   - **Not accepted:** the NPC reaction plays, then the quest's `quick_hint` appears as the tip.
   - **After 2 or 3 wrong answers:** the automatic help in `progression.json` applies.
6. The integration layer records the step's `target_words` and whether help was used. These drive the "word learned" rule.

### Notes for integration

- **Ids must match.** The game must use the same quest ids and speaker names as these files.
- **Unity builds** only include files inside the Unity project. Copy `content/` into the game project (e.g. `Assets/StreamingAssets/`) at a fixed version.
- **Reading the JSON in Unity:** the built-in `JsonUtility` can't read keyed objects or lists of pairs. These appear in `address_terms.json`, the Quest 2.2 exception in `progression.json`, and the spelling examples in `feedback.json`. Use Unity's Newtonsoft JSON package.
- **Kannada script** needs a Kannada font (e.g. Noto Sans Kannada) and correct joining of letters. Test with words like ಸ್ವಲ್ಪ, ಎಷ್ಟು and ಬ್ಯಾಟರಿ.
- **Versions:** the master repo pins `language-engine` through its submodule pointer. After content changes are merged, update that pointer.

## Status

All 11 quests and 8 notebook pages are complete. The Kannada lines need checking by a tester before they go into the game.
