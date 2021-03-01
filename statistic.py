import dbworker


def calculate_the_average_score_by_struct(forms: dict) -> list:
    divisor = len(forms[0])
    zero_list = [0] * divisor

    for item in forms:
        counter = 0
        for value in item:
            zero_list[counter] += item[value]
            counter += 1

    questions_mean = []
    for value in zero_list:
        questions_mean.append(round(value / divisor, 1))

    return questions_mean

def normal_distribution_of_answers(forms: dict):
    pass



if __name__ == '__main__':
    x = calculate_the_average_score_by_struct(dbworker.get_all_form_by_struct('Коворкинг "Garaж"'))
    print(x)