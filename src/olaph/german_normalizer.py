import re
import argparse
from pathlib import Path

number_mappings = {
    "0" : "null",
    "1" : "ein",
    "2" : "zwei",
    "3" : "drei",
    "4" : "vier",
    "5" : "fünf",
    "6" : "sechs",
    "7" : "sieben",
    "8" : "acht",
    "9" : "neun",
    "10" : "zehn",
    "11" : "elf",
    "12" : "zwölf",
    "13" : "dreizehn",
    "14" : "vierzehn",
    "15" : "fünfzehn",
    "16" : "sechzehn",
    "17" : "siebzehn",
    "18" : "achtzehn",
    "19" : "neunzehn",
    "20" : "zwanzig",
    "30" : "dreißig",
    "60" : "sechzig",
    "70" : "siebzig",
    "100" : "einhundert"
}
ordinal_mappings = {
    "1" : "erste",
    "3" : "dritte",
    "7" : "siebte",
    "11" : "elfte",
    "12" : "zwölfte",
    "13" : "dreizehnte",
    "14" : "vierzehnte",
    "15" : "fünfzehnte",
    "16" : "sechzehnte",
    "17" : "siebzehnte",
    "18" : "achtzehnte",
    "19" : "neunzehnte",
}
customs_mappings = {
    "¼" : "ein viertel",
    "½" : "einhalb",
    "¾" : "drei viertel",
}
'''
ordinal_genders = {
    ["diese"] : "te",
    ["als"] : "ter",
    [""] : "tes",
    ["am", "zum", "en", "im", "die", "dieser", "diese", "em"] : "ten",
}
'''
def number_literal(number):
    x_str = str(number)
    if x_str == "1":
        return "eins"
    if x_str in number_mappings:
        return number_mappings[x_str]
    x_str_left = x_str[0]
    x_str_right = x_str[1:].lstrip("0")
    if len(x_str) == 8:
        x_str_left = x_str[0:2]
        x_str_right = x_str[2:].lstrip("0")
        if x_str_right != "":
            return number_literal(x_str_left)+"millionen"+number_literal(x_str_right)
        else:
            return number_literal(x_str_left)+"millionen"
    if len(x_str) == 7:
        x_str_left = x_str[0]
        x_str_right = x_str[1:].lstrip("0")
        if x_str_right != "":
            return number_literal(x_str_left)+"millionen"+number_literal(x_str_right)
        else:
            return number_literal(x_str_left)+"millionen"
    if len(x_str) == 6:
        x_str_left = x_str[0:3]
        x_str_right = x_str[3:].lstrip("0")
        if x_str_right != "":
            return number_literal(x_str_left)+"tausend"+number_literal(x_str_right)
        else:
            return number_literal(x_str_left)+"tausend"
    if len(x_str) == 5:
        x_str_left = x_str[0:2]
        x_str_right = x_str[2:].lstrip("0")
        if x_str_right != "":
            return number_literal(x_str_left)+"tausend"+number_literal(x_str_right)
        else:
            return number_literal(x_str_left)+"tausend"

    if len(x_str) == 4:
        if x_str_right != "":
            if int(number) >= 1200 and int(number) < 2000:
                decade = x_str[2:].lstrip("0")
                if decade != "":
                    return number_literal(x_str[0:2])+"hundert"+number_literal(x_str[2:].lstrip("0"))
                else:
                    return number_literal(x_str[0:2])+"hundert"
            else:
                return number_literal(x_str_left)+"tausend"+number_literal(x_str_right)
        else:
            return number_literal(x_str_left)+"tausend"
    if len(x_str) == 3:
        if x_str_right != "":
            return number_literal(x_str_left)+"hundert"+number_literal(x_str_right)
        else:
            return number_literal(x_str_left)+"hundert"
    if len(x_str) == 2:
        if x_str_right != "":
            return number_literal(x_str_right)+"und"+number_literal(x_str_left+"0")
        else:
            return number_literal(x_str_left) + "zig"
class Normalizer:
    def __init__(self) -> None:
        pass

    def normalize_rationals(self, input_sentence:str):
        rationals = re.findall(r"(\d+[\. ']*\d*,\d+)",input_sentence)
        for rational in rationals:
            number, decimals = rational.split(",")
            normalized_number = self.normalize_integer(number)
            if number == "1":
                normalized_number = normalized_number + "s"
            decimals_list = []
            for decimal in decimals:
                normalized_decimal = self.normalize_integer(decimal)
                if decimal == "1":
                    normalized_decimal = normalized_decimal + "s"
                decimals_list.append(normalized_decimal)
            normalized_rational = normalized_number + " komma " + " ".join(decimals_list)
            input_sentence = re.sub(rational, f" {normalized_rational} ", input_sentence)
        return input_sentence

    def normalize_time(self, input_sentence:str):
        times = re.findall(r"(\d{1,2}[\.:]\d{1,2}(?:( Uhr)?))(?!\d)",input_sentence)

        if not len(times) > 0:
            return input_sentence
        if type(times[0]) is tuple:
            temp_times = []
            for t, _ in times:
                temp_times.append(t)
            times = temp_times
        for time in times:
            hour, minute = time.split()[0].replace(".",":").split(":")
            if len(hour) > 2 or len(minute) > 2:
                print("TOO LONG")
                continue
            if len(hour) == 2 and hour.startswith("0"):
                hour = hour[1]
            hour = self.normalize_integer(hour).capitalize()

            if len(minute) == 2 and minute.startswith("0"):
                minute = minute[1]
            if minute == "0":
                minute = ""
            else:
                minute = " "+self.normalize_integer(minute).capitalize()
            normalized_time = hour + " Uhr" + minute
            input_sentence = re.sub(time, f" {normalized_time} ", input_sentence)

        return input_sentence

    def normalize_date(self, input_sentence:str):
        dates = re.findall(r"(\d{1,2}\.\d{1,2}\.\d{1,4})",input_sentence)
        for date in dates:
            day, month, year = date.split(".")
            sentence_split = input_sentence.split()
            number_idx = sentence_split.index(date)
            if number_idx != 0:
                prev_word = sentence_split[number_idx-1]
                day = self.normalize_single_ordinal(day.lstrip("0"), prev_word)
            else:
                day = self.normalize_single_ordinal(day.lstrip("0"), "")

            month = self.normalize_ordinal(month.lstrip("0"))
            if number_idx != 0:
                prev_word = sentence_split[number_idx-1]
                month = self.normalize_single_ordinal(month.lstrip("0"), prev_word)
            else:
                month = self.normalize_single_ordinal(month.lstrip("0"), "")

            year = self.normalize_integer(year.lstrip("0"))
            normalized_date = " ".join([day, month, year])
            input_sentence = re.sub(date, normalized_date, input_sentence)

        return input_sentence

    def normalize_single_ordinal(self, number, prev_word):
        normalized_number = number

        if len(normalized_number) > 2:
            if normalized_number[-2] == 0 and normalized_number[-1] in ordinal_mappings:
                temp_number = self.normalize_integer(normalized_number[:-2]+"00")
                normalized_number = temp_number + "ste"
            elif normalized_number in ordinal_mappings:
                return ordinal_mappings[normalized_number]
            else:
                normalized_number = self.normalize_integer(normalized_number)+"te"
        elif len(normalized_number) == 2:
            normalized_number = self.normalize_integer(number)
            if int(number) < 20:
                normalized_number += "te"
            else:
                normalized_number+="ste"
        else:
            if normalized_number in ordinal_mappings:
                normalized_number = ordinal_mappings[normalized_number]
            else:
                normalized_number = self.normalize_integer(normalized_number)+"te"
        normalized_number = re.sub(r" +", "", normalized_number)
        #input_sentence = re.sub(number+".", f" {normalized_number} ", input_sentence)
        if prev_word.lower() in ["am", "zum", "dem"] and normalized_number.endswith("e"):
                    normalized_number += "n"
        else:
            if normalized_number.endswith("e"):
                normalized_number += "r"
        return normalized_number

    def normalize_ordinal(self, input_sentence:str):
        #TODO fix ordinals for dates
        ordinals = re.findall(r"([\.]*\d+[\. ']*\d*)\.(?!\d) ",input_sentence)
        for number in ordinals:
            try:
                if input_sentence.endswith(number+"."):
                    continue
            except:
                continue
            normalized_number = number

            if len(normalized_number) > 2:
                if normalized_number[-2] == 0 and normalized_number[-1] in ordinal_mappings:
                    temp_number = self.normalize_integer(normalized_number[:-2]+"00")
                    normalized_number = temp_number + "ste"
                elif normalized_number in ordinal_mappings:
                    return ordinal_mappings[normalized_number]
                else:
                    normalized_number = self.normalize_integer(normalized_number)+"te"
            elif len(normalized_number) == 2:
                normalized_number = self.normalize_integer(number)
                if int(number) < 20:
                    normalized_number += "te"
                else:
                    normalized_number+="ste"
            else:
                if normalized_number in ordinal_mappings:
                    normalized_number = ordinal_mappings[normalized_number]
                else:
                    normalized_number = self.normalize_integer(normalized_number)+"te"
            normalized_number = re.sub(r" +", "", normalized_number)
            #input_sentence = re.sub(number+".", f" {normalized_number} ", input_sentence)
            sentence_split = input_sentence.split()
            try:
                number_idx = sentence_split.index(number+".")
            except:
                return input_sentence
            if number_idx != 0:
                prev_word = sentence_split[number_idx-1]
                if prev_word.lower() in ["am", "zum", "dem", "der"] and normalized_number.endswith("e"):
                    normalized_number += "n"
            else:
                if normalized_number.endswith("e"):
                    normalized_number += "r"

            input_sentence = input_sentence.replace(number+".", f" {normalized_number} ")

        return input_sentence

    def normalize_integer(self, input_sentence:str):
        numbers = re.findall(r"(\d+(?:\.\d+)*)",input_sentence)
        numbers_copy = []
        for number in numbers:
            numbers_split = number
            if " " in number:
                numbers_split = number.split(" ")
                numbers_copy += numbers_split
            else:
                numbers_copy.append(numbers_split)
        numbers = [x for x in numbers_copy if len(x.replace(".", "")) > 0]
        numbers_normalized = []
        for number in numbers:
            if number.strip() == "0":
                numbers_normalized.append((number, "0", "null"))
            elif number[0] == "0":
                normalized_number = ""
                for n in number:
                    normalized_number += f" {number_literal(n)}"
                normalized_number = normalized_number.lstrip()
                input_sentence = input_sentence.replace(number, f" {normalized_number} ")
            else:
                number_cleaned = number.replace(" ","").replace(".", "").replace("'","")
                number = number.strip()

                normalized_number = number_literal(number_cleaned)
                if normalized_number is None:
                    normalized_number = " ".join([number_literal(x) for x in number_cleaned])
                if normalized_number.startswith("eins"):
                    normalized_number = "ein" + normalized_number[4:]
                numbers_normalized.append((number,number_cleaned, normalized_number))
        for number, number_cleaned, normalized_number in sorted(numbers_normalized, key=lambda x : int(x[1]), reverse=True):
            input_sentence=re.sub(number, f" {normalized_number} ", input_sentence)
        return input_sentence

    def normalize_customs(self, input_sentence:str):
        for custom_character in customs_mappings:
            if custom_character in input_sentence:
                input_sentence = input_sentence.replace(" "+custom_character, " "+customs_mappings[custom_character])
                input_sentence = input_sentence.replace(custom_character, " "+customs_mappings[custom_character])
        return input_sentence

    def normalize_percent(self, input_sentence:str):
        numbers = re.findall(r"(\d+%)",input_sentence)
        for number in numbers:
            number_cleaned = number.replace(" ","").replace(".", "").replace("'","")
            number = number.strip()
            normalized_number = number_literal(number_cleaned[:-1]) + " prozent"
            input_sentence=re.sub(number, f" {normalized_number} ", input_sentence)
        return input_sentence

    def normalize(self, input_sentence:str):
        input_sentence = self.normalize_date(input_sentence)
        input_sentence = self.normalize_time(input_sentence)
        input_sentence = self.normalize_percent(input_sentence)
        input_sentence = self.normalize_rationals(input_sentence)
        input_sentence = self.normalize_ordinal(input_sentence)

        input_sentence = self.normalize_integer(input_sentence)
        input_sentence = self.normalize_customs(input_sentence)
        input_sentence = input_sentence.replace("None", "")
        input_sentence = input_sentence.replace("einsund", "einund")
        input_sentence = input_sentence.replace("einshundert", "einhundert")
        input_sentence = input_sentence.replace(" ein s ", " eins ")
        input_sentence = re.sub(r" +", " ", input_sentence).strip()
        return input_sentence

def main():
    parser = argparse.ArgumentParser(description="Normalizer control")

    parser.add_argument("--files", required=True,action="append")
    parser.add_argument("--save_path", required=True)

    args = parser.parse_args()

    normalizer = Normalizer()

    normalized_sentences = []

    for text_file in args.files:
        with open(text_file, encoding="UTF-8") as file:
            lines = file.readlines()
            for line in lines:
                normalized_line = normalizer.normalize(line)
                normalized_sentences.append(normalized_line)
        text_file_name = Path(text_file).name
        with open(args.save_path+text_file_name+"_normalized.txt", "w", encoding="UTF-8") as file:
            file.writelines(normalized_sentences)
        normalized_sentences = []

if __name__ == "__main__":
    normalizer = Normalizer()
    sentence = "13.12.2024"
    sentence_normalized = normalizer.normalize(sentence)
    print(sentence_normalized)
    exit()
    main()