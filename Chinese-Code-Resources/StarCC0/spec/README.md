# StarCC 項目標準實現

## 字典

- `cn`: Simplified Chinese (Mainland China)
- `tw`: Traditional Chinese (Taiwan)
- `twp`: Traditional Chinese (Taiwan, with phrase conversion)
- `hk`: Traditional Chinese (Hong Kong)
- `jp`: Japanese Shinjitai

以 StarCC 標準（稱為 `st`）為中介。

例如 `cn` 轉 `tw`，方法是先使用 `CN2ST`，再使用 `ST2TW`。

參看 [StarCC0/dict](https://github.com/StarCC0/dict)。

未來還將加入：

- [ ] 日本擴張新字體 `jpe`
- [ ] 香港用詞 `hkp`
- [ ] 新馬用詞 `sgp`

## 方法

### 方法一

用 Trie 正向最長匹配。

如果先 `CN2ST`，再 `ST2TW`，則需要分別構造兩個 Trie 樹。

若有多種對應方法，程式只選擇第一個。

### 方法二

為了改進簡轉繁時的「擁有 116 年曆史」型錯誤，在 `CN2ST` 時，應當使用外部分詞工具分詞，再對每個詞分別作轉換。

## StarCC 標準

用字方面使用 StarCC 用字（如「爲」、「牀」，繼承自 OpenCC 用字）。

用詞方面採用中國大陸用詞（繼承自 OpenCC）。

例如，在 `zh-CN` 轉 `zh-TW` 時，是先使用 `CN2ST`，再使用 `ST2TWP`。第一步不發生用詞的轉換。

## API

TODO
