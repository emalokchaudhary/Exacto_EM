import collections
import tensorflow as tf

slim = tf.contrib.slim

class Block(collections.namedtuple('Block', ['scope', 'unit_fn', 'args'])):
    """
    """

def subsample(inputs, factor, scope=None):
    if factor == 1:
        return inputs
    else:
        return slim.max_pool2d(inputs, [1, 1], stride=factor, scope=scope)

def conv2d_same(inputs, num_outputs, kernel_size, stride, rate=1, scope=None):
    if stride == 1:
        return slim.conv2d(inputs, num_outputs, kernel_size, stride=1, rate=rate,
                           padding='SAME', scope=scope)
    else:
        kernel_size_effective = kernel_size + (kernel_size - 1) * (rate - 1)
        pad_total = kernel_size_effective - 1
        pad_beg = pad_total // 2
        pad_end = pad_total - pad_beg
        inputs = tf.pad(inputs,
                        [[0, 0], [pad_beg, pad_end], [pad_beg, pad_end], [0, 0]])
        return slim.conv2d(inputs, num_outputs, kernel_size, stride=stride,
                           rate=rate, padding='VALID', scope=scope)

@slim.add_arg_scope
def stack_blocks_dense(net, blocks, output_stride=None,   outputs_collections=None):
    current_stride = 1
    rate = 1
    for block in blocks:
        with tf.variable_scope(block.scope, 'block', [net]) as sc:
            for i, unit in enumerate(block.args):
                with tf.variable_scope('unit_%d' % (i + 1), values=[net]):
                    unit_depth, unit_depth_bottleneck, unit_stride = unit
                    if output_stride is not None and current_stride == output_stride:
                        net = block.unit_fn(net, depth=unit_depth,depth_bottleneck=unit_depth_bottleneck,stride=1,rate=rate)
                        rate *= unit_stride
                    else:
                        net = block.unit_fn(net,depth=unit_depth,depth_bottleneck=unit_depth_bottleneck,stride=unit_stride,rate=1)
                        current_stride *= unit_stride
            net = slim.utils.collect_named_outputs(outputs_collections, sc.name, net)
    return net

def resnet_arg_scope(weight_decay=0.0001,batch_norm_decay=0.997,batch_norm_epsilon=1e-5,batch_norm_scale=True):
    batch_norm_params = {'decay': batch_norm_decay,'epsilon': batch_norm_epsilon,'scale': batch_norm_scale,'updates_collections': tf.GraphKeys.UPDATE_OPS,}
    with slim.arg_scope([slim.conv2d],weights_regularizer=slim.l2_regularizer(weight_decay),weights_initializer=slim.variance_scaling_initializer(),activation_fn=tf.nn.relu,normalizer_fn=slim.batch_norm,normalizer_params=batch_norm_params):
        with slim.arg_scope([slim.batch_norm], **batch_norm_params):
            with slim.arg_scope([slim.max_pool2d], padding='SAME') as arg_sc:
                return arg_sc
