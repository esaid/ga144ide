from pyutil import inany, fileoverwrite, filereplace, fileappend

import database


def read_file(File_input):
    with open(File_input, 'r') as f:
        return f.read()

# list bibliotheque
def find_string_in_list(list_, string_found, s_extension):
    # cherche index de string_found dans list_, et retourne la liste des fichiers ( sans string_found )  + s_extension
    # exemple require delay ( index 0 ) require gpio ( index 1 ) , retourne [delay.ga, gpio.ga]
    return list(
        map(lambda s_: (list_[s_].replace(string_found, '').strip() + s_extension),
            [i_ for i_, value_ in enumerate(list_) if inany(value_, string_found, True)]))


def find_all_index_in_list(s, string_found):
    return [index for index in range(len(s)) if s.startswith(string_found, index)]


def creation_dictionnaire(code_bibliotheque_):
    dict_code_bibliotheque = {}
    code_bibli = []
    l1 = find_all_index_in_list(code_bibliotheque_, ": ")
    l2 = find_all_index_in_list(code_bibliotheque_, ";")

    i = 0
    while i < (min(len(l1), len(l2)) - 1):
        # print(l1[i],l1[i+1])
        # print(l2[i], l2[i+1])
        while l1[i + 1] < l2[i]:
            l1.pop(i + 1)
            # print(l1)
        while l2[i + 1] < l1[i + 1]:
            l2.pop(i)
            # print(l2)
        i += 1

    for i in range(len(l1) - 1):
        code_bibli = (code_bibliotheque_[l1[i]:l2[i] + 1])
        cle_code_bibliotheque, code_ = code_bibli.split()[1], code_bibli
        # print(code_bibli)
        dict_code_bibliotheque[cle_code_bibliotheque] = code_bibli.replace(': ', '')
    return dict_code_bibliotheque


def dictionnaire_bibliotheque_total(list_bibliotheque_, directoryBibliotheque_):
    dict_bibliotheque_ = {}
    for ll in list_bibliotheque_:
        code_bibliotheque__ = read_file(directoryBibliotheque_ + ll)

        # code_bibliotheque__ = read_file_from_database(f"{ll}")
        dict_bibliotheque_.update(creation_dictionnaire(code_bibliotheque__))
        # print(f"code_bibliotheque {code_bibliotheque__}")
    return dict_bibliotheque_


def code_to_add_to_replace(list_code_, dict_bibliotheque_):
    code_to_add_ = []
    code_to_replace_ = []
    for lc in list_code_:

        if lc in dict_bibliotheque_:
            if lc not in code_to_add_:
                code_to_add_.extend([lc, ': ' + dict_bibliotheque_[lc]])
                # print(lc)

        for key, value in dict_bibliotheque_.items():
            if inany(lc, key):
                if (key not in code_to_replace_) and (key not in code_to_add_):
                    code_to_replace_.extend([key, str(value.removeprefix(key)).replace(';', '')])
    # clean code_to_replace
    code_to_add_ = code_to_add_[1::2]  # odd element
    return code_to_add_, code_to_replace_


def extraction_code(code_):
    # liste_code , separation des lignes , suppression espaces
    list_code = list(filter(lambda x: x != '', list(map(str.strip, code_.splitlines()))))  # separation lignes
    # list_code = list(filter(lambda x: x != '', list(map(str.strip, code.split()))))
    # print(f"list_code:  {list_code}")
    list_node = find_string_in_list(list_code, 'node', '')
    # print(f"liste node : {list_node}")
    return list_code


def creation_bibliotheque(list_code_, directoryBibliotheque_):
    # liste fichier bibliotheque
    list_bibliotheque = find_string_in_list(list_code_, 'require', '.ga')
    # print(f"list_bibliotheque : {list_bibliotheque}")
    # dictionnaire
    dict_bibliotheque = dictionnaire_bibliotheque_total(list_bibliotheque, directoryBibliotheque_)
    # print(f"dictionnaire_bibliotheque {dict_bibliotheque}")
    return dict_bibliotheque


def code_manipulation(list_code_, dict_bibliotheque_, code, file_ga_):
    # code a ajouter a la fin ou a remplacer
    # la regle est la suivante
    # code a ajouter si le mot est seul dans le code exemple pause ( dans ledpulse.ga )
    # code a remplacer si le mot dans le code a un commentaire exemple io.h \ led on  ( dans ledpulse.ga )
    code_to_add, code_to_replace = code_to_add_to_replace(list_code_, dict_bibliotheque_)
    # init code
    fileoverwrite(file_ga_, code)
    # clean require
    filereplace(file_ga_, 'require', '\ require')

    # ajout code complet a la fin
    for s_code_to_add in code_to_add:
        fileappend(file_ga_, s_code_to_add + '\n')

    # remplace la definition du code par sa definition
    for i in range(len(code_to_replace) - 1, -1, -2):
        s_code_to_found = code_to_replace[i - 1]
        s_code_to_replace = code_to_replace[i]
        filereplace(file_ga_, ' ' + s_code_to_found, s_code_to_replace)

    # print(f"code a ajouter : {code_to_add}")
    # print(f"code a remplacer: {code_to_replace}")


def generation_code(code, directoryBibliotheque, file_ga_):
    code_manipulation(extraction_code(code), creation_bibliotheque(extraction_code(code), directoryBibliotheque), code,
                      file_ga_)
