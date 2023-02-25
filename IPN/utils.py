import csv
import random
from functools import partialmethod

import torch
import numpy as np
from sklearn.metrics import precision_recall_fscore_support


class AverageMeter(object):
    """Computes and stores the average and current value"""

    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


class Logger(object):

    def __init__(self, path, header):
        self.log_file = path.open('w')
        self.logger = csv.writer(self.log_file, delimiter='\t')

        self.logger.writerow(header)
        self.header = header

    def __del(self):
        self.log_file.close()

    def log(self, values):
        write_values = []
        for col in self.header:
            assert col in values
            write_values.append(values[col])

        self.logger.writerow(write_values)
        self.log_file.flush()


def calculate_accuracy(outputs, targets):
    with torch.no_grad():
        batch_size = targets.size(0)

        _, pred = outputs.topk(1, 1, largest=True, sorted=True)
        pred = pred.t()
        correct = pred.eq(targets.view(1, -1))
        n_correct_elems = correct.float().sum().item()

        return n_correct_elems / batch_size


def calculate_precision_and_recall(outputs, targets, pos_label=1):
    with torch.no_grad():
        _, pred = outputs.topk(1, 1, largest=True, sorted=True)
        precision, recall, _, _ = precision_recall_fscore_support(
            targets.view(-1, 1).cpu().numpy(),
            pred.cpu().numpy())

        return precision[pos_label], recall[pos_label]


def worker_init_fn(worker_id):
    torch_seed = torch.initial_seed()

    random.seed(torch_seed + worker_id)

    if torch_seed >= 2**32:
        torch_seed = torch_seed % 2**32
    np.random.seed(torch_seed + worker_id)


def get_lr(optimizer):
    lrs = []
    for param_group in optimizer.param_groups:
        lr = float(param_group['lr'])
        lrs.append(lr)

    return max(lrs)


def partialclass(cls, *args, **kwargs):

    class PartialClass(cls):
        __init__ = partialmethod(cls.__init__, *args, **kwargs)

    return PartialClass



def dropout_layer(X,dropout):
    #dropout范围在[0,1]之间
    assert 0<=dropout<=1
    #dropout = 1指把输出层所有元素都丢掉
    if dropout == 1:
        return torch.zeros_like(X)
    # dropout = 0指把输出层所有元素都保留，不丢掉
    if dropout ==0:
        return X
    #zero_one_X = torch.randn(X.shape)按照X尺寸维数大小按照正态分布随机生成0到1之间的元素所组成的矩阵，然后与dropout比较大小得到的bool值True,False，然后转换成浮点数，对应1,0值
    zero_one_X = torch.randn(X.shape)
    #print("zero_one_X = ",zero_one_X)
    mask = (zero_one_X > dropout).float()
    # mask = (torch.rand(X.shape) > dropout).float()#与上面两行代码等价
    #print("mask ：",mask)
    #mask矩阵和X矩阵对应元素相乘再除以(1-dropout)，保证使用dropout后保证每一层使用dropout后的输出层元素期望均值不变
    return mask * X /(1-dropout) 