
from normalizer import normalize_text


def match_structural_rule(quest_id, step_id, text):
    quest_id = str(quest_id).strip()
    step_id = str(step_id).strip()
    text = normalize_text(text)
    words = set(text.split())

    def result(outcome, answer_id="", category="",
               correction="", reaction=""):
        return {
            "outcome": outcome,
            "answer_id": answer_id,
            "error_category": category,
            "correction_type": correction,
            "reaction_id": reaction,
            "confidence": 0.95,
        }

    if not text:
        return None

    # q1_1_a: thank-you expression
    if quest_id == "q1_1" and step_id == "q1_1_a":
        thanks = {
            "dhanyavada", "dhanyavaada", "dhanyavad",
            "dhanyavadagalu", "dhanyawada"
        }
        if words & {"thank", "thanks", "you"} and not words & thanks:
            return result("not_accepted", "", "english_only", "", "r_puzzled")
        if words & thanks:
            return result("accepted", "a_thanks")
        if words & {
            "beku", "beeku", "bekku", "beda", "bedaa",
            "beeda", "namaskar", "namaskara"
        }:
            aid = "e_beku" if words & {"beku", "beeku", "bekku"} else ""
            return result("not_accepted", aid, "wrong_word", "", "r_puzzled")

    # q1_2_a: request for a drink
    if quest_id == "q1_2" and step_id == "q1_2_a":
        if words & {"beda", "bedaa", "beeda"}:
            return result("not_accepted", "e_beda", "beku_beda_mixup", "", "r_manjunatha_shrug")
        if "nimage" in words:
            return result("not_accepted", "", "pronoun_mixup", "", "r_puzzled")
        if words & {"naanu", "nanu"}:
            return result("not_accepted", "", "unclear", "", "r_puzzled")

        drinks = {"chaha", "chaa", "chahaa", "cha", "chai", "tea", "kaapi", "coffee", "neeru", "niru", "neru"}
        requests = {"beku", "beeku", "bekku", "bekuu"}
        if words & drinks and words & requests:
            return result("accepted", "a_tea")

        if text in {
            "nanage chaha", "nanage chai", "nanege chaha",
            "chaha", "chahaa", "chaa", "chai", "cha"
        }:
            return result("accepted_with_correction", "a_tea", "", "missing_verb", "")
        if words & {"one", "ek"}:
            return result("not_accepted", "", "unclear", "", "r_puzzled")

    # q1_2_b: yes/no response
    if quest_id == "q1_2" and step_id == "q1_2_b":
        yes = {"haudu", "houdu"}
        no = {"illa", "ila"}
        want = {"beku", "beeku", "bekku", "bekuu"}
        refuse = {"beda", "bedaa", "beeda"}

        if ((words & yes and words & (no | refuse))
                or (words & no and words & want)):
            return result("not_accepted", "", "unclear", "", "r_ask_clarify")
        if words & yes:
            return result("accepted", "a_yes")
        if words & no or words & refuse:
            return result("accepted", "a_no")
        if text in {
            "beku", "beeku", "bekuu", "bekku",
            "nanage beku", "nange beku", "nanege beku", "nanage bekku"
        }:
            return result("accepted", "a_yes")
        if text == "sari":
            return result("accepted_with_correction", "a_yes", "", "use_haudu", "")

    # q1_3_a: state your name
    if quest_id == "q1_3" and step_id == "q1_3_a":
        names = {"arun", "aditi", "ravi"}
        if words & {"nima", "nimma", "nimage"}:
            return result("not_accepted", "", "pronoun_mixup", "", "r_puzzled")
        if words & {"naanu", "nanu"} and words & {"hesaru", "hesru"}:
            return result("not_accepted", "", "pronoun_mixup", "", "r_puzzled")
        if words & {"nanna", "nana"} and words & {"hesaru", "hesru"} and words & names:
            return result("accepted", "a_name")
        if words & {"naanu", "nanu"} and words & names and not words & {"hesaru", "hesru"}:
            return result("accepted", "a_name")
        if text in names:
            return result("accepted", "a_name")
        if words & {"hesaru", "hesru"} and not words & names:
            return result("not_accepted", "", "incomplete_answer", "", "r_puzzled")

    # q1_4_a: ask where the library is
    if quest_id == "q1_4" and step_id == "q1_4_a":
        places = {"library", "granthalaya"}
        location_words = {"ellide", "elide", "yellide", "elli", "yelli", "eli"}
        if words & {"bus", "nildana", "aaspatre"}:
            return result("not_accepted", "", "wrong_word", "", "r_puzzled")
        if words & places and words & location_words:
            if words & {"ellide", "elide", "yellide"}:
                return result("accepted", "a_library")
            return result("accepted_with_correction", "a_library", "", "elli_vs_ellide", "")
        if text in {"library", "granthalaya"}:
            return result("not_accepted", "", "incomplete_answer", "", "r_puzzled")

    # q2_1_a: introduce yourself as an archivist
    if quest_id == "q2_1" and step_id == "q2_1_a":
        if words & {"nanage", "nanege", "nange"}:
            return result("not_accepted", "", "pronoun_mixup", "", "r_puzzled")
        if "namaste" in words:
            return result("not_accepted", "", "hindi_word", "", "r_puzzled")

        # These are explicitly accepted in the training data.
        if words & {"naanu", "nanu"} and "archivist" in words:
            return result("accepted", "a_intro")

        if words & {"nanna", "nana"} and words & {"hesaru", "hesru"} and words & {"arun", "aditi"}:
            return result("accepted_with_correction", "a_intro", "", "use_target_pattern", "")

        if words & {"namaskara", "namaskaara", "namaskar"}:
            if words & {"naanu", "nanu"} and "archivist" in words:
                return result("accepted", "a_intro")
            if words & {"nanna", "nana"} and words & {"hesaru", "hesru"} and words & {"arun", "aditi"}:
                return result("accepted_with_correction", "a_intro", "", "use_target_pattern", "")
            if len(words) == 1:
                return result("not_accepted", "", "incomplete_answer", "", "r_puzzled")

    # q2_1_b: politely ask to open the door
    if quest_id == "q2_1" and step_id == "q2_1_b":
        if "tegi" in words:
            return result("not_accepted", "e_tegi", "impolite_form", "", "r_puzzled")
        door = "bagilu" in words
        polite_open = bool(words & {"tegeyiri", "tegeyri", "tegiyiri"})
        if door and polite_open:
            return result("accepted", "a_open")
        if polite_open and not door:
            return result("accepted_with_correction", "a_open", "", "missing_object", "")
        if text in {"bagilu", "svalpa", "svalpaa", "swalpa"}:
            return result("not_accepted", "", "incomplete_answer", "", "r_puzzled")

    # q2_2_a: identify Ananya as the person with the key
    if quest_id == "q2_2" and step_id == "q2_2_a":
        person = {"ananya", "avala", "awala"}
        if words & person and (words & {"ide", "keeli", "hatra"}):
            return result("accepted", "a_ananya")
        if text in {"ananya", "avala", "awala"}:
            return result("accepted", "a_ananya")
        if words & {"somanna", "ravi", "basavaraju", "shanthakka"}:
            return result("not_accepted", "", "wrong_meaning", "", "r_puzzled")
        if words & {"illa", "ila", "ilvala", "ilvalla", "ilwalla"}:
            return result("not_accepted", "", "wrong_meaning", "", "r_puzzled")

    # q3_2_a: say enough / no more
    if quest_id == "q3_2" and step_id == "q3_2_a":
        saaku = {"saaku", "saakku", "sakku", "saku"}
        beda = {"beda", "bedaa", "beeda"}
        no = {"illa", "ila"}
        if words & saaku:
            return result("accepted", "a_saaku")
        if words & beda or words & no:
            return result("accepted_with_correction", "a_beda", "", "saaku_vs_beda", "")


    # q2_3_b: ask where the key is
    if quest_id == "q2_3" and step_id == "q2_3_b":
        key_words = {"keeli", "kili"}
        location_words = {"ellide", "elide", "yellide"}

        if words & {"ananya", "bagilu"}:
            return result("not_accepted", "", "wrong_word", "", "r_puzzled")

        if words & key_words and words & location_words:
            return result("accepted", "a_keeli")

        if words & key_words and words & {"elli", "yelli"}:
            return result(
                "accepted_with_correction", "a_keeli",
                "", "elli_vs_ellide", ""
            )

        if words & {"keeli", "kili"} and len(words) == 1:
            return result(
                "not_accepted", "", "incomplete_answer", "", "r_puzzled"
            )

    # q3_1_a: request a meal
    if quest_id == "q3_1" and step_id == "q3_1_a":
        meal_words = {"oota", "uta", "anna", "ana", "idli"}
        request_words = {"kodi", "beku", "beeku", "bekuu", "bekku"}
        yes_words = {"haudu", "houdu"}

        # Contradictory requests are rejected.
        if words & yes_words and words & {"beda", "bedaa", "beeda"}:
            return result(
                "not_accepted", "", "unclear", "", "r_ask_clarify"
            )

        if words & meal_words and words & request_words:
            return result("accepted", "a_meal")

        if words & yes_words and words & meal_words:
            return result("accepted", "a_meal")

        if words & yes_words and words & {"oota", "uta"}:
            return result("accepted", "a_meal")

        # "Haudu, oota" is a supported partial answer.
        if words & yes_words and words & {"oota", "uta"}:
            return result(
                "accepted_with_correction", "a_meal",
                "", "missing_verb", ""
            )

        if words & meal_words and words & {"beda", "bedaa", "beeda"}:
            return result(
                "not_accepted", "", "valid_other_answer", "", "r_puzzled"
            )

    # q3_3_a: ask how much something costs
    if quest_id == "q3_3" and step_id == "q3_3_a":
        price_words = {"rupayi", "rupaayi", "rupai"}
        how_many_words = {"eshtu", "estu", "yeshtu", "yestu"}

        if words & {"aivathu", "aivattu", "aiwattu", "hattu", "hatu"}:
            return result("not_accepted", "", "wrong_word", "", "r_puzzled")

        if words & how_many_words:
            if words & {"idu", "oota", "uta", "rupayi", "rupaayi", "rupai"}:
                return result("accepted", "a_price")
            if len(words) == 1:
                return result("accepted", "a_price")

        if words & price_words and not words & how_many_words:
            return result(
                "not_accepted", "", "incomplete_answer", "", "r_puzzled"
            )

    # q3_4_a: ask where Ananya is
    if quest_id == "q3_4" and step_id == "q3_4_a":
        location_words = {"elli", "eli", "yelli"}
        complete_location_words = {"ellide", "elide", "yellide"}

        if words & {"basavaraju", "ravi"}:
            return result("not_accepted", "", "wrong_word", "", "r_puzzled")

        if "ananya" in words and words & location_words:
            return result("accepted", "a_where")

        if "ananya" in words and words & complete_location_words:
            return result(
                "accepted_with_correction", "a_where",
                "", "elli_vs_ellide", ""
            )


    # q1_2_a fallback: accept common tea-request spelling variants
    if quest_id == "q1_2" and step_id == "q1_2_a":
        if words & {"beda", "bedaa", "beeda"}:
            return result(
                "not_accepted", "e_beda",
                "beku_beda_mixup", "", "r_manjunatha_shrug"
            )
        if words & {"nimage", "nimge"}:
            return result(
                "not_accepted", "", "pronoun_mixup", "", "r_puzzled"
            )
        if words & {"naanu", "nanu"}:
            return result(
                "not_accepted", "", "unclear", "", "r_puzzled"
            )

        tea_words = {"chaha", "chaa", "chahaa", "cha", "chai"}
        request_words = {"kodi", "beku", "beeku", "bekku", "bekuu"}

        if words & tea_words and words & request_words:
            return result("accepted", "a_tea")

    return None

def diagnose_unmatched_answer(quest_id, step_id, text):
    """Conservative, quest-specific diagnostics for unmatched answers."""
    text = normalize_text(text)
    words = set(text.split())

    if not text:
        return None

    def diagnostic(category, answer_id="", reaction="r_puzzled"):
        return {
            "error_category": category,
            "answer_id": answer_id,
            "reaction_id": reaction,
        }

    q = str(quest_id).strip()
    s = str(step_id).strip()

    # Generic fallback examples.
    if q == "ALL" and s == "ALL":
        if words & {
            "this", "is", "difficult", "hello", "thanks",
            "thank", "please", "where", "what", "price",
            "the", "meal", "open", "gate", "key", "my", "name"
        }:
            return diagnostic("english_only")
        return None

    # q1_1_a: thank-you expression.
    if (q, s) == ("q1_1", "q1_1_a"):
        if words & {"shukriya", "shukria"}:
            return diagnostic("hindi_word")
        if words & {"thank", "thanks"}:
            if words & {
                "dhanyavada", "dhanyavaada", "dhanyavad",
                "dhanyavadagalu", "dhanyawada"
            }:
                return None
            return diagnostic("english_only")
        if words & {
            "naana", "nana", "nanna", "hesaru", "hesru",
            "aditi", "arun", "ravi"
        }:
            return diagnostic("wrong_word")
        if words & {
            "haudu", "houdu", "illa", "ila", "sari",
            "beku", "beeku", "bekku", "beda", "bedaa",
            "beeda", "chaha", "cha", "chaa", "namaskara",
            "namaskar"
        }:
            aid = "e_beku" if words & {"beku", "beeku", "bekku"} else ""
            return diagnostic("wrong_word", aid)

    # q1_2_a: request for a drink.
    if (q, s) == ("q1_2", "q1_2_a"):
        if words & {"nimage", "nimge"}:
            return diagnostic("pronoun_mixup")
        if words & {"beda", "bedaa", "beeda"}:
            return diagnostic(
                "beku_beda_mixup", "e_beda", "r_manjunatha_shrug"
            )
        if words & {"haudu", "houdu", "illa", "ila"}:
            return diagnostic("wrong_meaning")
        if words & {"nana", "nanna", "hesaru", "hesru", "arun"}:
            return diagnostic("wrong_meaning")
        if words & {"i", "want", "tea", "please", "one"}:
            return diagnostic("english_only")
        if words & {"ek", "mujhe", "chahiye", "chai"}:
            return diagnostic("hindi_word")
        if words & {"naanu", "nanu"}:
            return diagnostic("pronoun_mixup")
        if words & {"beka"}:
            return diagnostic("wrong_word")

    # q1_2_b: yes/no response.
    if (q, s) == ("q1_2", "q1_2_b"):
        if words & {"haan", "nahi", "chahiye", "pani"}:
            return diagnostic("hindi_word")
        if words & {"yes", "no", "thanks", "thank", "please"}:
            return diagnostic("english_only")
        if words & {"nana", "nanna", "hesaru", "hesru", "arun"}:
            return diagnostic("wrong_meaning")
        if (
            words & {"haudu", "houdu"}
            and words & {"beda", "bedaa", "beeda", "illa", "ila"}
        ) or (
            words & {"illa", "ila"}
            and words & {"beku", "beeku", "bekku", "bekuu"}
        ):
            return diagnostic("unclear", reaction="r_ask_clarify")
        if (
            words & {"chaha", "chahaa", "cha", "chaa", "tea", "coffee", "kaapi"}
            and words & {"beku", "beeku", "bekku", "bekuu"}
        ):
            return diagnostic("wrong_meaning")

    # q1_3_a: state your name.
    if (q, s) == ("q1_3", "q1_3_a"):
        if words & {"my", "name", "am", "is"}:
            return diagnostic("english_only")
        if words & {"mera", "naam", "main", "hai"}:
            return diagnostic("hindi_word")
        if words & {"nima", "nimma", "nimage", "nimge"}:
            return diagnostic("pronoun_mixup")
        if words & {"hesaru", "hesru"} and not words & {"arun", "aditi", "ravi"}:
            return diagnostic("incomplete_answer")
        if words & {"nana", "nanna"} and not words & {"hesaru", "hesru"}:
            return diagnostic("incomplete_answer")
        if words & {"enu", "yenu"}:
            return diagnostic("wrong_meaning")
        if words & {"beku", "beeku", "bekku", "chaha", "cha"}:
            return diagnostic("wrong_meaning")

    # q1_4_a: ask where the library is.
    if (q, s) == ("q1_4", "q1_4_a"):
        if words & {"where", "library"}:
            return diagnostic("english_only")
        if words & {"mane"}:
            return diagnostic("wrong_word")

    # q2_1_a: archivist introduction.
    if (q, s) == ("q2_1", "q2_1_a"):
        if words & {"hello", "hi", "hey"}:
            return diagnostic("english_only")
        if words & {"nanage", "nange"} and words & {
            "chaha", "cha", "beku", "beeku", "bekku"
        }:
            return diagnostic("wrong_word")

    # q2_1_b: gate-related step.
    if (q, s) == ("q2_1", "q2_1_b"):
        if words & {"open", "gate", "please"}:
            return diagnostic("english_only")
        if words & {"bagilu", "kodi"}:
            return diagnostic("wrong_word")

    # q2_2_a: key-related step.
    if (q, s) == ("q2_2", "q2_2_a"):
        if words & {"bagilu", "manjunatha"}:
            return diagnostic("wrong_meaning")

    # q2_3_b: key location.
    if (q, s) == ("q2_3", "q2_3_b"):
        if words & {"key", "where"}:
            return diagnostic("english_only")
        if words & {"keeli", "kili"}:
            return diagnostic("wrong_word")

    # q3_1_a: meal/order-related step.
    if (q, s) == ("q3_1", "q3_1_a"):
        if words & {"namaskaara", "namaskar", "namaskara"}:
            return diagnostic("wrong_word")
        if words & {"yes", "meal", "please", "thanks", "thank"}:
            return diagnostic("english_only")
        if words & {"khana", "chahiye"}:
            return diagnostic("hindi_word")
        if words & {"rupayi", "rupaayi", "eshtu", "estu"}:
            return diagnostic("valid_other_answer")
        if words & {"illa"} and words & {"beda", "bedaa", "beeda"}:
            return diagnostic("valid_other_answer")

    # q3_2_a: additional-order step.
    if (q, s) == ("q3_2", "q3_2_a"):
        if words & {"no", "thanks"}:
            return diagnostic("english_only")
        if words & {"nahi", "chahiye"}:
            return diagnostic("hindi_word")
        if words & {"haudu"} and words & {"innu", "inu", "beku", "beeku"}:
            return diagnostic("valid_other_answer")

    # q3_3_a: price question.
    if (q, s) == ("q3_3", "q3_3_a"):
        if words & {"what", "is", "the", "price"}:
            return diagnostic("english_only")
        if words & {"kitna", "hua"}:
            return diagnostic("hindi_word")
        if words & {"oota", "uta"}:
            return diagnostic("wrong_word")

    # q3_3_b: number/price response.
    if (q, s) == ("q3_3", "q3_3_b"):
        if words & {
            "aravattu", "aravatu", "arawattu",
            "nooru", "noru", "nuru"
        } or text in {"10", "100"}:
            return diagnostic("wrong_number")

    # q3_4_a: ask where Ananya is.
    if (q, s) == ("q3_4", "q3_4_a"):
        if words & {"where"} and words & {"ananya"}:
            return diagnostic("english_only")
        if words & {"keeli", "kili"}:
            return diagnostic("wrong_word")

    return None
