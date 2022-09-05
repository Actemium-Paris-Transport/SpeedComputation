import base64
from xml.etree.ElementInclude import include
import numpy as np
from numpy import argmax
import tensorflow as tf


def str2dec(s : str) -> tuple :
    """
    simple function to turn string input (registration number) into a one
    hot-encoded 

    Args :
        s : string 
    return : 
        one-hot-encoded : tuple
    """
   
    s = s.replace("-","")
    # print(s)
    # define universe of possible input values
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    # define a mapping of chars to integers

    char_to_int = dict((c, i) for i, c in enumerate(alphabet))
    int_to_char = dict((i, c) for i, c in enumerate(alphabet))
    # integer encode input data
    integer_encoded = [char_to_int[char] for char in s]
    # print(integer_encoded)
    # one hot encode
    onehot_encoded = list()
    for value in integer_encoded:
        letter = [0 for _ in range(len(alphabet))]
        letter[value] = 1
        onehot_encoded.append(letter)
    # print(onehot_encoded)
    
    return onehot_encoded



def get_sec(time_str):
    """Get seconds from time."""
    h, m, s = time_str.split(':')
    return int(h)  + int(m) / 60 + int(s) / 3600




# the sys give u two matricules , two times and ONE distance !!! review your archi
def infromations (plaque_immatriculation1 : str ,plaque_immatriculation2 : str , passing_time1 : str ,passing_time2 : str, distance : int  ) -> tuple: 

    """
    Here we will give the informations needed for our application

    Args :

    plaque_immatriculation : str
    passing_time : integer
    distance : integer

    Returns : 
    Registration number 1 : tensor
    Registration number 2 : tensor
    passing time 1 : array
    passing time 2 : array
    distance : int
    """

    #First matricule 
    data1 = str2dec(plaque_immatriculation1)
    data_ndarray1 = np.array(data1)
    data_tensor1 = tf.convert_to_tensor(data_ndarray1)
    data_tensor_1  = tf.reshape(data_tensor1, [-1])



    #Second Matricule 
    data2 = str2dec(plaque_immatriculation2)
    data_ndarray2 = np.array(data2)
    data_tensor2 = tf.convert_to_tensor(data_ndarray2)
    data_tensor_2  = tf.reshape(data_tensor2, [-1])

    # data_0 = data_ndarray[0]
    # data_1 = data_ndarray[1]
    # data_2 = data_ndarray[2]
    # data_3 = data_ndarray[3]
    # data_4 = data_ndarray[4]
    # data_5 = data_ndarray[5]
    # data_6 = data_ndarray[6]

    passing_time_h_1 = get_sec(passing_time1)
    passing_time_vect1 = []
    passing_time_vect1.append(passing_time_h_1)


    passing_time_h_2 = get_sec(passing_time2)    
    passing_time_vect2 = []
    passing_time_vect2.append(passing_time_h_2)

    distance_vect = []
    distance = 1/distance
    distance_vect.append(distance)

    return data_tensor_1, data_tensor_2 , passing_time_vect1 , passing_time_vect2, distance_vect
    #return data_0,data_1,data_2,data_3,data_4,data_5,data_6, distance , passing_time_vect