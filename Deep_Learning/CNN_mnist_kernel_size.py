# Author: RenFun
# File: CNN_mnist_kernel_size.py
# Time: 2022/01/04


# 测试卷积神经网络的超参数动态修改
import os
import random
import torchvision
import torch
from torch.utils.data import DataLoader
import torch.nn as nn
import matplotlib.pyplot as plt
import numpy as np


# 添加随机数种子：为模型参数进行初始化
def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    # 设置固定生成随机数的种子，使得每次运行该.py文件时生成的随机数相同
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    # True的话，每次返回的卷积算法将是确定的，即默认算法
    torch.backends.cudnn.deterministic = True
    # 在 PyTorch 中对模型里的卷积层进行预先的优化，也就是在每一个卷积层中测试 cuDNN 提供的所有卷积实现算法，然后选择最快的那个。
    # 这样在模型启动的时候，只要额外多花一点点预处理时间，就可以较大幅度地减少训练时间。
    torch.backends.cudnn.benchmark = True


seed_everything(1024)


# 数据预处理函数：将数据转换到tensor类型，再归一化使其服从（0.5， 0.5）的正态分布
def get_trans():
    # torchvision.transforms:常用的图片变换，例如裁剪、旋转等
    # torchvision.transforms.Compose：主要作用是串联多个图片变换的操作
    trans = torchvision.transforms.Compose(
        [
            # 改变数据类型
            torchvision.transforms.ToTensor(),
            # 数据标准化
            torchvision.transforms.Normalize([0.5], [0.5])
        ]
    )
    return trans


# 加载数据集，并进行预处理
train_data = torchvision.datasets.MNIST(
    root="./mnist",
    # 是否是训练集
    train=True,
    # 调用get_trans()，对数据进行转换
    transform=get_trans(),
    download=True
)
test_data = torchvision.datasets.MNIST(
    root="./mnist",
    train=False,
    transform=get_trans(),
    download=True
)


# 得到测试集的规模
def get_test_data_len():
    return len(test_data)


# 以BATCH_SIZE大小导入数据
def get_trainloader(BATCH_SIZE):
    # batch_size：一次训练所选取的样本数；shuffle：一代训练（epoch）中打乱数据
    train_loader = DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True)
    return train_loader


def get_testloader(BATCH_SIZE):
    test_loader = DataLoader(test_data, batch_size=BATCH_SIZE, shuffle=False)
    return test_loader


os.environ["CUDA_VISIBLE_DEVICES"] = "0"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 设置一个列表，里面存放不同的卷积核大小的CNN模型，模型包含两个卷积层，卷积核数量（通道数）为32，步长为1，选择填充；使用最大池化；一个全连接层
CNN_kernel_size = []
# 3*3的卷积核模型
class CNN_ks3(nn.Module):
    def __init__(self):
        super(CNN_ks3, self).__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(1, 32, 3, 1, 1),
            nn.ReLU()
        )
        self.pool1 = nn.Sequential(
            nn.MaxPool2d(2, 2)
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(32, 32, 3, 1, 1),
            nn.ReLU()
        )
        self.pool2 = nn.Sequential(
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        self.full_connected = nn.Linear(in_features=32*7*7, out_features=10)
    def forward(self, x):
        x = self.conv1(x)
        x = self.pool1(x)
        x = self.conv2(x)
        x = self.pool2(x)
        x = x.view(x.size(0), -1)
        output = self.full_connected(x)
        return output
# 5*5的卷积核模型
class CNN_ks5(nn.Module):
    def __init__(self):
        super(CNN_ks5, self).__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(1, 32, 5, 1, 2),
            nn.ReLU()
        )
        self.pool1 = nn.Sequential(
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(32, 32, 5, 1, 2),
            nn.ReLU()
        )
        self.pool2 = nn.Sequential(
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        self.full_connected = nn.Linear(in_features=32*7*7, out_features=10)
    def forward(self, x):
        x = self.conv1(x)
        x = self.pool1(x)
        x = self.conv2(x)
        x = self.pool2(x)
        x = x.view(x.size(0), -1)
        output = self.full_connected(x)
        return output
# 7*7的卷积核模型
class CNN_ks7(nn.Module):
    def __init__(self):
        super(CNN_ks7, self).__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(1, 32, 7, 1, 3),
            nn.ReLU()
        )
        self.pool1 = nn.Sequential(
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(32, 32, 7, 1, 3),
            nn.ReLU()
        )
        self.pool2 = nn.Sequential(
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        self.full_connected = nn.Linear(in_features=32*7*7, out_features=10)
    def forward(self, x):
        x = self.conv1(x)
        x = self.pool1(x)
        x = self.conv2(x)
        x = self.pool2(x)
        x = x.view(x.size(0), -1)
        output = self.full_connected(x)
        return output


# 将模型添加到列表中
CNN_kernel_size.append(CNN_ks3())
CNN_kernel_size.append(CNN_ks5())
CNN_kernel_size.append(CNN_ks7())
# 定义常量
EPOCH = 20                              # 总的训练次数，即迭代次数
BATCH_SIZE = 128                        # 一批数据的规模，即一次训练选取的样本数量
LR = 0.01                                # 学习率
DOWNLOAD_MNIST = False                  # 运行代码时不需要下载数据集
epoch = 0
# 训练误差
train_loss = []
# 测试精度
accuracy = []
for i in range(3):
    print('模型：', i + 1)
    cnn = CNN_kernel_size[i]
    cnn.to(DEVICE)
    # torch.optim.选择优化函数，例如Adam，SGD ，AdaGrad ，RMSProp等
    optimizer1 = torch.optim.SGD(cnn.parameters(), lr=LR)
    # 损失函数选择交叉熵函数
    loss_function = nn.CrossEntropyLoss()
    # 加载训练集和测试集
    train_loader = get_trainloader(BATCH_SIZE)
    test_loader = get_testloader(BATCH_SIZE)
    for epoch in range(EPOCH):
        x = 0
        for data in train_loader:
            img, label = data
            img = img.to(DEVICE)
            label = label.to(DEVICE)
            out = cnn(img)
            # 得到训练误差
            loss = loss_function(out, label)
            x += loss.data.item()
            # train_loss.append(loss.data.item())
            # print('训练损失值：', loss.data.item())
            # 梯度归零
            optimizer1.zero_grad()
            # 反向传播误差，但是参数还没更新
            loss.backward()                           # 如果出现数据类型错误，将loss.backward(torch.ones_like(loss))
            # 更新模型参数
            optimizer1.step()
        train_loss.append(x/BATCH_SIZE)
        print('epoch次数：', epoch+1, '训练损失值：', x/BATCH_SIZE)
        num_correct = 0
        for data in test_loader:
            img, label = data
            img = img.to(DEVICE)
            label = label.to(DEVICE)
            # 获得输出
            out = cnn(img)
            # 获得测试误差
            loss = loss_function(out, label)
            # 将tensor类型的loss2中的data取出，添加到列表中
            # test_loss.append(loss.data.item())
            _, prediction = torch.max(out, 1)
            # 预测正确的样本数量
            num_correct += (prediction == label).sum()
            # 精度=预测正确的样本数量/测试集样本数量
        acc = float(format(num_correct.cpu().numpy() / float(get_test_data_len()), '0.4f'))  # .cpu()是将参数迁移到cpu上来
        # acc = float((prediction == label.data.cpu().numpy()).astype(int).sum()) / float(get_test_data_len.size(0))
        accuracy.append(acc)
        print('测试精度：', acc)
# 绘制图像1：训练集上的损失值
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.figure(figsize=(11, 5))
plt.subplot(121)
plt.plot(np.arange(1, 21), train_loss[0: 20], color='lightblue', label='卷积核3*3')
plt.plot(np.arange(1, 21), train_loss[20: 40], color='royalblue', label='卷积核5*5')
plt.plot(np.arange(1, 21), train_loss[40: 60], color='orange', label='卷积核7*7')
plt.xlabel("迭代次数")
plt.ylabel("训练损失值")
plt.xticks(np.arange(1, 21, 1))
plt.grid(b=True, linestyle='--')
plt.legend(loc='upper right')
# plt.savefig('CNN_mnist_kernel_size_loss.svg', bbox_inches='tight')
# plt.show()
# 绘制图像2：测试集上的精度
plt.subplot(122)
plt.plot(np.arange(1, 21), accuracy[0: 20], color='lightblue', label='卷积核3*3')
plt.plot(np.arange(1, 21), accuracy[20: 40], color='royalblue', label='卷积核5*5')
plt.plot(np.arange(1, 21), accuracy[40: 60], color='orange', label='卷积核7*7')
plt.xlabel("迭代次数")
plt.ylabel("精度")
plt.xticks(np.arange(1, 21, 1))
plt.grid(b=True, linestyle='--')
plt.legend(loc='upper left')
# plt.savefig('CNN_mnist_kernel_size_acc.svg', bbox_inches='tight')
plt.savefig('CNN_mnist_kernelsize_loss&accuracy.svg', bbox_inches='tight')
plt.show()