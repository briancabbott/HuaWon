#! -*- coding:utf-8 -*-
# 细粒度情感分析例子（5个类别，使用词语作为标签。这种方式可能比第一种方式效果好（默认推荐）），利用MLM+P-tuning
import os

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
import random

maxlen = 128
batch_size = 16

# 加载预训练模型
base_model_path='../pretrained_models/chinese_roberta_wwm_ext_L-12_H-768_A-12/'
config_path = base_model_path+'bert_config.json'
checkpoint_path =  base_model_path+'bert_model.ckpt'
dict_path = base_model_path+'vocab.txt'

# 加载数据的方法
# {"id": 16, "content": "你也不用说对不起，只是，，，，若相惜", "label": "sadness"}
label_list=['neutral','entailment','contradiction'] #### O.K. # 0: neutral, 1: entailment, 2:contradiction
label_en2zh_dict={'neutral':'并且',"entailment":"所以","contradiction":"但是"}

label_zh_list=[label_en2zh_dict[label_en] for label_en in label_en2zh_dict]
label2index={label:i for i,label in enumerate(label_list)} #### O.K.
# 建立分词器
tokenizer = Tokenizer(dict_path, do_lower_case=True)
label2tokenid_dict={} # {'neutral':[neutral_id_1,neutral_id_2],'entailment':[entailment_id_1,entailment_id_2],'contradiction':[contradiction_id_1,contradiction_id_2]}
for label_en in label_list:
    # label_en= # 'neutral'
    label_zh=label_en2zh_dict[label_en]
    char_id_list=[]
    for index,char_zh in enumerate(label_zh):
        char_id_list.append(tokenizer.token_to_id(char_zh))
    label2tokenid_dict[label_en]=char_id_list # e.g. 'neutral':[neutral_id_1,neutral_id_2]
# print("###label2tokenid_dict:",label2tokenid_dict) #  {'neutral': [704, 4989], 'entailment': [1259, 1419], 'contradiction': [4757, 4688]}

label_tokenid_list=[label2tokenid_dict[x] for x in label_list] # label_tokenid_list:[[like_id_1,like_id_2],[happiness_id_1,happiness_id_2],[sadness_id_1,sadness_id_2],[anger_id_1,anger_id_2],[disgust_id_1,disgust_id_2]]
token_id_list_1 = [x[0] for x in label_tokenid_list] # 标签第一个字组成的列表
token_id_list_2 = [x[1] for x in label_tokenid_list] # 标签第二个字组成的列表

# 对应的任务描述
mask_idxs=[1,2]
unused_length=9 # 9
desc = ['[unused%s]' % i for i in range(1, unused_length)] # desc: ['[unused1]','[unused2]','[unused3]','[unused4]','[unused5]','[unused6]','[unused7]','[unused8]']
desc.insert(mask_idxs[0] - 1, '[MASK]')                     #  desc: ['[MASK]',  '[unused1]','[unused2]','[unused3]','[unused4]','[unused5]','[unused6]','[unused7]','[unused8]']
desc.insert(mask_idxs[1] - 1, '[MASK]')                     #  desc: ['[MASK]',   '[MASK]',  '[unused1]','[unused2]','[unused3]','[unused4]','[unused5]','[unused6]','[unused7]','[unused8]']

desc_ids = [tokenizer.token_to_id(t) for t in desc] # 将token转化为id


def load_data(filename):
    D = []
    with open(filename, encoding='utf-8') as f:
        for jj,l in enumerate(f):
            #print("l:",l)
            json_string=json.loads(l.strip())
            # print("json_string:",json_string)
            sentence1=json_string['sentence1']
            sentence2=json_string['sentence2']
            label=json_string['label']
            text="。句子一："+sentence1+"；句子二："+sentence2
            if label not in ['neutral','entailment','contradiction']: # # 如果是其他标签的话，跳过这行数据
                continue
            D.append((text, label))
    return D

path = '../data/FewCLUEDatasets-master/ready_data/ocnli/'
save_path = '../output/ocnli/ptuning/'
if not os.path.exists(save_path):
    os.mkdir(save_path)

data_num = '4'
# 加载数据集
train_data = load_data('{}/train_{}.json'.format(path,data_num))
valid_datas = []
for i in range(5):
    valid_data = load_data('{}/dev_{}.json'.format(path,str(i)))
    valid_datas.append(valid_data)
test_data = load_data('{}/ocnli_publicTest.json'.format(path))

# 模拟标注和非标注数据
train_frac = 1# 0.01  # 标注数据的比例
print("0.length of train_data:",len(train_data)) # 16883
num_labeled = int(len(train_data) * train_frac)
# unlabeled_data = [(t, 2) for t, l in train_data[num_labeled:]]
train_data = train_data[:num_labeled]
print("1.num_labeled data used:",num_labeled," ;train_data:",len(train_data)) # 168

# train_data = train_data + unlabeled_data

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
    目前看只是将原始文本转换为token id
    负向样本（输入是一个[MASK]字符，输出是特定的字符。对于负样本，采用"不"，正样本，采用“很”）
    """
    def __iter__(self, random=False):
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
            source_ids[mask_idxs[0]] = tokenizer._token_mask_id # 1的位置用[mask]填充
            source_ids[mask_idxs[1]] = tokenizer._token_mask_id # 2的位置用[mask]填充
            targt_id_1 = label2tokenid_dict[label][0]
            targt_id_2 = label2tokenid_dict[label][1] # print("targt_id_1:",targt_id_1,";targt_id_2:",targt_id_2) # targt_id_1: 839（代表“伤”） ;targt_id_2: 2552(代表“心”）
            target_ids[mask_idxs[0]] = targt_id_1 # 第一个[mask]对应的正确的标签字，如：“伤”；
            target_ids[mask_idxs[1]] = targt_id_2 # 第二个[mask]对应的正确的标签字，如：“心”。
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
    """交叉熵作为loss，并mask掉输入部分。输入部分指的是：非标签位置的部分，与模板(pattern)有关。
    """
    def compute_loss(self, inputs, mask=None):
        y_true, y_pred = inputs # y_true=(8, 10, 21128)；y_pred=(8, 10, 21128)
        print("CrossEntropy.y_true.shape:",y_true.shape)
        y_mask = K.cast(K.not_equal(y_true, 0), K.floatx()) # 这个是找到1所在的位置，然后计算损失，忽略其他位置上的损失。
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
        mask[0:unused_length+2] += 1  # 0--unused_length位置可学习，并且额外加2个。因为在最开始位置插入了两个[mask]，那么可学习参数延长。
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
train_model.compile(optimizer=Adam(6e-4)) # 默认：6e-4. 3e-5学习率太小了
train_model.summary()

# 预测模型
model = keras.models.Model(model.inputs, output)

# 转换数据集
train_generator = data_generator(train_data, batch_size)
valid_generators = []
for valid_data in valid_datas:
    valid_generator = data_generator(valid_data, batch_size)
    valid_generators.append(valid_generator)
test_generator = data_generator(test_data, batch_size)


class Evaluator(keras.callbacks.Callback):
    def __init__(self):
        self.best_val_acc = 0.

    def on_epoch_end(self, epoch, logs=None):
        model.save_weights('mlm_model_pet_sentencepair.weights')
        val_accs = 0
        for valid_generator in valid_generators:
            val_accs += evaluate(valid_generator)
        val_acc = val_accs / 5
        if val_acc > self.best_val_acc: #  保存最好的模型，并记录最好的准确率
            self.best_val_acc = val_acc
            model.save_weights('best_model_bert_ptuning.weights')
        test_acc = evaluate(test_generator)
        print( # 打印准确率
            u'val_acc: %.5f, best_val_acc: %.5f, test_acc: %.5f\n' %
            (val_acc, self.best_val_acc, test_acc)
        )

# 对验证集进行验证
def evaluate(data):
    """
    计算候选标签列表中每一个标签（如'开心'）的联合概率，并得到联合概率最大的标签所在的索引，并与正确的标签索引做对比。候选标签的列表：['科技','娱乐','汽车',..,'农业']
    y_pred=(32, 2, 21128)=--->(32, 1, 14) = (batch_size, 1, label_size)---argmax--> (batch_size, 1, 1)=(batch_size, 1, index in the label)
    :param data:
    :return:
    """
    label_ids = np.array([tokenizer.encode(l)[0][1:-1] for l in label_zh_list]) # 获得两个字的标签对应的词汇表的id列表，如: label_id=[1093, 689]。label_ids=[[1093, 689],[],[],..[]]tokenizer.encode('农业') = ([101, 1093, 689, 102], [0, 0, 0, 0])
    total, right = 0., 0.
    for x_true, _ in data:
        x_true, y_true = x_true[:2], x_true[2] # x_true = [batch_token_ids, batch_segment_ids]; y_true: batch_output_ids
        y_pred = model.predict(x_true)[:, mask_idxs] # 取出特定位置上的索引下的预测值。y_pred=[batch_size, 2, vocab_size]。mask_idxs = [7, 8]
        # print("y_pred:",y_pred.shape,";y_pred:",y_pred) # (32, 2, 21128)
        # print("label_ids",label_ids) # [[4906 2825],[2031  727],[3749 6756],[3180 3952],[6568 5307],[3136 5509],[1744 7354],[2791  772],[4510 4993],[1092  752],[3125  752],[3152 1265],[ 860 5509],[1093  689]]
        y_pred = y_pred[:, 0, label_ids[:, 0]] * y_pred[:, 1, label_ids[:, 1]] # y_pred=[batch_size,1,label_size]=[32,1,14]。联合概率分布。 y_pred[:, 0, label_ids[:, 0]]的维度为：[32,1,21128]
        # print("y_pred[:, 0, label_ids[:, 0]]:",y_pred[:, 0, label_ids[:, 0]])
        y_pred = y_pred.argmax(axis=1) # 找到概率最大的那个label(词,如“财经”)所在的索引(index)。
        # print("y_pred:",y_pred.shape,";y_pred:",y_pred) # O.K. y_pred: (16,) ;y_pred: [4 0 4 1 1 4 5 3 9 1 0 9]
        # print("y_true.shape:",y_true.shape,";y_true:",y_true) # y_true: (16, 128)
        # y_true=[batch_size,sequence_length]=(16,128); y_true[:, mask_idxs]=[batch_size,2]
        y_true = np.array([label_zh_list.index(tokenizer.decode(y)) for y in y_true[:, mask_idxs]]) # 找到标签对应的ID,对应的文本，对应的标签列表中所在的顺序。 labels=['科技','娱乐',...,'汽车']
        total += len(y_true)
        right += (y_true == y_pred).sum()
    return right / total

if __name__ == '__main__':

    evaluator = Evaluator()

    train_model.fit_generator(
        train_generator.forfit(),
        steps_per_epoch= (len(train_data)/batch_size*50),# len(train_generator) * 50, #
        epochs=20,
        callbacks=[evaluator]
    )
else:
    model.load_weights('best_model_bert_ptuning.weights')