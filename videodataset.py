import json
from pathlib import Path

import torch
import torch.utils.data as data
import torchvision

from .loader import VideoLoader

people = [10001, 10004, 10005, 10007, 10009, 10010, 10013, 10014, 10016, 10017, 10021, 10024, 10025, 10026, 10029,
          10032,
          10034, 10035, 10036, 10037, 10038, 10039, 10040, 10041, 10042, 10043, 10044, 10045, 10048, 10049, 10050,
          10052,
          10053, 10054, 10055, 10056, 10058, 10061, 10063, 10066, 10068, 10071, 10076, 10077, 10078, 10079, 10080,
          10082,
          10083, 10084, 10085, 10086, 10087, 10091, 10095, 10096, 10100, 10101, 10102, 10104, 10108, 10110, 10111,
          10112,
          10114, 10115, 10117, 10120, 10121, 10122, 10123, 10124, 10126, 10127, 10135, 10137, 10138, 10139, 10140,
          10143,
          10145, 10146, 10149, 10150, 10151, 10152, 10153, 10154, 10155, 10156, 10157, 10159, 10160, 10161, 10163,
          10167,
          10168, 10170, 10171, 10172, 10173, 10174, 10176, 10178, 10179, 10181, 10183, 10184, 10185, 10188, 10189,
          10191,
          10194, 10196, 10197, 10203, 10216, 10220, 10221, 10224, 10228, 10235, 10241, 10244, 10245, 10248, 10257,
          10261,
          10262, 10263, 10268, 10281, 10284, 10285, 10286, 10287, 10288, 10297, 10300, 10304, 10306, 10310, 10311,
          10315,
          10317, 10324, 10325, 10335, 10345, 10349, 10353, 10364, 10365, 10373, 10379, 10380, 10384, 10391, 10401,
          10411,
          10414, 10421, 10432, 10433, 10436, 10447, 10454, 10456, 10458, 10464, 10467, 10479, 10489, 10499]


def get_class_labels(data):
    class_labels_map = {}
    index = 0
    for class_label in data['labels']:
        class_labels_map[class_label] = index
        index += 1
    return class_labels_map


def get_database(data, subset, root_path, video_path_formatter):
    video_ids = []
    video_paths = []
    annotations = []

    for key, value in data['database'].items():
        this_subset = value['subset']
        if this_subset == subset:
            video_ids.append(key)
            annotations.append(value['annotations'])
            if 'video_path' in value:
                video_paths.append(Path(value['video_path']))
            else:
                if 'label' in value['annotations']:
                    label = value['annotations']['label']
                else:
                    label = 'test'
                video_paths.append(video_path_formatter(root_path, label, key))
    return video_ids, video_paths, annotations


class VideoDataset(data.Dataset):

    def __init__(self,
                 root_path,
                 annotation_path,
                 subset,
                 direct_index='0',
                 spatial_transform=None,
                 temporal_transform=None,
                 target_transform=None,
                 video_loader=None,
                 video_path_formatter=(lambda root_path, label, video_id:
                 root_path / label / video_id),
                 image_name_formatter=lambda x: f'{x}.jpg',  # f'image_{x:05d}.jpg'
                 target_type='label'):

        self.data, self.class_names = self.__make_dataset(
            root_path, annotation_path, subset, video_path_formatter, direct_index)

        self.spatial_transform = spatial_transform
        self.temporal_transform = temporal_transform
        self.target_transform = target_transform
        if video_loader is None:
            self.loader = VideoLoader(image_name_formatter)
        else:
            self.loader = video_loader

        self.target_type = target_type

    def __make_dataset(self, root_path, annotation_path, subset,
                       video_path_formatter, direct_index='0'):  # 如果direct_index！=0，说明是直接给图片
        if direct_index == '0':
            with annotation_path.open('r') as f:
                data = json.load(f)
        else:
            data = {'labels': ['NORMAL', 'AMD', 'DR'], 'database': {direct_index: {'subset': 'testing', 'annotations': {}}}}
        video_ids, video_paths, annotations = get_database(
            data, subset, root_path, video_path_formatter)
        class_to_idx = get_class_labels(data)
        idx_to_class = {}
        for name, label in class_to_idx.items():
            idx_to_class[label] = name

        n_videos = len(video_ids)
        dataset = []
        for i in range(n_videos):
            if i % (n_videos // 1) == 0:
                print('dataset loading [{}/{}]'.format(i, len(video_ids)))
            if 'label' in annotations[i]:
                label = annotations[i]['label']
                label_id = class_to_idx[label]
            else:
                label = 'test'
                label_id = -1

            video_path = video_paths[i]
            print(video_path.exists(), video_path)
            if not video_path.exists():
                continue
            segment = [1, 101]  # 301
            if segment[1] == 1:
                continue

            frame_indices = list(range(segment[0], segment[1]))
            sample = {
                'video': video_path,
                'segment': segment,
                'frame_indices': frame_indices,
                'video_id': video_ids[i],
                'label': label_id
            }
            dataset.append(sample)
        return dataset, idx_to_class

    def __loading(self, path, frame_indices):
        clip = self.loader(path, frame_indices)
        self.spatial_transform = None  # zsj
        # if self.spatial_transform is not None:
        #     self.spatial_transform.randomize_parameters()
        #     clip = [self.spatial_transform(img) for img in clip]
        # else:
        clip = [torchvision.transforms.ToTensor()(ele) for ele in clip]
        clip = torch.stack(clip, 0).permute(1, 0, 2, 3)

        return clip

    def __getitem__(self, index):
        path = self.data[index]['video']
        if isinstance(self.target_type, list):
            target = [self.data[index][t] for t in self.target_type]
        else:
            target = self.data[index][self.target_type]

        frame_indices = self.data[index]['frame_indices']
        if self.temporal_transform is not None:
            frame_indices = self.temporal_transform(frame_indices)

        clip = self.__loading(path, frame_indices)

        if self.target_transform is not None:
            target = self.target_transform(target)

        return clip, target

    def __len__(self):
        return len(self.data)
