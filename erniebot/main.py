#coding=utf-8
"""
正山堂茶业消费者行为模拟系统 - 主程序入口
"""

import sys
import os
import time

# 将父目录添加到sys.path以确保正确导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 定义脚本目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 导入配置集成模块
from config_integration import HOST, PORT, MODEL_API_KEY, DB_PATH, DEBUG

from modules.client import ApiClient
from modules.data_processor import (
    string_to_dict, check_completed, clean_emoji_field, 
    verify_and_fix_json
)
from modules.product_manager import (
    is_product_generation_request, extract_consumer_type,
    extract_brand_summary, save_brand_info_to_file,
    save_simulation_data_to_file
)
from modules.sales_analytics import SalesTracker
from modules.socket_manager import SocketManager
from modules.config import PRODUCT_COSTS
from modules.db_manager import DBManager  # 导入数据库管理器
import logging # Add logging import
import json # 导入json模块用于写入日志
# import os # os 已经被导入
from datetime import datetime # 导入datetime用于生成时间戳

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """主程序入口"""
    # 显示配置信息
    logging.info(f"服务配置: 地址={HOST}:{PORT}, 调试模式={DEBUG}")
    
    # 初始化组件
    api_client = ApiClient()
    socket_manager = SocketManager(host=HOST, port=PORT)
    sales_tracker = SalesTracker()
    
    # 初始化数据库管理器
    db_manager = DBManager(db_path=DB_PATH)
    
    # 添加API连接状态检查
    logging.info("检查API连接状态...")
    is_api_available, api_status_message = api_client.connector.check_api_connection()
    logging.info(f"API状态: {api_status_message}")
    
    if not is_api_available:
        logging.warning(f"API连接检查失败: {api_status_message}")
        retry_connection = 0
        max_connection_retries = 3
        
        while not is_api_available and retry_connection < max_connection_retries:
            retry_connection += 1
            logging.info(f"尝试重新检查API连接 ({retry_connection}/{max_connection_retries})...")
            time.sleep(10)  # 等待10秒后重试
            is_api_available, api_status_message = api_client.connector.check_api_connection()
            logging.info(f"API重试状态: {api_status_message}")
            
        if not is_api_available:
            logging.warning("API连接状态异常，但将尝试继续运行。可能会在实际调用时遇到问题。")
            # 注意：我们不退出程序，而是继续尝试，因为连接检查可能不完全准确
    else:
        logging.info("API连接状态正常，继续初始化...")
    
    # 初始化Socket连接
    if not socket_manager.initialize():
        logging.error("Socket连接初始化失败，可能是端口冲突或网络问题。程序将退出。")
        sys.exit(1) # Exit with a non-zero status code to indicate failure
    
    # 存储所有模拟数据以便最后生成总结
    all_simulation_data = []
    prev_day_data = None # Store previous day's successful data for fallback
    
    # 先等待接收初始消息
    brand_suggestion = None
    brand_name_for_simulation = None
    
    # 初始化实时日志文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    realtime_log_filename = f"realtime_simulation_log_{timestamp}.json"
    
    # 创建空的实时日志文件
    os.makedirs(os.path.dirname(os.path.join(SCRIPT_DIR, realtime_log_filename)), exist_ok=True)
    with open(os.path.join(SCRIPT_DIR, realtime_log_filename), 'w', encoding='utf-8') as f:
        json.dump({"simulation_start_time": timestamp, "days": []}, f, ensure_ascii=False, indent=2)
    
    logging.info(f"已创建实时日志文件: {os.path.join(SCRIPT_DIR, realtime_log_filename)}")
    
    # 将实时日志路径传递给socket_manager
    socket_manager.set_realtime_log_path(os.path.join(SCRIPT_DIR, realtime_log_filename))

    # --- 等待WebGL客户端连接，然后等待用户指令 ---
    logging.info("等待WebGL客户端连接...")
    retry_count = 0
    max_initial_retries = 10 # 最大重试次数
    client_connected = False
    
    # 等待WebGL客户端连接
    while not client_connected:
        recv_data = None
        try:
            # 接收WebGL客户端连接确认
            recv_data = socket_manager.receive()
            
            # 如果接收失败则短暂等待再重试，不记录日志减少噪音
            if recv_data == False:
                time.sleep(2)  # 增加等待时间到2秒减少重试频率
                continue
                
            # 检查是否是WebGL连接消息
            type_flag_check, content_check = api_client.extract_info(recv_data)
            
            if (type_flag_check and content_check == 'Unity客户端已连接') or \
               (type_flag_check and content_check.startswith('Unity WebGL 客户端已连接')):
                # 显示消息并设置客户端已连接标志
                logging.info("WebGL客户端已连接，等待用户输入指令...")
                # 发送欢迎消息
                socket_manager.send({
                    "type": "welcome", 
                    "message": "WebGL客户端连接成功，请输入指令"
                })
                # 设置客户端已连接标志
                client_connected = True
                # 暂停5秒等待界面完全加载
                time.sleep(5)
                
            # 检查是否已经收到指令
            elif type_flag_check and content_check and not content_check.startswith('Unity'):
                logging.info(f"收到来自客户端的指令: '{content_check}'")
                # 这是第一个实际命令，直接使用它并跳出循环
                client_connected = True
                
                # 处理这个初始指令
                process_command(content_check, socket_manager, api_client, sales_tracker, db_manager, all_simulation_data, brand_name_for_simulation, realtime_log_filename)
                
        except Exception as e:
            # 出错时等待一段时间再重试
            logging.error(f"等待客户端连接时出错: {str(e)}")
            time.sleep(3)
            continue
    
    # 创建一个持续运行的命令处理循环
    logging.info("进入持续监听模式，等待用户命令...")
    
    try:
        # 持续监听用户命令的循环
        while True:
            try:
                # 接收用户命令
                recv_data = socket_manager.receive()
                
                # 未收到数据，等待一段时间再尝试
                if recv_data == False:
                    time.sleep(1)  # 短暂等待再次检查
                    continue
                
                # 成功接收数据，尝试解析
                type_flag, content = api_client.extract_info(recv_data)
                
                if type_flag and content and not content.startswith('Unity'):
                    # 这是一个有效命令
                    logging.info(f"收到来自客户端的命令: '{content}'")
                    
                    # 处理命令
                    process_command(content, socket_manager, api_client, sales_tracker, db_manager, all_simulation_data, brand_name_for_simulation, realtime_log_filename)
                    
                    # 发送命令处理完成的消息
                    socket_manager.send({
                        "type": "command_processed",
                        "message": f"命令 '{content}' 处理完成"
                    })
                    
            except Exception as e:
                logging.error(f"命令处理循环中出错: {str(e)}", exc_info=True)
                time.sleep(3)  # 出错后暂停一段时间
                continue
            
            # 短暂休眠避免CPU过载
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        logging.info("收到键盘中断，程序退出")
    except Exception as e:
        logging.error(f"主循环异常: {str(e)}", exc_info=True)
    finally:
        # 确保在程序退出时关闭socket连接
        if socket_manager and hasattr(socket_manager, 'socketserver') and socket_manager.socketserver:
            try:
                socket_manager.socketserver.close()
            except Exception as close_err:
                logging.warning(f"关闭socket时出错: {close_err}")
        logging.info("erniebot/main.py 主函数完成，程序退出")


def process_command(command, socket_manager, api_client, sales_tracker, db_manager, all_simulation_data, brand_name_for_simulation, realtime_log_filename):
    """处理单个命令的函数，从主循环中抽取出来以便重用"""
    logging.info(f"收到来自客户端的指令: '{command}'")
    
    try:
        # 检查是否是system_init命令（特殊处理）
        if command == "system_init":
            socket_manager.send({
                "type": "system_status",
                "status": "ready",
                "message": "系统已准备就绪"
            })
            logging.info("处理system_init命令完成")
            return
            
        # 检查是否需要生成产品建议
        if is_product_generation_request(command):
            # --- Product Generation Logic ---
            logging.info("开始生成茶饮品牌建议...")
            # 提取目标消费群体
            target_consumers = extract_consumer_type(command)
            if target_consumers:
                logging.info(f"针对 {target_consumers} 生成品牌")
                
                # 生成产品建议
                brand_suggestion = api_client.generate_tea_product(target_consumers)
                
                # 提取品牌名称和简洁描述
                brand_name, simple_description = extract_brand_summary(brand_suggestion)
                
                # 保存品牌信息到文件
                save_brand_info_to_file(brand_name, simple_description, target_consumers, brand_suggestion)
                
                # 保存品牌名称供后续模拟使用
                brand_name_for_simulation = brand_name
                
                # 设置新产品名称到销售追踪器
                sales_tracker.new_product_name = brand_name
                
                # 添加新产品到成本和库存数据中 (估算成本为定价的40%)
                import random
                estimated_price = random.randint(200, 500)  # 估计零售价
                PRODUCT_COSTS[brand_name] = {
                    "cost": int(estimated_price * 0.4),
                    "initial_stock": 200
                }
                sales_tracker.product_stock[brand_name] = 200
                
                # 发送产品建议回客户端
                socket_manager.send({
                    "type": "product_generated",
                    "product": {
                        "name": brand_name,
                        "description": simple_description,
                        "target_consumers": target_consumers
                    },
                    "raw_suggestion": brand_suggestion
                })
                
                logging.info(f"品牌设计完成: {brand_name}")
                
                # 将品牌信息写入实时日志
                try:
                    with open(os.path.join(SCRIPT_DIR, realtime_log_filename), "r", encoding="utf-8") as f:
                        realtime_log = json.load(f)
                    
                    realtime_log["brand_info"] = {
                        "name": brand_name,
                        "description": simple_description,
                        "full_suggestion": brand_suggestion,
                        "target_consumers": target_consumers
                    }
                    
                    with open(os.path.join(SCRIPT_DIR, realtime_log_filename), "w", encoding="utf-8") as f:
                        json.dump(realtime_log, f, ensure_ascii=False, indent=2)
                except Exception as log_err:
                    logging.error(f"将品牌信息写入实时日志时出错: {str(log_err)}")
                
                # 直接使用生成的产品描述，启动消费者模拟循环
                logging.info("使用生成的产品描述开始消费者模拟...")
                question = simple_description
                
                # --- Start Simulation Loop (only after getting summary) ---
                logging.info("准备开始消费者行为模拟循环...")
                prev_cumulative = None  # 存储上一天的累计数据
                simulation_days = []  # 存储模拟数据
     
                for day in range(1, 31):  # 最多模拟30天
                    retry_count = 0 # Reset retry count for each day
                    max_api_retries = 3
                    
                    try:
                        if day == 1:
                            # 首次对话，发送品牌/店铺信息
                            logging.info("开始新的消费者行为模拟...")
                            # 提供消费者数据以增强模拟效果
                            consumer_data = {
                                "include_region": True,
                                "include_psychological_traits": True
                            }
                            # 使用生成提示词函数生成带有消费者画像信息的提示词
                            messages = api_client.generate_prompt(
                                [{"role": "user", "content": question}], 
                                consumer_data
                            )
                            logging.info(f"准备调用API模拟第{day}天的消费者行为 - 使用提示词：{question[:100]}...")
                            try:
                                response = api_client.chat_with_messages(messages)
                                logging.info(f"成功获取第{day}天API响应，长度：{len(response) if response else 0}字符")
                            except Exception as api_err:
                                logging.error(f"API调用异常: {str(api_err)}", exc_info=True)
                                # 创建一个基本的默认响应
                                response = f"API调用失败: {str(api_err)}"
                        else:
                            logging.info(f"第{day}天：请求模拟下一天消费者行为...")
                            # 增加更详细的日志记录和错误处理
                            try:
                                response = api_client.chat("继续")
                                logging.info(f"成功获取第{day}天API响应，长度：{len(response) if response else 0}字符")
                            except Exception as api_err:
                                logging.error(f"API调用异常: {str(api_err)}", exc_info=True)
                                response = f"API调用失败: {str(api_err)}"
     
                        logging.info(f"Day {day} API Response:\n{response[:200]}...") # Log API response (truncated)
                        json_text = api_client.extract_json(response)
                        json_data = None # Initialize json_data for the day
                        
                        retry_count = 0 # 明确重置重试计数器
                        while json_data is None and retry_count < max_api_retries:
                            if json_text:
                                # Attempt to parse JSON
                                json_data_attempt = string_to_dict(json_text)
                                if json_data_attempt: # Check if parsing was successful
                                   json_data = json_data_attempt
                                   logging.info(f"Day {day}: Successfully extracted and parsed JSON.")
                                   break # Exit retry loop on success
                                else:
                                   logging.warning(f"Day {day}: Failed to parse JSON from extracted text. Retry {retry_count+1}/{max_api_retries}.")
                                   json_text = None # Force retry logic
                            
                            if json_data is None: # If extraction failed or parsing failed
                                logging.warning(f"Day {day}: Failed to extract/parse JSON. Retry {retry_count+1}/{max_api_retries}.")
                                retry_count += 1
                                if retry_count < max_api_retries:
                                    # 更详细的重试提示，明确指定格式
                                    retry_prompt = """请使用标准JSON格式生成消费者行为数据，必须包含以下结构：
    {
      "customer_interactions": [
        {"name": "消费者1", "location": "入口", "comments": "查看商品", "emoji": "😊"},
        {"name": "消费者2", "location": "茶台", "comments": "品尝产品", "emoji": "👍"}
      ],
      "daily_stats": {"visitors": 10, "revenue": 1000},
      "day": 1
    }
    所有字段必须使用双引号，并用```json```标记包裹整个JSON。"""
                                    logging.info(f"Day {day}: Sending retry prompt: {retry_prompt}")
                                    # 增强重试逻辑中的错误处理
                                    try:
                                        response = api_client.chat(retry_prompt)
                                        logging.info(f"Day {day} API Retry Response:\n{response[:200]}...")
                                        json_text = api_client.extract_json(response)
                                    except Exception as retry_err:
                                        logging.error(f"重试API调用时出错: {str(retry_err)}", exc_info=True)
                                        # 在重试失败后继续循环，让外层逻辑处理
                                        time.sleep(8)  # 重试失败后等待8秒再继续
                                else:
                                    logging.error(f"Day {day}: Max retries reached for API call.")
                            
                        # Fallback logic if json_data is still None after retries
                        if json_data is None:
                            logging.warning(f"Day {day}: Failed to get valid JSON after retries. Attempting fallback.")
                            if len(simulation_days) > 0: 
                                logging.warning(f"Day {day}: Using previous day's data as fallback.")
                                prev_day_data = simulation_days[-1].copy()
                                json_data = prev_day_data.copy() 
                                # 更新日期
                                json_data['day'] = day 
                                # 对fallback数据做轻微随机变化，避免完全重复数据
                                if 'daily_stats' in json_data:
                                    import random
                                    # 对访客数量和收入做轻微调整，使数据看起来更自然
                                    for stat in ['customer_flow', 'total_sales', 'avg_expense']:
                                        if stat in json_data['daily_stats']:
                                            value = json_data['daily_stats'][stat]
                                            if isinstance(value, (int, float)):
                                                # 在原值基础上上下浮动10%
                                                variation = 0.9 + random.random() * 0.2  # 0.9 到 1.1之间
                                                json_data['daily_stats'][stat] = int(value * variation)
                                logging.info(f"Day {day}: Applied variation to fallback data.")
                            else:
                                logging.error(f"Day {day}: No previous day data available. Generating default data.")
                                json_data = verify_and_fix_json(None, day, prev_cumulative)
                        
                        # --- Processing valid json_data (either from API or fallback) --- 
                        
                        # 验证和修复JSON数据 (always run verify_and_fix)
                        json_data = verify_and_fix_json(json_data, day, prev_cumulative)
                        
                        # 处理表情符号
                        json_data = clean_emoji_field(json_data)
                        
                        # 记录销售数据用于分析
                        sales_tracker.record_daily_sales(
                            day, 
                            json_data.get('customer_interactions', []), 
                            json_data.get('daily_stats', {})
                        )
                        
                        # 保存当天的累计数据用于下一次迭代
                        prev_cumulative = json_data.get('cumulative_stats', {})
                        
                        # 保存本次数据
                        simulation_days.append(json_data.copy())
                        all_simulation_data.append(json_data.copy())
                        
                        # 保存数据到数据库
                        try:
                            logging.info(f"尝试将第 {day} 天的数据保存到数据库...")
                            save_success = db_manager.save_simulation_data(json_data, day)
                            if save_success:
                                logging.info(f"第 {day} 天的数据已成功保存到数据库。")
                            else:
                                logging.warning(f"第 {day} 天的数据保存到数据库失败。")
                        except Exception as db_err:
                            logging.error(f"保存数据到数据库时出错: {str(db_err)}")
     
                        # 发送模拟数据
                        socket_manager.send_simulation_data(day, json_data)
                        
                        # 实时记录每天的模拟数据到日志文件
                        try:
                            try:
                                with open(os.path.join(SCRIPT_DIR, realtime_log_filename), "r", encoding="utf-8") as f:
                                    realtime_log = json.load(f)
                            except FileNotFoundError:
                                logging.error(f"实时日志文件未找到: {os.path.join(SCRIPT_DIR, realtime_log_filename)}")
                                realtime_log = {"simulation_start_time": datetime.now().strftime("%Y%m%d_%H%M%S"), "days": []}
                            except json.JSONDecodeError as e:
                                logging.error(f"解析实时日志文件失败: {e}")
                                realtime_log = {"simulation_start_time": datetime.now().strftime("%Y%m%d_%H%M%S"), "days": []}
                            
                            # 将当天数据保存到实时日志
                            day_data = {
                                "day": day,
                                "data": json_data
                            }
                            realtime_log["days"].append(day_data)
                            
                            # 写回文件
                            try:
                                with open(os.path.join(SCRIPT_DIR, realtime_log_filename), "w", encoding="utf-8") as f:
                                    json.dump(realtime_log, f, ensure_ascii=False, indent=2)
                            except IOError as e:
                                logging.error(f"写入第{day}天数据到实时日志失败: {e}")
                            
                            logging.info(f"已将第{day}天的模拟数据实时记录到日志文件")
                        except Exception as e:
                            logging.error(f"实时记录第{day}天的模拟数据时出错: {str(e)}")
                        
                        # 检查是否完成30天模拟
                        if check_completed(json_data) or day >= 30:
                            logging.info("已完成30天模拟，生成总结报告")
                            
                            # 生成模拟总结
                            summary = sales_tracker.generate_simulation_summary(all_simulation_data)
                            
                            # 计算产品爆款指数
                            if brand_name_for_simulation:
                                product_metrics = sales_tracker.calculate_product_metrics(brand_name_for_simulation)
                                popularity_score = product_metrics['popularity_score']
                                
                                # 添加地域分析和消费心理分析
                                regional_analysis = sales_tracker.analyze_regional_distribution()
                                psychological_analysis = sales_tracker.analyze_consumer_psychology()
                                
                                # 将分析结果添加到产品指标中
                                product_metrics['regional_analysis'] = regional_analysis
                                product_metrics['psychological_analysis'] = psychological_analysis
                            else:
                                popularity_score = None
                            
                            # 添加总结数据到实时日志
                            try:
                                with open(os.path.join(SCRIPT_DIR, realtime_log_filename), "r", encoding="utf-8") as f:
                                    realtime_log = json.load(f)
                                
                                realtime_log["simulation_summary"] = summary
                                if brand_name_for_simulation:
                                    realtime_log["product_metrics"] = product_metrics
                                
                                with open(os.path.join(SCRIPT_DIR, realtime_log_filename), "w", encoding="utf-8") as f:
                                    json.dump(realtime_log, f, ensure_ascii=False, indent=2)
                                
                                logging.info("已将模拟总结记录到实时日志文件")
                            except Exception as e:
                                logging.error(f"记录模拟总结到实时日志文件时出错: {str(e)}")
                            
                            # 发送模拟总结
                            socket_manager.send_simulation_summary(summary, prev_cumulative, popularity_score)
                            logging.info("模拟总结已发送")
                            
                            # 更新当天的销售统计
                            sales_tracker.update_from_simulation(json_data)
                            logging.info(f"第 {day} 天模拟处理完成")
                            break
                            
                    except Exception as e:
                        logging.error(f"Day {day} 处理主循环出错: {str(e)}", exc_info=True)
                        if len(simulation_days) > 0:
                            json_data = simulation_days[-1].copy()
                            json_data['day'] = day
                        else:
                            json_data = verify_and_fix_json(None, day, prev_cumulative)
                        
                        # 发送错误恢复的数据
                        socket_manager.send_simulation_data(day, json_data)
                        
                        # 保存用于下一天
                        simulation_days.append(json_data.copy())
                        all_simulation_data.append(json_data.copy())
                        
                        # 记录错误恢复的数据到实时日志
                        try:
                            with open(os.path.join(SCRIPT_DIR, realtime_log_filename), "r", encoding="utf-8") as f:
                                realtime_log = json.load(f)
                            
                            # 添加错误恢复的数据
                            day_data = {
                                "day": day,
                                "data": json_data,
                                "error_recovery": True,
                                "error": str(e)
                            }
                            realtime_log["days"].append(day_data)
                            
                            # 写回文件
                            with open(os.path.join(SCRIPT_DIR, realtime_log_filename), "w", encoding="utf-8") as f:
                                json.dump(realtime_log, f, ensure_ascii=False, indent=2)
                            
                            logging.info(f"已将第{day}天的错误恢复数据实时记录到日志文件")
                        except Exception as log_error:
                            logging.error(f"实时记录第{day}天的错误恢复数据时出错: {str(log_error)}")
                
                # 模拟完成
                logging.info("消费者行为模拟完成")
                return
                
        # 如果不是特殊命令，则发送为普通查询
        response = api_client.chat(command)
        socket_manager.send({
            "type": "response",
            "query": command,
            "response": response
        })
        logging.info(f"已处理普通查询: {command}")
        
    except Exception as e:
        logging.error(f"处理命令时出错: {str(e)}", exc_info=True)
        socket_manager.send({
            "type": "error",
            "message": f"处理命令时出错: {str(e)}"
        })


if __name__ == '__main__':
    main()