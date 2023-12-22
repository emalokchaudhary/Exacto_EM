import tensorflow as tf
from tensorflow.contrib import slim
import ocr.res2 as resnet_utils

resnet_arg_scope = resnet_utils.resnet_arg_scope

@slim.add_arg_scope
def bottleneck(inputs, depth, depth_bottleneck, stride, rate=1,outputs_collections=None, scope=None):
    with tf.variable_scope(scope, 'bottleneck_v1', [inputs]) as sc:
        depth_in = slim.utils.last_dimension(inputs.get_shape(), min_rank=4)
        if depth == depth_in:
            shortcut = resnet_utils.subsample(inputs, stride, 'shortcut')
        else:
            shortcut = slim.conv2d(inputs, depth, [1, 1], stride=stride,activation_fn=None, scope='shortcut')
        residual = slim.conv2d(inputs, depth_bottleneck, [1, 1], stride=1,scope='conv1')
        residual = resnet_utils.conv2d_same(residual, depth_bottleneck, 3, stride,rate=rate, scope='conv2')
        residual = slim.conv2d(residual, depth, [1, 1], stride=1,activation_fn=None, scope='conv3')
        output = tf.nn.relu(shortcut + residual)
        return slim.utils.collect_named_outputs(outputs_collections, sc.original_name_scope,output)


def resnet_v1(inputs,blocks,num_classes=None,is_training=True,global_pool=True,output_stride=None,include_root_block=True,spatial_squeeze=True,reuse=None,scope=None):
    with tf.variable_scope(scope, 'resnet_v1', [inputs], reuse=reuse) as sc:
        end_points_collection = sc.name + '_end_points'
        with slim.arg_scope([slim.conv2d, bottleneck,
                             resnet_utils.stack_blocks_dense],
                            outputs_collections=end_points_collection):
            with slim.arg_scope([slim.batch_norm], is_training=is_training):
                net = inputs
                if include_root_block:
                    if output_stride is not None:
                        if output_stride % 4 != 0:
                            raise ValueError('The output_stride needs to be a multiple of 4.')
                        output_stride /= 4
                    net = resnet_utils.conv2d_same(net, 64, 7, stride=2, scope='conv1')
                    net = slim.max_pool2d(net, [3, 3], stride=2, scope='pool1')

                    net = slim.utils.collect_named_outputs(end_points_collection, 'pool2', net)

                net = resnet_utils.stack_blocks_dense(net, blocks, output_stride)

                end_points = slim.utils.convert_collection_to_dict(end_points_collection)
                try:
                    end_points['pool3'] = end_points['resnet_v1_50/block1']
                    end_points['pool4'] = end_points['resnet_v1_50/block2']
                except:
                    end_points['pool3'] = end_points['Detection/resnet_v1_50/block1']
                    end_points['pool4'] = end_points['Detection/resnet_v1_50/block2']
                end_points['pool5'] = net
                return net, end_points

resnet_v1.default_image_size = 224

def resnet_v1_50(inputs,
                 num_classes=None,
                 is_training=True,
                 global_pool=True,
                 output_stride=None,
                 spatial_squeeze=True,
                 reuse=None,
                 scope='resnet_v1_50'):
    blocks = [
        resnet_utils.Block('block1', bottleneck, [(256, 64, 1)] * 2 + [(256, 64, 2)]),
        resnet_utils.Block('block2', bottleneck, [(512, 128, 1)] * 3 + [(512, 128, 2)]),
        resnet_utils.Block('block3', bottleneck, [(1024, 256, 1)] * 5 + [(1024, 256, 2)]),
        resnet_utils.Block('block4', bottleneck, [(2048, 512, 1)] * 3)
    ]

    return resnet_v1(inputs, blocks, num_classes, is_training,
                     global_pool=global_pool, output_stride=output_stride,
                     include_root_block=True, spatial_squeeze=spatial_squeeze,
                     reuse=reuse, scope=scope)


resnet_v1_50.default_image_size = resnet_v1.default_image_size

