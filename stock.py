import datetime
import math

BUY = "BUY"
SELL = "SELL"


class Trade:
    """Represents a single trade transaction."""
    
    def __init__(self, timestamp, quantity, indicator, price):
        if quantity <= 0 or price <= 0:
            raise ValueError("Trade quantity and price must be positive.")
        self.timestamp = timestamp
        self.quantity = quantity
        self.indicator = indicator
        self.price = price

    def __repr__(self):
        return (f"Trade(time={self.timestamp}, qty={self.quantity}, "
                f"type={self.indicator}, price={self.price})")


class Stock:
    """
    Base class for a stock.
    Subclasses must implement dividend/yield calculations.
    """
    def __init__(self, symbol, par_value):
        self.symbol = symbol
        self.par_value = par_value
        self.trades = []

    def get_dividend(self):
        """Returns the dividend value used for P/E ratio."""
        raise NotImplementedError

    def calculate_dividend_yield(self, price):
        """Calculates the dividend yield for a given price."""
        raise NotImplementedError

    def calculate_pe_ratio(self, price):
        """Calculates the P/E Ratio for a given price."""
        if price <= 0:
            return None
        
        dividend = self.get_dividend()
        
        if dividend == 0:
            return None
            
        return price / dividend

    def record_trade(self, quantity, indicator, price):
        """Records a new trade for this stock."""
        trade = Trade(
            timestamp=datetime.datetime.now(),
            quantity=quantity,
            indicator=indicator,
            price=price
        )
        self.trades.append(trade)
        return trade

    def calculate_volume_weighted_stock_price(self):
        """
        Calculates the VWSP based on trades in the past 5 minutes.
        """
        now = datetime.datetime.now()
        cutoff_time = now - datetime.timedelta(minutes=5)
        
        recent_trades = [t for t in self.trades if t.timestamp >= cutoff_time]
        
        if not recent_trades:
            return None

        total_value = 0.0
        total_quantity = 0
        
        for trade in recent_trades:
            total_value += trade.price * trade.quantity
            total_quantity += trade.quantity
        
        if total_quantity == 0:
            return None
            
        return total_value / total_quantity

    def __repr__(self):
        return f"Stock('{self.symbol}')"


class CommonStock(Stock):
    """Represents a Common stock."""
    
    def __init__(self, symbol, par_value, last_dividend):
        super().__init__(symbol, par_value)
        self.last_dividend = last_dividend

    def get_dividend(self):
        return self.last_dividend

    def calculate_dividend_yield(self, price):
        if price <= 0:
            return None
        return self.last_dividend / price


class PreferredStock(Stock):
    """Represents a Preferred stock."""
    
    def __init__(self, symbol, par_value, last_dividend, fixed_dividend_rate):
        super().__init__(symbol, par_value)
        self.last_dividend = last_dividend
        self.fixed_dividend_rate = fixed_dividend_rate

    def get_dividend(self):
        return self.fixed_dividend_rate * self.par_value

    def calculate_dividend_yield(self, price):
        if price <= 0:
            return None
        return (self.fixed_dividend_rate * self.par_value) / price


# --- Exchange Class ---

class StockExchange:
    """Manages all stocks and calculates the All Share Index."""
    
    def __init__(self):
        self.stocks = {}

    def add_stock(self, stock):
        self.stocks[stock.symbol] = stock

    def get_stock(self, symbol):
        return self.stocks.get(symbol)

    def calculate_gbce_all_share_index(self):
        """Calculates the GBCE All Share Index using geometric mean."""
        vwsp_values = []
        for stock in self.stocks.values():
            vwsp = stock.calculate_volume_weighted_stock_price()
            if vwsp is not None and vwsp > 0:
                vwsp_values.append(vwsp)
        
        if not vwsp_values:
            return None 

        n = len(vwsp_values)
        product = 1.0
        for val in vwsp_values:
            product *= val
            
        return product ** (1.0 / n)


# --- Demo Function to Prove Requirements ---

def main():
    """Runs a demo of all features."""
    
    print("--- Initializing GBCE ---")
    gbce = StockExchange()
    
    gbce.add_stock(CommonStock(symbol="TEA", par_value=100, last_dividend=0))
    gbce.add_stock(CommonStock(symbol="POP", par_value=100, last_dividend=8))
    gbce.add_stock(CommonStock(symbol="ALE", par_value=60, last_dividend=23))
    gbce.add_stock(PreferredStock(symbol="GIN", par_value=100, last_dividend=8, fixed_dividend_rate=0.02))
    gbce.add_stock(CommonStock(symbol="JOE", par_value=250, last_dividend=13))
    
    print(f"Stocks loaded: {list(gbce.stocks.keys())}")

    print("\n--- Yield and P/E Ratio Calculations (Price = 110p) ---")
    price = 110.0
    
    stock_pop = gbce.get_stock("POP")
    print(f"POP Yield: {stock_pop.calculate_dividend_yield(price):.4f}")
    print(f"POP P/E:   {stock_pop.calculate_pe_ratio(price):.2f}")
    
    stock_gin = gbce.get_stock("GIN")
    print(f"GIN Yield: {stock_gin.calculate_dividend_yield(price):.4f}")
    print(f"GIN P/E:   {stock_gin.calculate_pe_ratio(price):.2f}")

    print("\n--- Trade Recording & VWSP (for ALE) ---")
    stock_ale = gbce.get_stock("ALE")
    
    # Old trade (won't be in VWSP)
    trade_old = stock_ale.record_trade(50, BUY, 65)
    trade_old.timestamp = datetime.datetime.now() - datetime.timedelta(minutes=6)
    
    # Recent trades
    stock_ale.record_trade(100, BUY, 70)
    stock_ale.record_trade(50, SELL, 72)
    
    vwsp_ale = stock_ale.calculate_volume_weighted_stock_price()
    print(f"ALE VWSP (past 5 min): {vwsp_ale:.4f}")

    print("\n--- GBCE All Share Index ---")
    # Add trades for other stocks
    gbce.get_stock("TEA").record_trade(1000, BUY, 98)
    gbce.get_stock("POP").record_trade(500, SELL, 122)
    gbce.get_stock("GIN").record_trade(200, BUY, 105)
    gbce.get_stock("JOE").record_trade(300, SELL, 240)
    
    gbce_index = gbce.calculate_gbce_all_share_index()
    print(f"\nGBCE All Share Index (Geometric Mean): {gbce_index:.4f}")


if __name__ == "__main__":
    main()