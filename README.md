github爬虫小代码 --- 应对github的长尾效应

前提：目标的仓库列表中有0star的仓库有超过10000条仓库信息，但是只用网页端的话或者直接用API按照star数搜索最多只能返回1000条数据，无法得到全部的数据

解决方式： 用API+star+时间检索让每一轮检索的信息都在1000条以内，缩小检索范围这样就不会漏掉其余仓库的信息

key experience: 如果要获取大量github 仓库信息，最好不要用爬虫qwq, 因为网页端最多只显示1000条数据

最终效果：

<img width="2636" height="1170" alt="image" src="https://github.com/user-attachments/assets/757f1d58-f096-4059-9543-53c8a89dcd0c" />
