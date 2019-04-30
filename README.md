# gre-reciter

这是一个可以用于背 GRE 的小工具！我去年背 GRE 的时候背得非常痛苦，换了市面上各种背单词软件之后还是很痛苦。。于是决定自己写了一个。

亮点：
* **佛系法背词**：背不下来的词不会强求你背下来，而是提高这个词出现概率，择日再战！
* **形近词辨析**：两个长得像的词区分不开怎么办？两个词的编辑距离（Edit Distance）较小，就会有较高几率一起出现，你就不会搞混了！
* **历史可查询**：每个单词都会记录你以前的背词记录，通过看历史就可以知道哪个词最难背了！

## 安装

本背词小工具依赖 playsound, requests, numpy 这三个 Python 库。请使用 pip 或其他方式安装：
```sh
pip install --user --upgrade pip
pip install --user --upgrade playsound requests numpy
```

## 运行

使用如下命令即可开始背词：
```sh
python3 recite.py
```

还有其他一些可用的命令：
* `python3 recite.py list`: 列出所有词。
* `python3 recite.py list-intractable`: 列出所有你背了半天都没背下来的词（具体由 `word_acc` 所定义，可自行修改）。
* `python3 recite.py test`: 随机测试，估测下你背下了百分之多少的词。

## 伪代码

```python
BUS = 10
BUN = 6
BU = 20
BR = 3

while True:
    batch = empty
    for b = 1, ..., BUN:
        repeat
            word = rand_word()
        until word is not in batch and has not been seen by the user before
        add the word to batch
    for b = BUN + 1, ..., BUS:
        repeat
            word = random_word()
        until word is not in batch
        add the word to batch
    
    
    for every word that is not in the batch:
        dist[word] = min_{w in batch} EditDistance(word, w)
    Sort words by dist in the increasing order and add the first BU - BUS words to the batch
    
    for i = 1, ..., BR:
        shuffle the batch randomly
        for each word in batch:
            show the word to the user
            if user remembers the word, delete it from the batch
        if batch is empty:
            break
```

其中，`rand_word()` 的实现如下：
```python
tot = 0
for each word in words:
    tot += word_p(word)

select a word randomly from the distribution Pr[word] = word_p(word) / tot
```
请参阅代码查看 `word_p(word)` 的具体实现。你也可以写一个适合自己的版本。

## 词典

默认使用了 [良心 github 用户 hot13399 的一个《再要你命3000》的电子版词典](https://github.com/hot13399/FLY_US/blob/master/GRE/%E8%AF%8D%E6%B1%87/%E8%A6%81%E4%BD%A0%E5%91%BD%E4%B8%89%E5%8D%83%E7%B3%BB%E5%88%97/%E5%86%8D%E8%A6%81%E4%BD%A0%E5%91%BD3000_%E9%A1%BA%E5%BA%8F_supermemo_QA.txt) 作为词库，并使用了 [金山词霸](http://www.iciba.com/) 上的发音。如果有侵权行为我马上进行删除 QAQ

## License
GNU General Public License v3
