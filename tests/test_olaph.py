import pytest
from olaph import Olaph  # adjust this import to your actual module

phonemizer = Olaph()

@pytest.mark.parametrize("graphemes, phonemes", [
    ("Spielen wir wieder Kriegsspiele?", "ˈʃpiːlən viːɐ̯ ˈviːdɐ ˈkʁiːksˌʃpiːlə?"),
    ("Das Backend war noch nicht fertig und ich war schon in der Küche backend.", "das bˈækˈɛnd vaːɐ̯ nɔx nɪçt ˈfɛʁtɪk ʊnt ɪx vaːɐ̯ ʃoːn ɪn deːɐ̯ ˈkyːçə ˈbakn̩t."),
])
def test_german(graphemes, phonemes):
    assert phonemizer.phonemize_text(graphemes, lang="de") == phonemes

@pytest.mark.parametrize("graphemes, phonemes", [
    ("The farm will produce fresh vegetables.", "ðə fˈɑːm wˈɪl pɹəˈdus fɹˈɛʃ vˈɛd‍ʒɪtəbə‍lz."),
    ("The produce section is over there.", "ðə ˈpɹoʊdus sˈɛkʃən ˈɪz ˈə‍ʊvɐ ðˈe‍ə."),
])
def test_english(graphemes, phonemes):
    assert phonemizer.phonemize_text(graphemes, lang="en") == phonemes

@pytest.mark.parametrize("graphemes, phonemes", [
    ("I have read the agreement, but can you read it to me again?", "ˈaɪ ˈhæv ˈɹɛd ðə ɐɡɹˈiːmənt, bˈʌt kˈæn jˈuː ˈɹid ˈɪt tˈuː mˈiː ɐɡˈɛn?"),
    ("The workers refuse to handle the refuse left outside the factory.", "ðə ˈwɝkɝz ɹɪfˈjuz tˈuː hˈændə‍l ðə ˈɹɛfˌjuz lˈɛft ˈaʊtˈsaɪd ðə fˈæktəɹˌi."),
])
def test_homographs(graphemes, phonemes):
    assert phonemizer.phonemize_text(graphemes, lang="en") == phonemes

@pytest.mark.parametrize("graphemes, phonemes", [
    ("The Oktoberfest in München is a must visit event.", "ðə ɔkˈtoːbɐˌfɛst ˈɪn ˈmʏnçn̩ ˈɪz ˈeɪ mˈʌst vˈɪzɪt ɪvˈɛnt."),
    ("They visited the Museo del Prado in Madrid.", "ðˈe‍ɪ vˈɪzɪtɪd ðə museo ˈdɛɫ ˈpɹɑdoʊ ˈɪn məˈdɹɪd."),
])
def test_cross_lingual(graphemes, phonemes):
    assert phonemizer.phonemize_text(graphemes, lang="en") == phonemes

