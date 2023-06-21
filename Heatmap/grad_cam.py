import os
import random

import numpy as np
import json
import torch
from PIL import Image
import matplotlib.pyplot as plt
from torchvision import models
from torchvision import transforms

from Heatmap import my_model
from Heatmap.tools import GradCAM, show_cam_on_image, center_crop_img
from pathlib import Path
from Heatmap.opts import parse_opts
from Heatmap.dataset import get_inference_data
from IPN.spatial_transforms import (Compose, Normalize, Resize, CenterCrop,
                                    CornerCrop, MultiScaleCornerCrop,
                                    RandomResizedCrop, RandomHorizontalFlip,
                                    ToTensor, ScaleValue, ColorJitter,
                                    PickFirstChannels)
from IPN.temporal_transforms import (LoopPadding, TemporalRandomCrop,
                                     TemporalCenterCrop, TemporalEvenCrop,
                                     SlidingWindow, TemporalSubsampling)
from IPN.temporal_transforms import Compose as TemporalCompose


def worker_init_fn(worker_id):
    torch_seed = torch.initial_seed()

    random.seed(torch_seed + worker_id)

    if torch_seed >= 2 ** 32:
        torch_seed = torch_seed % 2 ** 32
    np.random.seed(torch_seed + worker_id)


def json_serial(obj):
    if isinstance(obj, Path):
        return str(obj)


def get_normalize_method(mean, std, no_mean_norm, no_std_norm):
    if no_mean_norm:
        if no_std_norm:
            return Normalize([0, 0, 0], [1, 1, 1])
        else:
            return Normalize([0, 0, 0], std)
    else:
        if no_std_norm:
            return Normalize(mean, [1, 1, 1])
        else:
            return Normalize(mean, std)


def get_mean_std(value_scale, dataset):
    assert dataset in ['activitynet', 'kinetics', '0.5']

    if dataset == 'activitynet':
        mean = [0.4477, 0.4209, 0.3906]
        std = [0.2767, 0.2695, 0.2714]
    elif dataset == 'kinetics':
        mean = [0.4345, 0.4051, 0.3775]
        std = [0.2768, 0.2713, 0.2737]
    elif dataset == '0.5':
        mean = [0.5, 0.5, 0.5]
        std = [0.5, 0.5, 0.5]

    mean = [x * value_scale for x in mean]
    std = [x * value_scale for x in std]

    return mean, std


def get_opt():
    opt = parse_opts()

    if opt.output_topk <= 0:
        opt.output_topk = opt.n_classes

    if opt.inference_batch_size == 0:
        opt.inference_batch_size = opt.batch_size

    opt.arch = '{}-{}'.format(opt.model, opt.model_depth)
    opt.begin_epoch = 1
    opt.mean, opt.std = get_mean_std(opt.value_scale, dataset=opt.mean_dataset)
    opt.n_input_channels = 1
    if opt.input_type == 'flow':
        opt.n_input_channels = 2
        opt.mean = opt.mean[:2]
        opt.std = opt.std[:2]
    return opt


def generator_heatmap(type, img_path, index):
    opt = get_opt()

    model = my_model.generate_model(model_depth=opt.model_depth,
                                    n_classes=opt.n_classes,
                                    n_input_channels=opt.n_input_channels,
                                    shortcut_type=opt.resnet_shortcut,
                                    conv1_t_size=opt.conv1_t_size,
                                    conv1_t_stride=opt.conv1_t_stride,
                                    no_max_pool=opt.no_max_pool,
                                    widen_factor=opt.resnet_widen_factor)
    model.load_state_dict(torch.load("C:\\Users\\86173\\Desktop\\fsdownload\\save_200.pth"))

    target_layers = [model.layer4]

    # load image
    normalize = get_normalize_method(opt.mean, opt.std, opt.no_mean_norm,
                                     opt.no_std_norm)
    spatial_transform = [Resize(opt.sample_size)]
    if opt.inference_crop == 'center':
        spatial_transform.append(CenterCrop(opt.sample_size))
    spatial_transform.append(ToTensor())
    if opt.input_type == 'flow':
        spatial_transform.append(PickFirstChannels(n=2))
    spatial_transform.extend([ScaleValue(opt.value_scale), normalize])
    spatial_transform = Compose(spatial_transform)
    temporal_transform = []
    if opt.sample_t_stride > 1:
        temporal_transform.append(TemporalSubsampling(opt.sample_t_stride))
    temporal_transform.append(
        SlidingWindow(opt.sample_duration, opt.inference_stride))
    temporal_transform = TemporalCompose(temporal_transform)

    inference_data, collate_fn = get_inference_data(
        opt.video_path, opt.annotation_path, opt.dataset, opt.input_type,
        opt.file_type, opt.inference_subset, spatial_transform,
        temporal_transform)
    inference_loader = torch.utils.data.DataLoader(
        inference_data,
        batch_size=opt.inference_batch_size,
        shuffle=False,
        num_workers=opt.n_threads,
        pin_memory=True,
        worker_init_fn=worker_init_fn,
        collate_fn=collate_fn)

    cam = GradCAM(model=model, target_layers=target_layers, use_cuda=False)
    target_category = None

    for i, (inputs, targets) in enumerate(inference_loader):
        break

    assert os.path.exists(img_path), "file: '{}' dose not exist.".format(img_path)
    img = Image.open(img_path).convert('RGB')

    img = np.array(img, dtype=np.uint8)

    grayscale_cam = cam(input_tensor=inputs, target_category=target_category)

    grayscale_cam = grayscale_cam[0, :]

    grayscale_cam_ = grayscale_cam[:, :, type]
    visualization = show_cam_on_image(img.astype(dtype=np.float32) / 255.,
                                      grayscale_cam_,
                                      use_rgb=True)
    plt.imshow(visualization)
    plt.savefig('app/static/heatmaps/' + index)
