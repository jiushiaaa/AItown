/**
 * 数据服务 - 提供各分析页面访问模拟数据的统一接口
 * 从localStorage读取模拟数据，并提供格式化和处理函数
 */

var DataService = {
    // 缓存数据，避免重复从localStorage读取
    cache: {},
    
    // 初始化，注册事件监听
    init: function() {
        // 监听数据更新事件
        window.addEventListener('simulation_data_updated', function() {
            console.log('数据更新事件接收到，清除缓存');
            DataService.clearCache();
            // 触发页面数据更新
            DataService.notifyDataUpdated();
        });
        
        console.log('数据服务已初始化');
        return this;
    },
    
    // 检查是否有模拟数据
    hasSimulationData: function() {
        return localStorage.getItem('simulation_completed') === 'true';
    },
    
    // 获取上次数据更新时间
    getLastUpdated: function() {
        return localStorage.getItem('simulation_last_updated');
    },
    
    // 获取产品数据
    getProductData: function() {
        return this.getDataByKey('product_data');
    },
    
    // 获取模拟步骤数据
    getSimulationData: function() {
        return this.getDataByKey('simulation_data');
    },
    
    // 获取模拟结果数据
    getSimulationResult: function() {
        return this.getDataByKey('simulation_result');
    },
    
    // 根据键名从localStorage获取数据，使用缓存
    getDataByKey: function(key) {
        // 如果缓存中有数据，直接返回
        if (this.cache[key]) {
            return this.cache[key];
        }
        
        // 否则从localStorage读取
        var dataStr = localStorage.getItem(key);
        if (!dataStr) {
            return null;
        }
        
        try {
            var data = JSON.parse(dataStr);
            // 将数据放入缓存
            this.cache[key] = data;
            return data;
        } catch (e) {
            console.error('解析数据出错:', e);
            return null;
        }
    },
    
    // 清除缓存
    clearCache: function() {
        this.cache = {};
        console.log('数据缓存已清除');
    },
    
    // 通知数据已更新
    notifyDataUpdated: function() {
        var event = new CustomEvent('local_data_updated');
        window.dispatchEvent(event);
        console.log('已触发本地数据更新事件');
    },
    
    // 获取预期销售增长数据
    getExpectedSalesIncrease: function() {
        var result = this.getSimulationResult();
        if (result && result.length > 0 && result[0].sales_increase) {
            return result[0].sales_increase;
        }
        return 45.3; // 默认值
    },
    
    // 获取预期客流量增长数据
    getExpectedTrafficIncrease: function() {
        var result = this.getSimulationResult();
        if (result && result.length > 0 && result[0].traffic_increase) {
            return result[0].traffic_increase;
        }
        return 32.7; // 默认值
    },
    
    // 获取品牌声誉提升数据
    getBrandReputationIncrease: function() {
        var result = this.getSimulationResult();
        if (result && result.length > 0 && result[0].brand_increase) {
            return result[0].brand_increase;
        }
        return 27.9; // 默认值
    },
    
    // 获取客户忠诚度提升数据
    getCustomerLoyaltyIncrease: function() {
        var result = this.getSimulationResult();
        if (result && result.length > 0 && result[0].loyalty_increase) {
            return result[0].loyalty_increase;
        }
        return 38.2; // 默认值
    },
    
    // 获取营销策略数据
    getMarketingStrategies: function() {
        var result = this.getSimulationResult();
        if (result && result.length > 0 && result[0].strategies) {
            return result[0].strategies;
        }
        return null; // 没有策略数据时返回null
    },
    
    // 获取消费者分析数据
    getConsumerAnalysis: function() {
        var result = this.getSimulationResult();
        if (result && result.length > 0 && result[0].consumer_analysis) {
            return result[0].consumer_analysis;
        }
        return null;
    },
    
    // 获取地域分析数据
    getRegionAnalysis: function() {
        var result = this.getSimulationResult();
        if (result && result.length > 0 && result[0].region_analysis) {
            return result[0].region_analysis;
        }
        return null;
    },
    
    // 获取消费心理分析数据
    getPsychologyAnalysis: function() {
        var result = this.getSimulationResult();
        if (result && result.length > 0 && result[0].psychology_analysis) {
            return result[0].psychology_analysis;
        }
        return null;
    }
};

// 自动初始化
DataService.init(); 