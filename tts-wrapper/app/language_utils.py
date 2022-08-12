from iso639 import Lang

macrolanguage_map = {"aao": "ara",
                "abh": "ara",
                "abv": "ara",
                "acm": "ara",
                "acq": "ara",
                "acw": "ara",
                "acx": "ara",
                "acy": "ara",
                "adf": "ara",
                "aeb": "ara",
                "aec": "ara",
                "afb": "ara",
                "ajp": "ara",
                "apc": "ara",
                "apd": "ara",
                "arb": "ara",
                "arq": "ara",
                "ars": "ara",
                "ary": "ara",
                "arz": "ara",
                "auz": "ara",
                "avl": "ara",
                "ayh": "ara",
                "ayl": "ara",
                "ayn": "ara",
                "ayp": "ara",
                "bbz": "ara",
                "pga": "ara",
                "shu": "ara",
                "ssh": "ara"}

def convert_language(language):
    lang = language
    if language in macrolanguage_map:
        lang = macrolanguage_map[language]
    lg = Lang(lang)
    return lg.pt1

def convert_language_config_key(language):
    lang = language.split('_')
    lang_1 = convert_language(lang[0])
    if len(lang) > 1:
        new_lang = lang_1 + "_" + lang[1]
    else:
        new_lang = lang_1
    return new_lang