import math

def cosine_similarity(vector_x, vector_y):
    dot_pdt = 0
    length_x = 0
    length_y = 0

    for i in range(len(vector_x)):
        dot_pdt += vector_x[i] * vector_y[i]
        length_x += vector_x[i] ** 2
        length_y += vector_y[i] ** 2

    length_x = math.sqrt(length_x)
    length_y = math.sqrt(length_y)
    den = length_x * length_y

    if den == 0:
        return 0
    else:
        return dot_pdt / float(den)

def deviation(vector_x, vector_y, card_x_y):
    deviation = 0

    for i in range(len(vector_x)):
        num = vector_x[i] - vector_y[i]
        deviation += num / float(card_x_y)

    return deviation