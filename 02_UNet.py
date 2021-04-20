import scipy.misc
import keras
from keras.models import Sequential, Model,Input
from keras.layers import Dense, Flatten, Dropout, LeakyReLU, ZeroPadding2D, BatchNormalization, concatenate, Reshape, \
    Permute, Activation
from keras.layers.convolutional import Conv2D, MaxPooling2D, UpSampling2D, Deconv2D
from keras.applications.vgg16 import VGG16
from keras.optimizers import Adam
from glob import glob
import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv 
import os
import matplotlib.pyplot as plt 

TEST_SIZE = 1000

class UNET(object):
    def __init__(self, train_clear_path, train_noise_path):
        '''
        :param train_clear_path: the path of clear imgs
        :param train_noise_path: the path of noise imgs
        '''
        self.clears_path = train_clear_path
        self.noises_path = train_noise_path

    def build_encoder(self):
        '''
        build the u-net
        :return: autoencoder of u-net
        '''
        inputs = Input(shape=(256, 256, 3))
        # Block 1
        # 使用32个卷积核每层做两次卷积，一次池化
        conv1 = Conv2D(64, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(inputs)
        conv1 = Conv2D(64, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(conv1)
        pool1 = MaxPooling2D((2, 2), strides=(2, 2), name='block1_pool')(conv1)

        # Block 2
        # 使用64个卷积核每层做两次卷积，一次池化
        conv2 = Conv2D(64, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(pool1)
        conv2 = Conv2D(128, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(conv2)
        pool2 = MaxPooling2D((2, 2), strides=(2, 2), name='block2_pool')(conv2)

        # Block 3
        # 使用128个卷积核每层做两次卷积，一次池化
        conv3 = Conv2D(128, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(pool2)
        conv3 = Conv2D(128, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(conv3)
        pool3 = MaxPooling2D((2, 2), strides=(2, 2), name='block3_pool')(conv3)

        # Block 4
        # 使用256个卷积核每层做两次卷积，一次池化
        conv4 = Conv2D(256, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(pool3)
        conv4 = Conv2D(256, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(conv4)
        pool4 = MaxPooling2D((2, 2), strides=(2, 2), name='block4_pool')(conv4)
        # Block 5
        conv5 = Conv2D(256, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(pool4)
        conv5 = Conv2D(512, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(conv5)
        pool5 = MaxPooling2D((2, 2), strides=(2, 2), name='block5_pool')(conv5)

        conv6 = Conv2D(512, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(pool5)
        conv6 = Conv2D(512, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(conv6)
        pool6 = MaxPooling2D((2, 2), strides=(2, 2), name='block6_pool')(conv6)

        conv7 = Conv2D(512, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(pool6)
        conv7 = Conv2D(1024, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(conv7)
        pool7 = MaxPooling2D((2, 2), strides=(2, 2), name='block7_pool')(conv7)

        conv8 = Conv2D(1024, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(pool7)
        conv8 = Conv2D(1024, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(conv8)
        pool8 = MaxPooling2D((2, 2), strides=(2, 2), name='block8_pool')(conv8)

        # Block 5
        # 使用512个卷积核每层做两次卷积
        conv9 = Conv2D(1024, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(pool8)
        conv9 = Conv2D(1024, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(conv9)

        # 1-2
        up10 = concatenate([UpSampling2D(size=(2, 2))(conv9), conv8])
        conv10 = Conv2D(512, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(up10)
        conv10 = Conv2D(512, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(conv10)
        # 2-4
        up11 = concatenate([UpSampling2D(size=(2, 2))(conv10), conv7])
        conv11 = Conv2D(512, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(up11)
        conv11 = Conv2D(256, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(conv11)


        # 4-8
        up12 = concatenate([UpSampling2D(size=(2, 2))(conv11), conv6])
        conv12 = Conv2D(256, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(up12)
        conv12 = Conv2D(256, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(conv12)

        # 8-16
        up13 = concatenate([UpSampling2D(size=(2, 2))(conv12), conv5])
        conv13 = Conv2D(256, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(up13)
        conv13 = Conv2D(128, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(conv13)


        # 16-32
        up14 = concatenate([UpSampling2D(size=(2, 2))(conv13), conv4])
        conv14 = Conv2D(128, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(up14)
        conv14 = Conv2D(128, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(conv14)

        # 32-64
        up15 = concatenate([UpSampling2D(size=(2, 2))(conv14), conv3])
        conv15 = Conv2D(125, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(up15)
        conv15 = Conv2D(64, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(conv15)

        # 64-128
        up16 = concatenate([UpSampling2D(size=(2, 2))(conv15), conv2])
        conv16 = Conv2D(64, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(up16)
        conv16 = Conv2D(64, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(conv16)

        # 128-256
        up17 = concatenate([UpSampling2D(size=(2, 2))(conv16), conv1])
        conv17 = Conv2D(32, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(up17)
        conv17 = Conv2D(32, (3, 3), activation='relu', padding='same', kernel_initializer='he_normal')(conv17)

        
        conv17 = Conv2D(3, (3, 3), activation='tanh', padding='same',kernel_initializer='he_normal')(conv17)

        # 构建模型
        model = Model(input=inputs, output=conv17)
        optimizer = Adam(0.00025, 0.5)
        # 编译模型
        model.compile(optimizer=optimizer, loss='mse')
        model.summary()
        # 返回模型
        return model

    def load_train(self, batch_size=4):
        '''
        加载数据集
        :param batch_size: 16
        :return: train data
        '''
        # get all the elements of clears_path
        self.clears_lists = glob('%s/*' % (self.clears_path))
        self.noises_lists = glob('%s/*' % (self.noises_path))

        # random index of picture
        index = np.random.randint(0, len(self.clears_lists)-TEST_SIZE, batch_size)

        # save the batch_imgs
        clear_imgs = []
        noise_imgs = []

        for idx in index:
            # get the match imgs of clears and noises
            c_path = ('%s/%d.png' % (self.clears_path, idx))
            n_path = ('%s/%d.png' % (self.noises_path, idx))
            # append clear imgs and noise imgs
            clear_imgs.append(self.imread(c_path))
            noise_imgs.append(self.imread(n_path))

        # normalize clear imgs and noise imgs to -1 - 1
        return np.array(clear_imgs) / 127.5 - 1, np.array(noise_imgs) / 127.5 - 1

    def imread(self, path):
        img = cv.imread(path)
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        return img
    def load_show(self, batch_size=4):
        '''
        load the imgs to show
        :param batch_size: the number of show imgs
        :return: noise imgs , clear imgs wanted to show
        '''
        index = np.random.randint(len(self.clears_lists)-TEST_SIZE, len(self.clears_lists), batch_size)
        clear_imgs = []
        noise_imgs = []
        for idx in index:
            # get the match imgs of clears and noises
            c_path = ('%s/%d.png' % (self.clears_path, idx))
            n_path = ('%s/%d.png' % (self.noises_path, idx))

            clear_imgs.append(self.imread(c_path))
            noise_imgs.append(self.imread(n_path))
        return np.array(clear_imgs) / 127.5 - 1, np.array(noise_imgs) / 127.5 - 1

    def train_on_batch(self, epochs):
        # get the autoencoder network
        model = self.build_encoder()

        his_loss = []

        # for loop to train model
        for epoch in range(epochs):
            # get the data we want to train
            train_clear, train_noise = self.load_train()

            # get loss
            loss = model.train_on_batch(train_noise, train_clear)
            print('Epoch: {}/{}, loss is : {}'.format(epoch,epochs, loss))

            # save the results
            if epoch % 2 == 0:
                # load the clear and noise imgs
                clears, noises = self.load_show()
                # transform noise to clear imgs
                noise2clear = model.predict(noises)
            
            # 保存模型
            if epoch % 500 == 0:
                his_loss.append([epoch, loss])
                path = 'results/test/impro_unet/'
                if not os.path.exists(path):
                    os.makedirs(path)
                model.save(path+'model_%d.h5' % epoch)
                self.sample_images(epoch, clears, noises, noise2clear, path)
        his_loss = np.array(his_loss)
        fig = plt.figure()
        plt.plot(his_loss[:, 0], his_loss[:, 1])
        plt.title('Plot Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.show()
        fig.savefig(path+"figure.png")

    # save imgs
    def sample_images(self, epoch, clear, noise, noise_img2clear_img, path):
        # row = 3, col = 4
        r, c = 3, 4
        # transform imgs to 0 - 1
        clear = 0.5 * clear + 0.5
        noise = 0.5 * noise + 0.5
        noise_img2clear_img = 0.5 * noise_img2clear_img + 0.5

        # get figure and axs
        fig, axs = plt.subplots(r, c)
        for i in range(c):
            # the firs row
            axs[0, i].imshow(clear[i])
            axs[0, i].axis('off')
            # the second row
            axs[1, i].imshow(noise[i])
            axs[1, i].axis('off')
            # the third row
            axs[2, i].imshow(noise_img2clear_img[i])
            axs[2, i].axis('off')
        # save the imgs
        
        fig.savefig(path + "/%d.png" % epoch)
        plt.close()


if __name__ == '__main__':
    # the path of clears and noise
    train_clear_path = 'datasets/original_faces/'
    train_noise_path = 'datasets/dirty_faces/'
    # get the model
    autoencoder = UNET(train_clear_path, train_noise_path)

    # start train, epochs = 10000
    autoencoder.train_on_batch(epochs=10)
