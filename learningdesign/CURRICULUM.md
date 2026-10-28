# Curriculum

- **Learner:** an English speaker with no Kannada.
- **Route:** English → Kanglish → Kannada script.
- **How the player answers:** by typing in Kanglish.
- **Length:** 3 levels, 11 quests.

## Levels

Difficulty rises in three ways: English support is withdrawn, the player reads more script, and politeness and grammar build up.

| Level | Place | English shown | The player learns to… | Script task |
|---|---|---|---|---|
| 1 | Bus Stand & Tea Stall | Full | Greet and thank; ask for something; say yes/no; say their name; ask where a place is | Bonus: read ಚಹಾ |
| 2 | Library | Full, but hidden in Quest 2.2 | Speak politely to an elder; understand a sentence without English; ask where a thing is | Drag ಕೀಲಿ into the notebook |
| 3 | Shanthakka's Mess | Keywords only (the player can switch full English back on) | Order food; say "enough"; ask a price; understand amounts from 1 to 1,000; ask where a person is | Read ಬಸವರಾಜು on a note |

## Quest objectives

| Quest | Notebook topic | Objective | Words the player says |
|---|---|---|---|
| 1.1 | Greetings and Thanks | Thank someone | dhanyavada |
| 1.2 | Ordering at a Shop | Ask for something; answer a yes/no offer | nanage, chaha, beku, beda, haudu, illa |
| 1.3 | Introducing Yourself | Say your name | nanna, hesaru |
| 1.4 | Asking for Directions and Finding People | Ask where a place is; understand "go straight" | ellide |
| 2.1 | Speaking Politely to Elders | Greet an elder, say who you are, make a polite request | namaskara, naanu, hosa, svalpa, bagilu, tegeyiri |
| 2.2 | Who Is Here? | Understand a Kannada sentence without English | (understanding only) |
| 2.3 | Asking for Directions and Finding People (reopened) | Reuse *ellide?* for a new object | keeli, ellide |
| 3.1 | Food at the Mess | Accept and order a meal politely | haudu, oota, kodi |
| 3.2 | Food at the Mess (reopened) | Say "enough" | saaku |
| 3.3 | Numbers and Money | Ask a price; recognise *aivattu* (50) | eshtu, rupayi |
| 3.4 | Asking for Directions and Finding People (reopened) | Ask where a person is | elli |

## Vocabulary progression

These counts are by the level where each word first appears.

| Level | Say | Understand | Names |
|---|---|---|---|
| 1 | 17 | 42 | 2 |
| 2 | 4 | 17 | 1 |
| 3 | 2 | 54 | 1 |

Within the MVP, only *haudu* (1.2, 3.1) and *ellide* (1.4, 2.3) are said in two quests. The other "say" words can only meet the "word learned" rule (two different quests) when later chapters reuse them.

## Grammar progression

**Level 1**

- **Wanting things:** *Nanage ___ beku* means "I want ___" (literally "to me, ___ is wanted"). *beda* means "don't want".
- **Yes/no questions:** a long *-aa* turns a statement into a question: *beku → beka?*
- **Saying your name:** *Nanna hesaru ___*. *Nanna* means "my".
- **Asking where:** *___ ellide?* for places and things; *___ elli?* for people.

**Level 2**

- **Politeness:** polite requests (*tegeyiri*) versus the rude short form (*tegi*); *neevu* (polite "you") versus *neenu* (friends only).
- **Being and having:** *illa* means "not here", *ide* means "is", and *avala hatra* means "with her".

**Level 3**

- **Polite asking:** *kodi* means "please give".
- **Enough vs don't want:** *saaku* ("enough") is different from *beda* ("don't want").
- **Prices:** *eshtu* ("how much") with *rupayi*. The notebook gives the numbers needed for money: 1–19, the tens, 100–500, 1,000 and 2,000. Tens and ones join (*ippattaidu* = 25), and *nooru* becomes *noora* before another number (*noora aivattu* = 150). The quest itself tests *aivattu* (50).

## Learning rules

The full rules are in `content/progression.json` and `content/feedback.json`.

- **Help comes in three levels:** quick hint → open the topic → full example. The quick hint appears by itself after 2 wrong answers. "Need more help?" is offered after 3. The player can always continue.
- **The notebook opens to the quest's topic.** The first time, it shows the whole page. When reopened, it highlights the word needed.
- **Answers are judged on meaning, and any spelling is accepted.** An answer with clear meaning but a small slip (e.g. *Nanage chaha*, missing *beku*) is accepted with a short correction tip. The game never shows "Wrong": for an answer that is not accepted, the NPC reacts naturally, then the quick hint appears as a tip.
- **A word counts as learned** when the player uses it correctly without opening the notebook in two different quests. Recalling a phrase without help earns a "Remembered!" stamp.
