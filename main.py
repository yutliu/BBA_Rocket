import argparse
import train
import test
import eval
from datasets.dataset_dota import DOTA
from datasets.dataset_hrsc import HRSC
from datasets.dataset_rocket import ROCKET
from models import ctrbox_net
import decoder
import os


def parse_args():
    parser = argparse.ArgumentParser(description='BBAVectors Implementation')
    parser.add_argument('--num_epoch', type=int, default=400, help='Number of epochs')
    parser.add_argument('--batch_size', type=int, default=8, help='Number of epochs')
    parser.add_argument('--num_workers', type=int, default=16, help='Number of workers')
    parser.add_argument('--init_lr', type=float, default=1.25e-5, help='Init learning rate')
    parser.add_argument('--input_h', type=int, default=608, help='input height')
    parser.add_argument('--input_w', type=int, default=608, help='input width')
    parser.add_argument('--K', type=int, default=100, help='maximum of objects')
    parser.add_argument('--conf_thresh', type=float, default=0.18, help='confidence threshold')
    parser.add_argument('--ngpus', type=int, default=2, help='number of gpus')
    parser.add_argument('--resume', type=str, default='./weights_rocket/model_warmup_115.pth', help='weights to be resumed')
    parser.add_argument('--loadpth', type=str, default='model_114.pth', help='load weights when test')
    parser.add_argument('--dataset', type=str, default='rocket', help='weights to be resumed')
    parser.add_argument('--data_dir', type=str, default='/home/dl/Data/Rocket/PreliminaryData', help='data directory')
    parser.add_argument('--phase', type=str, default='train', help='data directory')
    parser.add_argument('--wh_channels', type=int, default=8, help='data directory')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    dataset = {'dota': DOTA, 'hrsc': HRSC, 'rocket':ROCKET}
    num_classes = {'dota': 15, 'hrsc': 1, 'rocket':5}
    heads = {'hm': num_classes[args.dataset],
             'wh': 10,
             'reg': 2,
             'cls_theta': 1
             }
    down_ratio = 4
    model = ctrbox_net.CTRBOX(heads=heads,
                              pretrained=True,
                              down_ratio=down_ratio,
                              final_kernel=1,
                              head_conv=256)

    decoder = decoder.DecDecoder(K=args.K,
                                 conf_thresh=args.conf_thresh,
                                 num_classes=num_classes[args.dataset])
    if args.phase == 'train':
        ctrbox_obj = train.TrainModule(dataset=dataset,
                                       num_classes=num_classes,
                                       model=model,
                                       decoder=decoder,
                                       down_ratio=down_ratio)

        ctrbox_obj.train_network(args)
    elif args.phase == 'test':
        ctrbox_obj = test.TestModule(dataset=dataset, num_classes=num_classes, model=model, decoder=decoder)
        ctrbox_obj.test(args, down_ratio=down_ratio)
    else:
        ctrbox_obj = eval.EvalModule(dataset=dataset, num_classes=num_classes, model=model, decoder=decoder)
        ctrbox_obj.evaluation(args, down_ratio=down_ratio)