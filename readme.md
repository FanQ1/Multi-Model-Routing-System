# 新增
1. 门控模块 完成
2. router选择模型 完成
3. 多轮对话
    - 用户可以做多组对话，且每组对话均为多轮对话
    - 多轮对话流程：
    query -> rewrite query -> reconstructed query(based on db and context window) -> router -> model -> response -> reconstructe db and context window -> user
        1.对于重构query和修改数据库，均由memory_manager对象完成. 改对象类似aop增强功能
        2.数据库的重构分为四种操作：ADD, UPDATE, DELETE, NOOP.数据库存储用户和model的每一组对话，但包含去重。如果是已有的内容，则执行NOOP。如果出现新内容，则ADD，如果对已有内容的更新，则UPDATE，如果是对已有内容的颠覆，则DELETE
        3.重构query会根据数据库匹配的结果和context window选择重构方式
4. 可能的问题
    - context window的设计即滑动窗口，保存一个固定长度的窗口。
    - 对于重构query，可能会导致query的意图改变。例如：第一轮为询问算法原理，第二轮为写具体算法，第三步为询问代码细节，最后一步为原理中的数学证明（example：这个算法的上限是由怎么由数学证明得到的？）
    - 数据库的操作比例，分别为多少？可不可以针对执行多的操作进行优化，或者删去不需要的操作？

### 模型能力排名
gemini-2.5-pro [11,30,11,15,29]
qwen3-max [15,18,23,13,4]
deepseek-3.2-exp [22,28,21,35,8]
RANK = [
    [11, 15, 22],
    [30, 18, 28],
    [11, 23, 21],
    [15, 13, 35],
    [29, 4, 8]
]
