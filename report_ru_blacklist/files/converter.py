# -*- coding: cp1251 -*-
# the main code is lost


import json
from Country import country


def main():
    with open("new_json.json", "r", encoding="utf-8") as read_file:
        data = json.load(read_file)
    c = len(data.keys())
    print(f'�������� � ����������� ������� �����{c}')

    answer = dict()

    counter = 0
    count = 0
    for item in data.values():
        count += 1
        if item[2] == '49.4542,11.0775':
            key_org = country[item[1]]
            value_org = item[3]['org']
        else:
            key_org = country[item[2]]
            value_org = item[3]['org']
        for k, v in value_org.items():
            counter += v
            try:
                if answer[key_org]:
                    try:
                        if answer[key_org][k]:
                            answer[key_org][k] += v
                        else:
                            answer[key_org][k] = v
                    except KeyError:
                        answer[key_org][k] = v
                else:
                    answer[key_org] = {k: v}
            except KeyError:
                answer[key_org] = {k: v}

    print(f'��� �������� � JSON �����{counter}')
    print(f'������ � �����{len(answer.keys())}')
    count = 0
    for item in answer.values():
        for k, v in item.items():
            count += v
            print(k, v)
    print(f'��� �������� � �������� � �������� ���� {count}')

    with open('data_json.json', 'w', encoding="utf-8") as json_file:
        json.dump(answer, json_file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
