#coding=utf-8
"""
产品关联分析模块 - 负责分析产品间的关联关系，如互补和替代关系
"""

from collections import defaultdict

class ProductAssociationAnalyzer:
    """产品关联分析器，负责分析产品之间的关联关系"""
    
    def __init__(self, data_provider):
        """
        初始化产品关联分析器
        
        Args:
            data_provider: 提供销售数据的对象，通常是SalesTracker实例
        """
        self.data_provider = data_provider
    
    def analyze_product_associations(self, product_name=None):
        """分析产品间关联性，找出经常一起购买的产品组合"""
        # 分析每位顾客的购买记录，找出经常一起购买的产品
        product_pairs = {}
        for customer, purchases in self.data_provider.customer_purchase_history.items():
            all_products = []
            for purchase in purchases:
                all_products.extend(purchase['items'])
                
            # 计算产品对出现频率
            for i, product1 in enumerate(all_products):
                for product2 in all_products[i+1:]:
                    if product1 != product2:
                        # 如果指定了特定产品，则只分析与该产品相关的组合
                        if product_name and product_name not in [product1, product2]:
                            continue
                            
                        pair = tuple(sorted([product1, product2]))
                        product_pairs[pair] = product_pairs.get(pair, 0) + 1
        
        # 计算所有产品的购买频率
        product_frequency = defaultdict(int)
        for customer, purchases in self.data_provider.customer_purchase_history.items():
            for purchase in purchases:
                for item in purchase['items']:
                    product_frequency[item] += 1
        
        # 计算支持度和置信度
        association_rules = []
        for (product1, product2), pair_count in product_pairs.items():
            # 支持度 = 产品对出现次数 / 总购买记录数
            support = pair_count / max(1, len(self.data_provider.customer_purchase_history))
            
            # 置信度A->B = 产品对出现次数 / 产品A出现次数
            confidence_a_to_b = pair_count / max(1, product_frequency[product1])
            confidence_b_to_a = pair_count / max(1, product_frequency[product2])
            
            # 提升度 = 置信度 / (产品B出现频率)
            lift_a_to_b = confidence_a_to_b / max(0.01, product_frequency[product2] / max(1, len(self.data_provider.customer_purchase_history)))
            lift_b_to_a = confidence_b_to_a / max(0.01, product_frequency[product1] / max(1, len(self.data_provider.customer_purchase_history)))
            
            # 添加规则
            association_rules.append({
                'products': [product1, product2],
                'support': support,
                'confidence_a_to_b': confidence_a_to_b,
                'confidence_b_to_a': confidence_b_to_a,
                'lift_a_to_b': lift_a_to_b,
                'lift_b_to_a': lift_b_to_a,
                'pair_count': pair_count
            })
            
        # 按支持度排序
        sorted_rules = sorted(association_rules, key=lambda x: x['pair_count'], reverse=True)
        
        # 找出互补产品 (提升度高的产品对)
        complementary_products = []
        for rule in sorted_rules:
            if rule['lift_a_to_b'] > 1.5 or rule['lift_b_to_a'] > 1.5:
                complementary_products.append({
                    'products': rule['products'],
                    'lift': max(rule['lift_a_to_b'], rule['lift_b_to_a']),
                    'count': rule['pair_count']
                })
        
        # 找出竞争产品 (很少一起购买，但单独购买频率高的产品)
        substitute_products = []
        top_products = sorted(product_frequency.items(), key=lambda x: x[1], reverse=True)
        top_product_names = [p[0] for p in top_products[:10]]  # 取销量最高的10种产品
        
        for i, product1 in enumerate(top_product_names):
            for product2 in top_product_names[i+1:]:
                # 如果指定了特定产品，则只分析与该产品相关的组合
                if product_name and product_name not in [product1, product2]:
                    continue
                    
                pair = tuple(sorted([product1, product2]))
                pair_count = product_pairs.get(pair, 0)
                
                # 如果两个热门产品很少一起购买，可能是竞争关系
                if pair_count < 2:
                    substitute_products.append({
                        'products': [product1, product2],
                        'individual_counts': [product_frequency[product1], product_frequency[product2]],
                        'joint_count': pair_count
                    })
        
        return {
            'frequent_pairs': sorted_rules[:10],  # 取前10个频繁项集
            'complementary_products': complementary_products[:10],  # 取前10个互补产品对
            'substitute_products': substitute_products[:10]  # 取前10个可能的竞争产品对
        }
        
    def find_related_products(self, product_name, relation_type='complementary'):
        """查找与指定产品相关的产品"""
        associations = self.analyze_product_associations(product_name)
        
        related_products = []
        
        if relation_type == 'complementary':
            for item in associations['complementary_products']:
                products = item['products']
                if product_name in products:
                    related_product = products[1] if products[0] == product_name else products[0]
                    related_products.append({
                        'product': related_product,
                        'lift': item['lift'],
                        'count': item['count']
                    })
        elif relation_type == 'substitute':
            for item in associations['substitute_products']:
                products = item['products']
                if product_name in products:
                    related_product = products[1] if products[0] == product_name else products[0]
                    related_products.append({
                        'product': related_product,
                        'individual_counts': item['individual_counts'],
                        'joint_count': item['joint_count']
                    })
                    
        return sorted(related_products, key=lambda x: x.get('lift', 0) if 'lift' in x else x.get('individual_counts', [0])[0], reverse=True) 