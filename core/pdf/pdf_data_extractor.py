import camelot
from fidel import Transliterate

stream_table = camelot.read_pdf("/home/ramsi/telegram_bot/pdf_file/efayda_Ahmed Gelgelu Dido.pdf", pages = 'all', flavor = 'stream', suppress_stdout=False)
table = stream_table[0].df
data_extracted = {
    'name_english': table[1][1],
    'date_of_birth_greg': table[0][5],
    'date_of_birth_et': table[0][4],
    'sex_am': table[0][7],
    'sex_en': table[0][8],
    'phone_number': table[0][13],
    'region_am': table[1][4],
    'region_en': table[1][5],
    'zone_am': table[1][7],
    'zone_en': table[1][8],
    'woreda_am': table[1][10],
    'woreda_en': table[1][11],
}

transliterator = Transliterate(text=data_extracted['name_english'].lower())
amharic_output = transliterator.transliterate()
data_extracted['name_am'] = amharic_output
print(data_extracted)