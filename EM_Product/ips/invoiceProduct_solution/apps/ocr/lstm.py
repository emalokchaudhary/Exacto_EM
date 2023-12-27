import os

os.environ["PBR_VERSION"]='3.1.1'

from ocr.config import (batch_size, hidden_neurons, total_classes, num_hidden_layers,dropout)
import tensorflow as tf

class Model:
    def __init__(self, batch_size):
        self.batch_size = batch_size

    def lstm_fw_cell(self):
      cell = tf.contrib.rnn.BasicLSTMCell(hidden_neurons, forget_bias=0.0, state_is_tuple=True, reuse=tf.get_variable_scope().reuse)
      return tf.contrib.rnn.DropoutWrapper(cell, input_keep_prob=dropout)


    def lstm_bw_cell(self):
      cell = tf.contrib.rnn.BasicLSTMCell(hidden_neurons, forget_bias=0.0, state_is_tuple=True, reuse=tf.get_variable_scope().reuse)
      return tf.contrib.rnn.DropoutWrapper(cell, input_keep_prob=dropout)


    def length(self, sequence):
        used = tf.sign(tf.reduce_max(tf.abs(sequence), reduction_indices=2))
        length = tf.reduce_sum(used, reduction_indices=1)
        length = tf.cast(length, tf.int32)
        return length

    def LSTM(self, X, seq_len):
        with tf.variable_scope('LSTM_Layer', reuse=None):

            self.lstm_fw_multicell = tf.contrib.rnn.MultiRNNCell([self.lstm_fw_cell() for _ in range(num_hidden_layers)])
            self.lstm_bw_multicell = tf.contrib.rnn.MultiRNNCell([self.lstm_bw_cell() for _ in range(num_hidden_layers)])

            self.lstm_fw_multicell =  tf.contrib.rnn.DropoutWrapper(self.lstm_fw_multicell, output_keep_prob=dropout)
            self.lstm_bw_multicell =  tf.contrib.rnn.DropoutWrapper(self.lstm_bw_multicell, output_keep_prob=dropout)

            #self.lstm_fw_cell = tf.contrib.rnn.LSTMCell(hidden_neurons/2,state_is_tuple=True)
            #self.lstm_bw_cell = tf.contrib.rnn.LSTMCell(hidden_neurons/2,state_is_tuple=True)
            #self.lstm_cell = tf.nn.rnn_cell.LSTMCell(hidden_neurons, state_is_tuple=True)

            self.output,_ = tf.nn.bidirectional_dynamic_rnn(self.lstm_fw_multicell,self.lstm_bw_multicell,X,seq_len,dtype=tf.float32)

            self.output = tf.concat(self.output,axis=2)

            self.stack_cell = tf.contrib.rnn.MultiRNNCell([tf.contrib.rnn.LSTMCell(hidden_neurons, state_is_tuple=True) for _ in range(2)],state_is_tuple=True)

            self.Y,last_state = tf.nn.dynamic_rnn(self.stack_cell,self.output,seq_len,dtype=tf.float32)

            #self.Y, _ = tf.nn.dynamic_rnn(self.lstm_cell, X, seq_len, dtype=tf.float32)
            shape = tf.shape(X)
            batch_size_i, max_timesteps = shape[0], shape[1]
            self.Y = tf.reshape(self.Y, [-1, hidden_neurons])
            with tf.name_scope("weights"):
                self.W = tf.get_variable("W", shape=[hidden_neurons,total_classes],initializer=tf.contrib.layers.xavier_initializer())
                #self.W = tf.get_variable("W", shape=[hidden_neurons,total_classes], dtype=tf.float32, initializer=None,regularizer=None, trainable=True, collections=None)
                #self.W = tf.Variable(tf.truncated_normal([hidden_neurons,total_classes],stddev=0.1), name="W")
            with tf.name_scope("biases"):
                #self.b = tf.get_variable("b", shape=[total_classes],initializer=tf.contrib.layers.xavier_initializer())
                self.b = tf.Variable(tf.constant(0., shape=[total_classes]), name="b")
            with tf.name_scope("logits"):
                self.logits = tf.transpose(tf.reshape((tf.matmul(self.Y, self.W) + self.b), [batch_size_i, -1, total_classes]), (1, 0, 2), name='logits')
        return self.logits, self.W, self.b
    
    # def conv_single(self, input, k_h, k_w, c_o, s_h, s_w, name, c_i=None, biased=True,relu=True, padding=DEFAULT_PADDING, trainable=True):
    #         """ contribution by miraclebiu, and biased option"""
    #         self.validate_padding(padding)
    #         if not c_i: c_i = input.get_shape()[-1]
    #         if c_i==1: input = tf.expand_dims(input=input,axis=3)
    #         convolve = lambda i, k: tf.nn.conv2d(i, k, [1,s_h, s_w, 1], padding=padding)
    #         with tf.variable_scope(name) as scope:
    #             init_weights = tf.contrib.layers.xavier_initializer()
    #             init_biases = tf.constant_initializer(0.0)
    #             kernel = self.make_var('weights', [k_h, k_w, c_i, c_o], init_weights, trainable, \
    #                                    regularizer=self.l2_regularizer(cfg.TRAIN.WEIGHT_DECAY))
    #             if biased:
    #                 biases = self.make_var('biases', [c_o], init_biases, trainable)
    #                 conv = convolve(input, kernel)
    #                 if relu:
    #                     bias = tf.nn.bias_add(conv, biases)
    #
    #                     return tf.nn.relu(bias)
    #                 return tf.nn.bias_add(conv, biases)
    #             else:
    #                 conv = convolve(input, kernel)
    #                 if relu:
    #                     return tf.nn.relu(conv)
    #                 return conv
