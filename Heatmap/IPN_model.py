import torch
import torch.nn as nn
import torch.nn.functional as F


class IPN(nn.Module):
    def __init__(self, in_channels, channels, n_classes):
        super(IPN, self).__init__()
        self.in_channels = in_channels
        self.channels = channels
        self.n_classes = n_classes
        self.input = InConv3d(in_channels, channels)
        self.PLM1 = PLM(5, channels)  # self.PLM1 = PLM(5, channels)
        self.PLM2 = PLM(4, channels)  # self.PLM1 = PLM(4, channels)
        self.PLM3 = PLM(2, channels)  # 原来是4
        self.PLM4 = PLM(2, channels)
        self.output = OutConv3d(channels)

    def forward(self, x):
        x = self.input(x)
        x = self.PLM1(x)
        x = self.PLM2(x)
        x = self.PLM3(x)
        feature = self.PLM4(x)
        # feature = torch.squeeze(feature, 2)
        # print("6", feature.shape)
        logits = self.output(feature)
        return logits, feature


class InConv3d(nn.Module):

    def __init__(self, in_channels, channels):
        super().__init__()
        self.Conv3d = nn.Conv3d(in_channels, channels, kernel_size=3, padding=1)
        torch.nn.init.kaiming_normal_(self.Conv3d.weight, nonlinearity='linear')
        self.relu = SELU()

    def forward(self, x):
        x = self.Conv3d(x)
        x = self.relu(x)
        return x


class SELU(nn.Module):
    def __init__(self):
        super(SELU, self).__init__()
        self.alpha = 1.6732632423543772848170429916717
        self.scale = 1.0507009873554804934193349852946

    def forward(self, x):
        temp1 = self.scale * F.relu(x)
        # temp2 = self.scale * self.alpha * (F.elu(-1*F.relu(-1*x)))
        temp2 = self.scale * self.alpha * (-1 * F.relu(1 - torch.exp(x)))
        return temp1 + temp2


class PLM(nn.Module):

    def __init__(self, poolingsize, channels):
        super().__init__()
        self.maxpool = nn.MaxPool3d(kernel_size=[poolingsize, 1, 1])
        self.Conv3d = nn.Conv3d(channels, channels, kernel_size=3, padding=1)
        torch.nn.init.kaiming_normal_(self.Conv3d.weight, nonlinearity='linear')
        self.relu = SELU()

    def forward(self, x):
        x = self.maxpool(x)
        x = self.Conv3d(x)
        x = self.relu(x)
        x = self.Conv3d(x)
        x = self.relu(x)
        return x


class OutConv3d(nn.Module):

    def __init__(self, channels, n_class=64):
        super().__init__()
        self.out_conv = nn.Sequential(
            nn.Conv3d(channels, n_class, kernel_size=3, padding=1, stride=(1, 2, 2))
        )

    def forward(self, x):
        return self.out_conv(x)

