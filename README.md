# -
1. 在配对数据集前提下，可以进行图像去噪，修补，去水印，去马赛克，图像增强等操作。
   三个文件均可以完成图像修复工作。

2. 第一个基于自动编码器实现
   第二个基于U-Net实现
   第三个生成对抗网络实现。

3. 在复现的过程中只需要将自己的数据路径填写到代码下方的路径即可开始训练。
   注意：图片大小为256x256x3
   默认保留了1000张作为测试，如果数据总量少于1000，可以更改默认保留测试数据量。
   index = np.random.randint(0, len(self.clears_lists)-1000, batch_size)
   index = np.random.randint(len(self.clears_lists)-1000, len(self.clears_lists), batch_size)

Kears --2.0.4
如有问题欢迎通过邮件联系我：yuhufei@csu.edu.cn
