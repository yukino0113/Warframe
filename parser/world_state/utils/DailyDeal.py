from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class DailyDeal:
    activation: int
    amount_sold: int
    amount_total: int
    discount: int
    expiry: int
    original_prize: int
    sale_prize: int
    store_item: str

    @classmethod
    def parse_daily_deal(cls, deal_json: Dict[str, Any]) -> 'DailyDeal':
        return cls(
            activation=int(deal_json['Activation']['$date']['$numberLong']),
            amount_sold=deal_json.get('AmountSold', 0),
            amount_total=deal_json.get('AmountTotal', 0),
            discount=deal_json.get('Discount', 0),
            expiry=int(deal_json['Expiry']['$date']['$numberLong']),
            original_prize=deal_json.get('Originalprize', 0),
            sale_prize=deal_json.get('Saleprize', 0),
            store_item=deal_json.get('StoreItem', '')
        )
