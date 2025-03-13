# Foil

该库用 Cursor 实现了知识图谱中的一阶规则学习算法，它遵循**序贯覆盖框架**，采用**自顶向下**的规则归纳策略。

我对这个算法的理解就是纯搜索，然后剪枝。

代码使用：

> python foil.py

输入

> 5
> Couple(James, David)
>
> Mother(James, Mike)
> Father(David, Mike)
> Mother(James, Ann)
> Sibling(Ann, Mike)
> Father

输出

> Couple(z, x), Mother(z, y) -> Father(x, y)

输入

> 18
> succ(0,1)
> succ(1,2)
> succ(2,3)
> succ(3,4)
> succ(4,5)
> succ(5,6)
> succ(6,7)
> succ(7,8)
> succ(8,9)
> pred(1,0)
> pred(2,1)
> pred(3,2)
> pred(4,3)
> pred(5,4)
> pred(6,5)
> pred(7,6)
> pred(8,7)
> pred(9,8)  
> pred

输出

> succ(y, x) -> pred(x, y)
