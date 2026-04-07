import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from core.api.poster_control import PosterControlAPI

logger = logging.getLogger("AnalyticsModule")

class AsyncAnalytics:
    def __init__(self):
        self.api = PosterControlAPI()

    async def run_abc_analysis(self, days: int = 30) -> Dict[str, List[Dict[str, Any]]]:
        """Асинхронний ABC-аналіз меню (STARS, PLOWHORSES, PUZZLES, DOGS)."""
        date_to = datetime.now().strftime('%Y%m%d')
        date_from = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        logger.info(f"Running Async ABC analysis for {days} days...")
        
        # 1. Отримуємо транзакції та меню паралельно
        transactions, all_products = await asyncio.gather(
            self.api.get_transactions(date_from=date_from, date_to=date_to),
            self.api.get_menu_products()
        )
        
        if not transactions or not all_products:
            logger.warning("No data for ABC analysis.")
            return {}

        # 2. Мапимо продукти для швидкого доступу до собівартості та імен
        product_map = {
            str(p['product_id']): {
                'name': p['product_name'],
                'cost': float(p.get('cost', 0)) / 100,
                'weight_flag': p.get('weight_flag') == '1'
            } for p in all_products
        }

        # 3. Отримуємо деталі кожної транзакції паралельно (з лімітом)
        semaphore = asyncio.Semaphore(15) # Більше паралелізму для швидкості
        
        async def fetch_tx_products(tid):
            async with semaphore:
                return await self.api.get_transaction_products(tid)

        tasks = [fetch_tx_products(t['transaction_id']) for t in transactions if t.get('transaction_id')]
        results_tx = await asyncio.gather(*tasks)

        # 4. Агрегація продажів
        sales_summary = {} # pid -> {qty, revenue, tx_count}
        total_receipts = len(transactions)
        
        for prods in results_tx:
            if not prods: continue
            seen_in_this_tx = set()
            for p in prods:
                pid = str(p['product_id'])
                qty = float(p.get('num', 0))
                rev = float(p.get('payed_sum', 0)) / 100
                
                if pid not in sales_summary:
                    sales_summary[pid] = {'qty': 0, 'revenue': 0, 'tx_count': 0}
                
                sales_summary[pid]['qty'] += qty
                sales_summary[pid]['revenue'] += rev
                if pid not in seen_in_this_tx:
                    sales_summary[pid]['tx_count'] += 1
                    seen_in_this_tx.add(pid)

        # 5. Розрахунок метрик та класифікація
        items = []
        total_profit = 0
        
        for pid, data in sales_summary.items():
            p_info = product_map.get(pid)
            if not p_info: continue
            
            qty = data['qty']
            revenue = data['revenue']
            
            # Враховуємо вагові товари (Poster зберігає ціну за кг, але в транзакціях кількість у грамах)
            if p_info['weight_flag']:
                total_cost = (qty / 1000) * p_info['cost']
            else:
                total_cost = qty * p_info['cost']
                
            profit = revenue - total_cost
            frequency_pct = (data['tx_count'] / total_receipts) * 100 if total_receipts > 0 else 0
            
            if qty <= 0: continue
            
            items.append({
                'id': pid,
                'name': p_info['name'],
                'qty': qty,
                'profit': profit,
                'frequency_pct': frequency_pct,
                'weight_flag': p_info['weight_flag']
            })
            total_profit += profit

        if not items: return {}

        # 6. Визначення порогів (Середні значення)
        avg_profit = total_profit / len(items)
        avg_freq = sum(i['frequency_pct'] for i in items) / len(items)

        results = {"STARS": [], "PLOWHORSES": [], "PUZZLES": [], "DOGS": []}
        
        for item in items:
            high_profit = item['profit'] >= avg_profit
            high_freq = item['frequency_pct'] >= avg_freq
            
            if high_profit and high_freq: results["STARS"].append(item)
            elif not high_profit and high_freq: results["PLOWHORSES"].append(item)
            elif high_profit and not high_freq: results["PUZZLES"].append(item)
            else: results["DOGS"].append(item)

        # Сортування для звіту
        for k in results:
            results[k] = sorted(results[k], key=lambda x: x['profit'], reverse=True)
            
        return results
