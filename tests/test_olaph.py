import pytest
from olaph import Olaph

phonemizer = Olaph()

@pytest.mark.parametrize("graphemes, phonemes", [
    ("Spielen wir wieder Kriegsspiele?", "ˈʃpiːlən viːɐ̯ ˈviːdɐ ˈkʁiːksˌʃpiːlə?"),
    ("Das Backend war noch nicht fertig und ich war schon in der Küche backend.", "das bˈækˈɛnd vaːɐ̯ nɔx nɪçt ˈfɛʁtɪk ʊnt ɪç vaːɐ̯ ʃoːn ɪn deːɐ̯ ˈkyːçə ˈbakn̩t."),
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
    ("I have read the agreement, but can you read it to me again?", "ˈaɪ ˈhæv ˈɹɛd ði ɐɡɹˈiːmənt, bˈʌt kˈæn jˈuː ˈɹid ˈɪt tˈuː mˈiː ɐɡˈɛn?"),
    ("The workers refuse to handle the refuse left outside the factory.", "ðə ˈwɝkɝz ɹɪfˈjuz tˈuː hˈændə‍l ðə ˈɹɛfˌjuz lˈɛft ˈaʊtˈsaɪd ðə fˈæktəɹˌi."),
])
def test_homographs(graphemes, phonemes):
    assert phonemizer.phonemize_text(graphemes, lang="en") == phonemes

@pytest.mark.parametrize("graphemes, phonemes", [
    ("The Oktoberfest in München is a must visit event.", "ði ɔkˈtoːbɐˌfɛst ˈɪn ˈmʏnçn̩ ˈɪz ə mˈʌst vˈɪzɪt ɪvˈɛnt."),
    ("They visited the Museo del Prado in Madrid.", "ðˈe‍ɪ vˈɪzɪtɪd ðə museo ˈdɛɫ ˈpɹɑdoʊ ˈɪn məˈdɹɪd."),
])
def test_cross_lingual(graphemes, phonemes):
    assert phonemizer.phonemize_text(graphemes, lang="en") == phonemes

@pytest.mark.parametrize("graphemes, phonemes", [
    ("das Finalfeld wurde von den neun nächstplatzierten übernommen.", "das fiˈnaːlfɛlt ˈvʊʁdə fɔn deːn nɔɪ̯n nɛːçstplaˈt͡siːɐ̯tn̩ ˈyːbɐˌnɔmən."),
    ("Der Verwaltungssitz befindet sich in Botswana.", "deːɐ̯ fɛɐ̯ˈvaltʊŋszɪt͡s bəˈfɪndət zɪç ɪn bɔˈt͡svaːna."),
])
def test_probability_scoring(graphemes, phonemes):
    assert phonemizer.phonemize_text(graphemes, lang="de") == phonemes



@pytest.mark.parametrize("graphemes, phonemes", [
    ("Don't touch the driver’s radio at eight o’clock unless you’re ready for some loud rock’n’roll.", "ˈdoʊnt tˈʌt‍ʃ ðə ˈdɹaɪvɝz ɹˈe‍ɪdɪˌə‍ʊ ˈæt ˈe‍ɪt əˈklɒk ʌnlˈɛs ˈjuɹ ɹˈɛdi fˈɔː sˈʌm lˈa‍ʊd ˈɹɑkənˈɹoʊɫ."),
])
def test_quotation_marks_en(graphemes, phonemes):
    assert phonemizer.phonemize_text(graphemes, lang="en") == phonemes


@pytest.mark.parametrize("graphemes, phonemes", [
    ("Heut' geh’ ich zu Opa’s Garten, weil's dort schön is’, und frag’, ob er’s erlaubt, dass ich sein’n alten Ball nehm’.", "hɔɪ̯t ɡeː ɪç t͡suː ˈoːpas ˈɡ̊aʁtn̩, vaɪ̯ls dɔʁt ʃøːn ɪs, ʊnt fʁaːk, ɔp eːɐ̯s ɛɐ̯ˈlaʊ̯pt, das ɪç ʃeiɲ ˈaltn̩ bal nəhm̩."),
])
def test_quotation_marks_de(graphemes, phonemes):
    assert phonemizer.phonemize_text(graphemes, lang="de") == phonemes

@pytest.mark.parametrize("graphemes, phonemes", [
    ("l'écart entre les dalits et les non dalits augmente depuis le début des années quatre vingt dix consacrant ainsi l'échec des politiques de développement qui trop souvent ignorent le problème.", "lekaʁ ɑ̃tʁ le dali e le nɔ̃ dali ogmɑ̃t dəpɥi lə deby de ane katʁ vɛ̃ dis kɔ̃sakʁɑ̃ ɛ̃si leʃɛk de pɔlitik də devlɔpmɑ̃ ki tʁo suvɑ̃ iɲɔʁ lə pʁɔblɛm."),
])
def test_quotation_marks_fr(graphemes, phonemes):
    assert phonemizer.phonemize_text(graphemes, lang="fr") == phonemes

@pytest.mark.parametrize("graphemes, phonemes", [
    ("Pa’ qué voy a decirte que no, si sé que t’ha’ ido bien y que to’ lo que hiciste fue pa’ mejorar.", "pa ˈke ˈboj a deθiɾte ke no, si ˈse ke ta iðo bjen i ke ˈto lo ke iθiste fwe pa mexoɾaɾ."),
])
def test_quotation_marks_es(graphemes, phonemes):
    assert phonemizer.phonemize_text(graphemes, lang="es") == phonemes


@pytest.mark.parametrize("graphemes, phonemes", [
    ("Er musste laut BGB § 9 Absatz 3 um die 750 € Strafe zahlen.", "eːɐ̯ ˈmʊstə laʊ̯t ˈbeː ˈɡeː ˈbeː paʁaˈɡʁaːf nɔɪ̯n ˈapˌzat͡s dʁaɪ̯ ʊm diː ˈziːbn̩ˌhʊndɐtˈfʏnft͡sɪk ˈɔɪ̯ʁo ˈʃtʁaːfə ˈt͡saːlən."),
])
def test_replacements_de(graphemes, phonemes):
    assert phonemizer.phonemize_text(graphemes, lang="de") == phonemes

@pytest.mark.parametrize("graphemes, lang, expected_refused", [
    # French contractions resolved via splitting in the target-lang dict (no refusal)
    ("L'amour est beau.", "fr", []),
    # "Günter" is a German name not in the French dictionary; the umlaut blocks
    # splitting via single French-dict characters, so it must be refused.
    ("Il a rencontré Günter en Allemagne.", "fr", ["günter"]),
])
def test_no_guessing(graphemes, lang, expected_refused):
    from olaph import NoGuessingRefusal
    o = Olaph()
    o.phonemize_text(graphemes, lang=lang, guessing=False)
    assert sorted(o.refused_words) == sorted(expected_refused)


def test_cross_language_default_result():
    # "L'argent" was previously looked up as "largent" in the cross-language dict,
    # returning the English IPA for "largent" instead of the correct French IPA.
    # With source-aware lookups, the English entry is skipped and OLaPh correctly
    # splits "largent" -> "l" + "argent" using the French dictionary.
    o = Olaph()
    assert o.phonemize_text("L'argent", lang="fr") == "laʁʒɑ̃."
