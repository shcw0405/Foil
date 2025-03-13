import math

class Fact:
    def __init__(self, predicate, arguments):
        self.predicate = predicate
        self.arguments = arguments
    
    def __str__(self):
        args_str = ", ".join(self.arguments)
        return f"{self.predicate}({args_str})"
    
    def __eq__(self, other):
        return (self.predicate == other.predicate and 
                self.arguments == other.arguments)
    
    def __hash__(self):
        return hash((self.predicate, tuple(self.arguments)))

class Rule:
    def __init__(self, head, body=None):
        self.head = head
        self.body = body if body is not None else []
    
    def __str__(self):
        if not self.body:
            return str(self.head)
        body_str = ", ".join(str(lit) for lit in self.body)
        return f"{body_str} -> {self.head}"

class FOILAlgorithm:
    def __init__(self):
        self.facts = []
        self.constants = set()
        self.predicates = {}
        self.target_predicate = ""
        
    def add_fact(self, fact_str):
        # 解析事实字符串，例如："Mother(James, Mike)"
        predicate, args_str = fact_str.strip().split("(")
        args_str = args_str.rstrip(")")
        arguments = [arg.strip() for arg in args_str.split(",")]
        
        fact = Fact(predicate, arguments)
        self.facts.append(fact)
        
        # 更新常量集和谓词集
        self.constants.update(arguments)
        if predicate not in self.predicates:
            self.predicates[predicate] = []
        self.predicates[predicate].append(arguments)
    
    def set_target_predicate(self, predicate):
        self.target_predicate = predicate
    
    def generate_all_possible_facts(self, predicate, arity):
        # 生成所有可能的谓词实例
        import itertools
        all_facts = []
        for args in itertools.product(self.constants, repeat=arity):
            all_facts.append(Fact(predicate, list(args)))
        return all_facts
    
    def get_positive_examples(self):
        # 获取目标谓词的已知正例
        if self.target_predicate in self.predicates:
            return [Fact(self.target_predicate, args) for args in self.predicates[self.target_predicate]]
        return []
    
    def get_negative_examples(self):
        # 获取目标谓词的负例（可能的事实中不是正例的部分）
        positive = self.get_positive_examples()
        
        # 确定目标谓词的元数
        if positive:
            arity = len(positive[0].arguments)
        elif self.target_predicate in self.predicates and self.predicates[self.target_predicate]:
            arity = len(self.predicates[self.target_predicate][0])
        else:
            # 假设二元关系
            arity = 2
        
        all_possible = self.generate_all_possible_facts(self.target_predicate, arity)
        return [fact for fact in all_possible if fact not in positive]
    
    def evaluate_literal(self, literal, bindings):
        # 评估在给定绑定下，literal是否为真
        if literal.predicate not in self.predicates:
            return False
        
        # 替换变量
        grounded_args = []
        for arg in literal.arguments:
            if arg in bindings:
                grounded_args.append(bindings[arg])
            else:
                grounded_args.append(arg)
        
        return grounded_args in self.predicates[literal.predicate]
    
    def covers(self, rule, example, bindings=None):
        # 检查规则是否覆盖了例子
        if bindings is None:
            # 初始绑定为头部谓词的变量绑定
            bindings = {}
            for i, arg in enumerate(rule.head.arguments):
                if arg.startswith('?'):
                    bindings[arg] = example.arguments[i]
        
        # 如果所有体文字都被满足，则规则覆盖了例子
        for literal in rule.body:
            # 尝试所有可能的绑定
            satisfied = False
            for args in self.predicates.get(literal.predicate, []):
                new_bindings = bindings.copy()
                match = True
                
                for i, arg in enumerate(literal.arguments):
                    if arg.startswith('?'):
                        if arg in new_bindings:
                            if new_bindings[arg] != args[i]:
                                match = False
                                break
                        else:
                            new_bindings[arg] = args[i]
                    elif arg != args[i]:
                        match = False
                        break
                
                if match:
                    satisfied = True
                    bindings.update(new_bindings)
                    break
            
            if not satisfied:
                return False
        
        return True
    
    def foil_gain(self, rule, new_literal, pos, neg):
        # 计算添加new_literal的信息增益
        p0, n0 = len(pos), len(neg)
        if p0 == 0:
            return 0
        
        # 计算添加new_literal后覆盖的正例和负例
        new_rule = Rule(rule.head, rule.body + [new_literal])
        p1 = sum(1 for ex in pos if self.covers(new_rule, ex))
        n1 = sum(1 for ex in neg if self.covers(new_rule, ex))
        
        if p1 == 0:
            return 0
        
        # 计算信息增益
        gain = p1 * (math.log2(p1/(p1+n1)) - math.log2(p0/(p0+n0)))
        return gain
    
    def learn_rule(self):
        # 获取正例和负例
        pos = self.get_positive_examples()
        neg = self.get_negative_examples()
        
        if not pos:
            return None
        
        # 初始化规则
        # 假设目标谓词是二元的，使用变量 ?x 和 ?y
        head = Fact(self.target_predicate, ["?x", "?y"])
        rule = Rule(head)
        
        # 迭代添加文字，直到规则不再覆盖任何负例或无法添加新文字
        while neg and any(self.covers(rule, ex) for ex in neg):
            # 生成候选文字
            best_literal = None
            best_gain = 0
            
            for pred in self.predicates:
                if pred == self.target_predicate:
                    continue
                
                arity = len(self.predicates[pred][0])
                variables = set()
                
                # 收集已有变量
                for lit in [rule.head] + rule.body:
                    for arg in lit.arguments:
                        if arg.startswith('?'):
                            variables.add(arg)
                
                # 为每个可能的变量组合生成文字
                import itertools
                for args in itertools.product(list(variables) + ["?z"], repeat=arity):
                    literal = Fact(pred, list(args))
                    
                    # 计算信息增益
                    gain = self.foil_gain(rule, literal, pos, neg)
                    
                    if gain > best_gain:
                        best_gain = gain
                        best_literal = literal
            
            if best_literal is None or best_gain <= 0:
                break
            
            # 添加最佳文字到规则体
            rule.body.append(best_literal)
            
            # 更新覆盖的例子
            pos = [ex for ex in pos if self.covers(rule, ex)]
            neg = [ex for ex in neg if self.covers(rule, ex)]
        
        return rule
    
    def run(self):
        # 主方法，运行FOIL算法并返回学到的规则
        rule = self.learn_rule()
        
        if rule:
            # 将变量重命名为更易读的形式
            var_map = {}
            var_count = 0
            
            for literal in [rule.head] + rule.body:
                for i, arg in enumerate(literal.arguments):
                    if arg.startswith('?') and arg not in var_map:
                        if var_count == 0:
                            var_map[arg] = 'x'
                        elif var_count == 1:
                            var_map[arg] = 'y'
                        elif var_count == 2:
                            var_map[arg] = 'z'
                        else:
                            var_map[arg] = f'v{var_count}'
                        var_count += 1
            
            # 替换变量名
            for literal in [rule.head] + rule.body:
                for i, arg in enumerate(literal.arguments):
                    if arg in var_map:
                        literal.arguments[i] = var_map[arg]
            
            return str(rule)
        return "未找到规则"

def main():
    # 读取输入
    n = int(input().strip())
    
    foil = FOILAlgorithm()
    
    # 读取已有关系
    for _ in range(n):
        fact_str = input().strip()
        foil.add_fact(fact_str)
    
    # 读取目标谓词
    target_predicate = input().strip()
    foil.set_target_predicate(target_predicate)
    
    # 运行FOIL算法并输出结果
    result = foil.run()
    print(result)

if __name__ == "__main__":
    main() 