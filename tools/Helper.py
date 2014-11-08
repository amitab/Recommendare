def change_range(OldValue, OldMax, OldMin, NewMax, NewMin):
    OldRange = (OldMax - OldMin)
    if OldRange == 0:
        NewValue = NewMin
    else:
        NewRange = (NewMax - NewMin)  
        NewValue = (((OldValue - OldMin) * NewRange) / float(OldRange)) + NewMin

    return NewValue

def build_user_vectors(user1, user2, max_age):

    vector_x = [ change_range(user1['age'], max_age, 0, 1, 0) ]
    vector_y = [ change_range(user2['age'], max_age, 0, 1, 0) ]

    if user1['sex'] == user2['sex']:
        vector_x.extend([1, 0])
        vector_y.extend([1, 0])
    else:
        vector_x.extend([0, 1])
        vector_y.extend([1, 0])

    if user1['zip_code'] == user2['zip_code']:
        vector_x.extend([1, 0])
        vector_y.extend([1, 0])
    else:
        vector_x.extend([0, 1])
        vector_y.extend([1, 0])

    if user1['occupation'] == user2['occupation']:
        vector_x.extend([1, 0])
        vector_y.extend([1, 0])
    else:
        vector_x.extend([0, 1])
        vector_y.extend([1, 0])

    return {
        'user1': vector_x,
        'user2': vector_y
    }