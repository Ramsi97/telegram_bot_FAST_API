import camelot
from fidel import Transliterate
from pathlib import Path


def extract_user_data(pdf_path: str | Path, debug: bool = False) -> dict:
    """
    Extract user data from Ethiopian ID PDF using Camelot.
    Converts English name to Amharic using `fidel.Transliterate`.

    Args:
        pdf_path (str | Path): Path to the PDF file.
        debug (bool): Whether to print extracted data for debugging.

    Returns:
        dict: Extracted user information.
    """
    pdf_path = str(pdf_path)

    try:
        # Extract table data from the PDF
        tables = camelot.read_pdf(pdf_path, pages="all", flavor="stream", suppress_stdout=False)
        if len(tables) == 0:
            raise ValueError("No tables found in the PDF.")

        table = tables[0].df

        # Build the data dictionary
        data_extracted = {
            "name_en": table[1][1],
            "date_of_birth_greg": table[0][5],
            "date_of_birth_et": table[0][4],
            "sex_am": table[0][7],
            "sex_en": table[0][8],
            "phone_number": table[0][13],
            "region_am": table[1][4],
            "region_en": table[1][5],
            "zone_am": table[1][7],
            "zone_en": table[1][8],
            "woreda_am": table[1][10],
            "woreda_en": table[1][11],
        }

        # Transliterate English name → Amharic
        try:
            transliterator = Transliterate(text=data_extracted["name_en"].lower())
            data_extracted["name_am"] = transliterator.transliterate()
        except Exception as e:
            data_extracted["name_am"] = ""
            if debug:
                print(f"⚠️ Transliteration failed: {e}")

        if debug:
            print("✅ Extracted Data:")
            for k, v in data_extracted.items():
                print(f"  {k}: {v}")

        return data_extracted

    except Exception as e:
        print(f"❌ Failed to extract data: {e}")
        return {}
