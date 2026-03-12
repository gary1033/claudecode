from test_case_reader import SimplePOSTagger


def test_verb_tagging():
    assert SimplePOSTagger.tag_word("launch") == "VERB"
    assert SimplePOSTagger.tag_word("click") == "VERB"


def test_noun_tagging():
    assert SimplePOSTagger.tag_word("browser") == "NOUN"
    assert SimplePOSTagger.tag_word("button") == "NOUN"


def test_preposition_tagging():
    assert SimplePOSTagger.tag_word("in") == "PREP"
    assert SimplePOSTagger.tag_word("on") == "PREP"


def test_tokenize_and_tag():
    result = SimplePOSTagger.tokenize_and_tag("launch browser")
    assert result == [("launch", "VERB"), ("browser", "NOUN")]
