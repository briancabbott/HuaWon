#! -*- coding:utf-8 -*-
# 情感分析例子，利用MLM+P-tuning

# 英文上面的实验参数（使用超参数搜索的方法）：
# we take learning
# rates from 1e-5, 2e-5, 3e-5 and batch sizes from 16, 32.
# For small datasets (COPA, WSC, CB, RTE), we fine-tune
# pretrained models for 20 epochs
import numpy as np
from bert4keras.backend import keras, K
from bert4keras.layers import Loss, Embedding
from bert4keras.tokenizers import Tokenizer
from bert4keras.models import build_transformer_model, BERT
from bert4keras.optimizers import Adam
from bert4keras.snippets import sequence_padding, DataGenerator
from bert4keras.snippets import open
from keras.layers import Lambda, Dense
import json
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0, 1, 2, 3"
import argparse
parser = argparse.ArgumentParser(description="training set index")
parser.add_argument("--train_set_index", "-t", help="training set index", type=str, default="0")
args = parser.parse_args()
train_set_index = args.train_set_index

maxlen = 256
batch_size = 16
num_per_val_file = 45
acc_list = []
# 加载预训练模型
base_model_path='/path/language_model/chinese_roberta_wwm_ext_L-12_H-768_A-12/'
config_path = base_model_path+'bert_config.json'
checkpoint_path =  base_model_path+'bert_model.ckpt'
dict_path = base_model_path+'vocab.txt'


# 加载数据的方法
def load_data(filename):
    D = []
    with open(filename, encoding='utf-8') as f:
        for jj,l in enumerate(f):
            #print("l:",l)
            json_string=json.loads(l.strip())
            # print("json_string:",json_string)
            sentence1=json_string['abst']
            sentence2=json_string['keyword']
            label=json_string['label']
            text=sentence1[0:200]+"的关键词是"+"，".join(sentence2)

            #text, label = l.strip().split('\t')
            D.append((text, int(label)))
    return D

# 加载数据集
# 加载数据集，只截取一部分，模拟小数据集
train_data = load_data('ready_data/csl/train_{}.json'.format(train_set_index))
valid_data = []
for i in range(5):
    valid_data += load_data('ready_data/csl/dev_{}.json'.format(i))
test_data = load_data('ready_data/csl/csl_publicTest.json')

# 模拟标注和非标注数据
train_frac = 1 # 0.01  # 标注数据的比例
print("0.length of train_data:",len(train_data)) # 16883
num_labeled = int(len(train_data) * train_frac)
# unlabeled_data = [(t, 2) for t, l in train_data[num_labeled:]]
train_data = train_data[:num_labeled]
print("1.num_labeled data used:",num_labeled," ;train_data:",len(train_data)) # 168

# train_data = train_data + unlabeled_data

# 建立分词器
tokenizer = Tokenizer(dict_path, do_lower_case=True)

# 对应的任务描述
mask_idx = 1 #5
unused_length=9 # 9
desc = ['[unused%s]' % i for i in range(1, unused_length)] # desc: ['[unused1]', '[unused2]', '[unused3]', '[unused4]', '[unused5]', '[unused6]', '[unused7]', '[unused8]', '[unused9]', '[unused10]']
desc.insert(mask_idx - 1, '[MASK]')            # desc: ['[MASK]', '[unused1]', '[unused2]', '[unused3]', '[unused4]', '[unused5]', '[unused6]', '[unused7]', '[unused8]', '[unused9]', '[unused10]
desc_ids = [tokenizer.token_to_id(t) for t in desc] # 将token转化为id

pos_id = tokenizer.token_to_id(u'很') # e.g. '[unused9]'. 将正向的token转化为id. 默认值：u'很'
neg_id = tokenizer.token_to_id(u'不') # e.g. '[unused10]. 将负向的token转化为id. 默认值：u'不'


def random_masking(token_ids):
    """对输入进行mask
    在BERT中，mask比例为15%，相比auto-encoder，BERT只预测mask的token，而不是重构整个输入token。
    mask过程如下：80%机会使用[MASK]，10%机会使用原词,10%机会使用随机词。
    """
    rands = np.random.random(len(token_ids)) # rands: array([-0.34792592,  0.13826393,  0.8567176 ,  0.32175848, -1.29532141, -0.98499201, -1.11829718,  1.18344819,  1.53478554,  0.24134646])
    source, target = [], []
    for r, t in zip(rands, token_ids):
        if r < 0.15 * 0.8:   # 80%机会使用[MASK]
            source.append(tokenizer._token_mask_id)
            target.append(t)
        elif r < 0.15 * 0.9: # 10%机会使用原词
            source.append(t)
            target.append(t)
        elif r < 0.15:       # 10%机会使用随机词
            source.append(np.random.choice(tokenizer._vocab_size - 1) + 1)
            target.append(t)
        else: # 不进行mask
            source.append(t)
            target.append(0)
    return source, target


class data_generator(DataGenerator):
    """数据生成器
    # TODO TODO TODO 这里面的每一行代码，，，
    目前看只是将原始文本转换为token id
    负向样本（输入是一个[MASK]字符，输出是特定的字符。对于负样本，采用"不"，正样本，采用“很”）
    """
    def __iter__(self, random=False): # TODO 这里的random是指否需要对原始文本进行mask
        batch_token_ids, batch_segment_ids, batch_output_ids = [], [], []
        for is_end, (text, label) in self.sample(random):
            token_ids, segment_ids = tokenizer.encode(text, maxlen=maxlen)
            if label != 2:
                token_ids = token_ids[:1] + desc_ids + token_ids[1:]
                segment_ids = [0] * len(desc_ids) + segment_ids
            if random: # 暂时没有用呢
                source_ids, target_ids = random_masking(token_ids)
            else:
                source_ids, target_ids = token_ids[:], token_ids[:]
            if label == 0: # 负样本
                source_ids[mask_idx] = tokenizer._token_mask_id
                target_ids[mask_idx] = neg_id
            elif label == 1: # 正向样本
                source_ids[mask_idx] = tokenizer._token_mask_id
                target_ids[mask_idx] = pos_id
            batch_token_ids.append(source_ids)
            batch_segment_ids.append(segment_ids)
            batch_output_ids.append(target_ids)
            if len(batch_token_ids) == self.batch_size or is_end: # padding操作
                batch_token_ids = sequence_padding(batch_token_ids)
                batch_segment_ids = sequence_padding(batch_segment_ids)
                batch_output_ids = sequence_padding(batch_output_ids)
                yield [
                    batch_token_ids, batch_segment_ids, batch_output_ids
                ], None
                batch_token_ids, batch_segment_ids, batch_output_ids = [], [], []


class CrossEntropy(Loss):
    """交叉熵作为loss，并mask掉输入部分
    """
    def compute_loss(self, inputs, mask=None):
        y_true, y_pred = inputs
        y_mask = K.cast(K.not_equal(y_true, 0), K.floatx())
        accuracy = keras.metrics.sparse_categorical_accuracy(y_true, y_pred)
        accuracy = K.sum(accuracy * y_mask) / K.sum(y_mask)
        self.add_metric(accuracy, name='accuracy')
        loss = K.sparse_categorical_crossentropy(y_true, y_pred)
        loss = K.sum(loss * y_mask) / K.sum(y_mask)
        return loss


class PtuningEmbedding(Embedding):
    """新定义Embedding层，只优化部分Token
    如果不考虑计算量，也可以先进行梯度求导，再多数位置加上一个极大的负数(如-10000），再求exp(x)，使得多数位置上的梯度为0.
    """
    def call(self, inputs, mode='embedding'):
        embeddings = self.embeddings
        embeddings_sg = K.stop_gradient(embeddings) # 在tf.gradients()参数中存在stop_gradients，这是一个List，list中的元素是tensorflow graph中的op，一旦进入这个list，将不会被计算梯度，更重要的是，在该op之后的BP计算都不会运行。
        mask = np.zeros((K.int_shape(embeddings)[0], 1)) #e.g. mask = array([[0.],[0.],[0.],[0.],[0.],[0.],[0.],[0.],[0.]])
        mask[1:unused_length] += 1  # 只优化id为1～8的token. 注：embedding第一位是[PAD]，跳过。          e.g. mask = array([[0.],[1.],[1.],[1.],[1.],[1.],[1.],[1.],[1.]]); 1-mask = array([[1.],[0.],[0.],[0.],[0.],[0.],[0.],[0.],[0.],[1.]])
        self.embeddings = embeddings * mask + embeddings_sg * (1 - mask)
        return super(PtuningEmbedding, self).call(inputs, mode)


class PtuningBERT(BERT):
    """替换原来的Embedding
    """
    def apply(self, inputs=None, layer=None, arguments=None, **kwargs):
        if layer is Embedding:
            layer = PtuningEmbedding
        return super(PtuningBERT,
                     self).apply(inputs, layer, arguments, **kwargs)


# 加载预训练模型
model = build_transformer_model(
    config_path=config_path,
    checkpoint_path=checkpoint_path,
    model=PtuningBERT, #PtuningBERT, bert
    with_mlm=True
)

for layer in model.layers:
    if layer.name != 'Embedding-Token': # 如果不是embedding层，那么不要训练
        layer.trainable = False

# 训练用模型
y_in = keras.layers.Input(shape=(None,))
output = keras.layers.Lambda(lambda x: x[:, :unused_length+1])(model.output) # TODO TODO TODO
outputs = CrossEntropy(1)([y_in, model.output])

train_model = keras.models.Model(model.inputs + [y_in], outputs)
train_model.compile(optimizer=Adam(6e-4)) # 可能是稍大好一点。模型：6e-4；finetuing常规学习率：2e-5.
train_model.summary()

# 预测模型
model = keras.models.Model(model.inputs, output)

# 转换数据集
train_generator = data_generator(train_data, batch_size)
valid_generator = data_generator(valid_data, batch_size)
test_generator = data_generator(test_data, batch_size)


class Evaluator(keras.callbacks.Callback):
    def __init__(self):
        self.best_val_acc = 0.

    def on_epoch_end(self, epoch, logs=None):
        model.save_weights('pet_tnews_model.weights')
        val_pred_result = evaluate(valid_generator)
        val_pred_result = np.array(val_pred_result, dtype="int32")
        total_acc = val_pred_result.sum()/val_pred_result.shape[0]
        val_pred_result = val_pred_result.reshape(5, num_per_val_file).sum(1)/num_per_val_file
        # val_acc_mean = val_pred_result.mean() 准确率均值和total准确率相等
        if total_acc > self.best_val_acc:
            self.best_val_acc = total_acc
            model.save_weights('pet_tnews_best_model.weights')
        test_pred_result = np.array(evaluate(test_generator))
        test_acc = test_pred_result.sum()/test_pred_result.shape[0]
        acc_tuple = tuple(val_pred_result.tolist()+[total_acc, self.best_val_acc, test_acc])
        acc_list.append(list(acc_tuple))
        draw_acc(acc_list) # 如果需要对照每个验证集准确率
        print(
            u'val_acc_0: %.5f, val_acc_1: %.5f, val_acc_2: %.5f, val_acc_3: %.5f, val_acc_4: %.5f, val_acc_total: %.5f, best_val_acc: %.5f, test_acc: %.5f\n' %
            acc_tuple
        )

# 对验证集进行验证
def evaluate(data):
    total, right = 0., 0.
    pred_result_list = []
    for x_true, _ in data:
        x_true, y_true = x_true[:2], x_true[2]
        y_pred = model.predict(x_true)
        y_pred = y_pred[:, mask_idx, [neg_id, pos_id]].argmax(axis=1)
        y_true = (y_true[:, mask_idx] == pos_id).astype(int)
        total += len(y_true)
        right += (y_true == y_pred).sum()
        pred_result_list += (y_true == y_pred).tolist()
    return pred_result_list

def draw_acc(acc_list):
    import matplotlib.pyplot as plt
    epoch = len(acc_list)
    x = np.linspace(0, epoch, epoch)

    fig, ax = plt.subplots()
    label_list = ["val_0", "val_1", "val_2", "val_3", "val_4", "val_total", "val_best", "test"]
    acc_arr = np.array(acc_list).T
    # Using set_dashes() to modify dashing of an existing line
    for idx, y in enumerate(acc_arr):
        ax.plot(x, y, label=label_list[idx])
    ax.legend()
    plt.savefig("baseline/models_keras/ptuning/output/ptuning_csl.svg") # 保存为svg格式图片，如果预览不了svg图片可以把文件后缀修改为'.png'


if __name__ == '__main__':

    evaluator = Evaluator()

    train_model.fit_generator(
        train_generator.forfit(),
        steps_per_epoch=len(train_generator) * 50,
        epochs=20,
        callbacks=[evaluator]
    )

else:

    model.load_weights('best_model_bert_ptuning.weights')