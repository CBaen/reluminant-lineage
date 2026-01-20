# BASIC OPTIONS STRATEGIES - COMPREHENSIVE RESEARCH

## 1. LONG CALLS

### When to Use
- Bullish outlook with limited risk
- Expecting significant upside move
- Lower capital requirement vs stock purchase
- High volatility scenarios

### Risk/Reward Profile
- **Maximum Loss**: Premium paid (limited)
- **Maximum Gain**: Unlimited
- **Breakeven**: Strike Price + Premium Paid
- **Risk/Reward Ratio**: Asymmetric positive

### Mechanics
- Buy call option at strike price X
- Pay upfront premium (cost of entry)
- Profit when stock > Strike + Premium
- Value increases with stock price, volatility, time remaining

### Greeks Impact
- **Delta**: Increases as stock moves up (0 to 1.0)
- **Gamma**: Highest at-the-money, accelerates delta changes
- **Theta**: Negative (time decay works against you)
- **Vega**: Positive (benefits from volatility increase)

### Examples & Calculations
Stock at $100, buy $105 call for $2.50 premium
- Max loss: $2.50 per share = $250
- Breakeven: $107.50
- Profit if stock > $107.50
- Margin requirement: Minimal

### Entry & Exit Signals
- Entry: Stock at support, technical breakout, earnings catalyst
- Exit: 50-75% of max profit, stop loss at 30% premium loss, expiration approach

---

## 2. LONG PUTS

### When to Use
- Bearish outlook with limited risk
- Expecting significant downside move
- Hedging long stock position
- High volatility with downside expectation

### Risk/Reward Profile
- **Maximum Loss**: Premium paid (limited)
- **Maximum Gain**: Strike Price - Premium Paid
- **Breakeven**: Strike Price - Premium Paid
- **Risk/Reward Ratio**: Asymmetric (capped upside)

### Mechanics
- Buy put option at strike price X
- Pay upfront premium
- Profit when stock < Strike - Premium
- Value increases with stock price decline, volatility, time remaining

### Greeks Impact
- **Delta**: Becomes more negative as stock declines (-1.0 to 0)
- **Gamma**: Highest at-the-money
- **Theta**: Negative (time decay hurts position)
- **Vega**: Positive (benefits from volatility increase)

### Examples & Calculations
Stock at $100, buy $95 put for $2.50 premium
- Max loss: $2.50 per share = $250
- Max gain: $92.50 per share = $9,250
- Breakeven: $92.50
- Profit if stock < $92.50

### Entry & Exit Signals
- Entry: Stock at resistance, technical breakdown, earnings uncertainty
- Exit: 50-75% of max profit, stop loss, expiration management

---

## 3. COVERED CALLS

### Setup Requirements
- Own underlying stock (100 shares minimum per contract)
- Sell (write) call option against stock position
- Stock fully "covers" the call obligation

### Income Generation Mechanics
- Collect call premium upfront
- Generate income from stock appreciation up to strike
- Can repeat (rolling) monthly for recurring income
- Typically sell near-term (30-45 days to expiration)

### Assignment Risk
- Assignment occurs if stock rises above strike at expiration
- Stock called away at strike price (may miss additional upside)
- Opportunity cost if stock significantly rallies
- Can prevent with rolling before expiration

### Rolling Strategies
- **Roll up/out**: Buy back call, sell higher strike further out
- **Roll out**: Extend expiration, keep same strike
- **Roll down/out**: Buy back call, sell lower strike further out
- Timing: When stock approaches strike (2-3 weeks before expiration)

### Income Optimization
- Select strike price between 5-15% out-of-the-money
- Typically yields 1-2% monthly (12-24% annualized)
- More premium for higher volatility
- Balance income vs upside capture

### Opportunity Cost & Tax Treatment
- Miss upside beyond strike price if assigned
- Premium reduces cost basis (improves tax efficiency on stock sale)
- If assigned: long-term capital gains treatment if held >1 year
- Premium income treated as short-term gains initially
- Holding period reset with assignment (new cost basis)

---

## 4. PROTECTIVE PUTS

### Portfolio Insurance Mechanics
- Own stock (bullish)
- Buy put option to protect downside
- Establishes floor price
- Maintain stock ownership and upside

### Cost Considerations
- Put premium is insurance cost (reduces net returns)
- Out-of-the-money puts cheaper (higher risk)
- At-the-money puts expensive (full protection)
- Best for 20%+ expected downside risk

### Protective Collar Strategy
- Own stock
- Buy put at lower strike (downside protection)
- Sell call at higher strike (cap upside)
- Call premium offsets put cost
- Creates defined risk zone

### When to Use
- Holding concentrated position
- Expecting volatility or uncertainty
- Before earnings announcements
- In bearish market conditions
- For capital preservation

### Profitability Analysis
- Profit: Stock gains above put strike minus premiums paid
- Loss: Limited to put strike price
- Breakeven: Stock price + net premium paid
- Best outcome: Stock rises, expires worthless (keep premium difference)

---

## 5. CASH-SECURED PUTS

### Setup Requirements
- Maintain cash equal to (Strike × 100) in account
- Sell put option at chosen strike
- Cash secures assignment obligation
- No margin required (fully secured)

### Assignment Willingness
- Collected premium is benefit for accepting assignment
- Assignment means buying 100 shares at strike price
- Willing to own stock at strike price + premium discount
- Used as entry strategy for stocks you want to own

### Capital Tie-Up Considerations
- Cash reserved but available
- Earn premium while waiting
- If assigned, cash converts to stock
- Can recycle with rolling (sell new put against same cash)

### The Wheel Strategy
1. **Sell cash-secured put** → Collect premium
2. **Assignment** → Own stock at lower price
3. **Sell covered call** → Generate income
4. **Assignment** → Stock called away at profit
5. **Repeat** → Cycle continues

### Wheel Strategy Profitability
- Per cycle: Put premium + Call premium - Slippage
- Annual cycles if repeated monthly
- 15-25% annualized returns possible
- Requires patience and adequate capital
- Works in range-bound markets

### Capital Requirements for Wheel
- Minimum per cycle: Strike price × 100
- Can manage multiple cycles with adequate capital
- Example: $10,000 cash → run two cycles simultaneously

---

## 6. MARRIED PUTS

### Combining Stock & Put Protection
- Buy 100 shares of stock at market price
- Simultaneously buy put at chosen strike
- Acts as insurance for stock position
- Creates defined maximum loss

### Cost vs Protective Puts
- Same protection outcome as protective puts
- Different tax treatment (IRS "married put" rule)
- Cost: Stock purchase + put premium
- More expensive than buying stock alone + later buying put

### Tax Implications (Married Put Rule)
- If loss position held, cannot deduct put premium
- Put cost must reduce stock cost basis instead
- Holding period for stock + put tied together
- Wash sale rules still apply
- Long-term treatment if combined holding > 1 year

### When to Use
- New position entry with built-in protection
- High-conviction bullish with protection
- Volatile stock purchase
- Avoiding assignment surprise

---

## 7. SYNTHETIC POSITIONS

### Synthetic Long
**Method A: Long Call + Short Stock**
- Buy call at strike X
- Short sell 100 shares
- Effectively creates long stock position
- Unlimited upside, defined downside

**Method B: Long Stock + Short Put**
- Own 100 shares
- Sell put at strike X
- Similar to synthetic long
- More capital efficient than stock ownership

### Synthetic Short
**Long Put + Long Stock**
- Buy put at strike X
- Own 100 shares
- Protects downside, creates bearish payoff
- Actually protective put (covered put behavior)

### Conversion Arbitrage
- Long stock + Long put + Short call (same strike)
- Creates risk-free position if spread mispriced
- Strike price becomes guaranteed sale price
- Exploits volatility mispricing
- Requires deep option liquidity

### Tax Implications
- Synthetic positions treated as constructive sales
- Can trigger capital gains if original stock position has gains
- Must hold >30 days apart to avoid wash sale issues
- Consult tax professional before implementation

---

## 8. DECISION FRAMEWORK - WHICH STRATEGY?

### By Market View

**Bullish View**
- Bullish + Limited capital → Long call
- Bullish + Own stock → Covered call (income)
- Bullish + Downside risk → Protective put or Collar
- Bullish + Entry point → Cash-secured put (enter on dip)

**Bearish View**
- Bearish + Limited capital → Long put
- Bearish + Own stock → Protective put (hedge)
- Bearish + Want downside → Synthetic short

**Neutral View**
- Neutral + Generate income → Covered call, Cash-secured put
- Neutral + Range-bound → Wheel strategy
- Neutral + Own stock → Covered call (recurring income)

### By Volatility Regime

**High Volatility**
- Sell strategies more attractive (collect premium)
- Covered calls more profitable
- Cash-secured puts more attractive yields
- Long options more expensive (reduce buying)

**Low Volatility**
- Buy strategies more attractive (cheaper premiums)
- Sell strategies less attractive (low premium)
- Covered call yields reduced
- Good time for protective puts

### By Time Horizon

**Days/Weeks (Short-term)**
- Long calls/puts for fast moves
- Focus on technical setup
- Theta decay accelerates risk
- Tight stop losses required

**Weeks/Months (Medium-term)**
- Covered calls (30-45 day expirations)
- Cash-secured puts (recurring income)
- Wheel strategy
- Better theta profile

**Months+ (Long-term)**
- Protective puts/collars
- Married puts for new position entry
- Buy-and-hold covered calls
- Quarterly rolling strategies

---

## 9. ENTRY & EXIT TIMING

### Entry Signals
- **Technical**: Support bounce, breakout, moving average crossover
- **Volatility**: Entry on IV spike down (better prices)
- **Catalyst**: Earnings pre-announcement, economic data
- **Fundamental**: Valuation attractive, support level identified
- **Volume**: Confirm with above-average volume

### Exit Signals - Profit Taking
- **50% rule**: Exit at 50% of max profit (best for directional plays)
- **75% rule**: Exit at 75% of max profit (more conservative)
- **Target price**: Exit when stock reaches technical target
- **Time-based**: Exit 2 weeks before expiration (theta accelerates)

### Exit Signals - Stop Loss
- **Dollar loss**: Exit if lose 30-50% of premium paid
- **Technical break**: Stop below key technical level
- **Time**: Exit if position unchanged after timeframe expires
- **Volatility**: Exit if IV drops significantly (premium evaporates)

### Rolling Mechanics
- **When**: 2-4 weeks before expiration
- **Method**: Buy to close, sell to open new position
- **Adjustments**: Roll up/out (bullish), out only (neutral), down/out (bearish)
- **Profit tracking**: Each roll is separate P&L event
- **Frequency**: Monthly typical for income strategies

### Expiration Management
- **In-the-money calls**: Roll or accept assignment
- **Out-of-the-money calls**: Let expire worthless (keep premium)
- **In-the-money puts**: Roll or accept assignment
- **Out-of-the-money puts**: Let expire worthless (keep premium)
- **Week of expiration**: Avoid holding near expiration (gamma risk)

---

## 10. POSITION SIZING FOR BASIC STRATEGIES

### Risk Management Framework
- Risk per trade: 1-2% of total portfolio
- Position size based on worst-case scenario
- Account for maximum loss, not margin requirement
- Scale based on confidence and setup quality

### For Long Calls/Puts
- Premium paid = maximum risk
- Size: (Account × Risk %) / Premium paid
- Example: $50,000 account, 1% risk = $500 max loss
- $2.50 premium = 20 contracts maximum

### For Covered Calls
- Stock position size = primary consideration
- Premium collected = secondary income
- Covered call capital = 100 × strike price per contract
- Example: 1000 shares = 10 covered calls maximum

### For Protective Puts
- Match to stock position size
- Put cost reduces capital efficiency
- Collar balances cost with protection
- Size: 1 put per 100 shares of stock

### For Cash-Secured Puts
- Capital requirement: Strike × 100 per contract
- Portfolio allocation: 5-10% per position
- Multiple contracts: Size based on total portfolio
- Example: $100,000 account → 5-10 contracts maximum

### For Wheel Strategy
- Per-cycle capital: Strike × 100
- Simultaneous cycles: Total capital ÷ strike price
- Monitor capital efficiency
- Reinvest freed capital in new cycles

### Leverage Considerations
- Margin not recommended for basic strategies
- Cash-secured puts naturally cap exposure
- Covered calls fully backed by stock
- Excess leverage creates ruin risk

---

## 11. TAX IMPLICATIONS

### Wash Sale Rules
- Cannot harvest losses if bought within 30 days before/after
- Applies to covered calls on underwater positions
- "Substantially identical" includes same stock/options
- Disallowed loss adds to new position cost basis
- Applies: Options bought 30 days before, during, and after stock sale

### Example Wash Sale Scenario
1. Buy 100 shares at $100 = $10,000 cost basis
2. Stock drops to $85 = $1,500 loss
3. Sell stock, realize loss
4. Can't buy put within 30 days (extends holding period)
5. Can't sell covered call within 30 days (lock-in mechanism)

### Long-term vs Short-term Capital Gains
- **Long-term** (>1 year holding): 0-20% federal tax (15% typical for high earners)
- **Short-term** (<1 year): Ordinary income tax rates (up to 37%)
- Significant tax difference: 35% differential possible
- Plan holding periods accordingly

### Covered Call Tax Treatment
- Premium collected = short-term income initially
- If assigned: Sale price at strike (not market price)
- Holding period resets with assignment (new cost basis)
- If stock held long-term: Assignment = long-term sale
- Must hold stock > 1 year before call assignment for LTCG

### Protective & Married Puts
- **Protective Put**: Premium is deductible if held for income
- **Married Put**: Premium becomes part of stock cost basis (IRS rule)
- Married puts cannot deduct loss if position goes underwater
- Holding period extends until put expires or exercises

### Cash-Secured Put Assignment
- Assignment triggers stock purchase at strike
- Stock cost basis = strike price + slippage costs
- Holding period starts from assignment date
- Premium collected reduces effective cost basis

### Wheel Strategy Tax Optimization
- Put premium: Short-term income
- Call premium: Short-term income (if assigned within year)
- Stock assignment: New holding period starts
- If stock held >1 year before assignment: LTCG treatment
- Can manipulate timing to optimize tax efficiency

### Documentation Requirements
- Track all open/close dates precisely
- Record P&L separately for each position
- Note assignment dates (start new holding period)
- Maintain premium received/paid records
- Consider Form 8949 complexity with active trading

### Section 1256 Contracts (Advanced)
- Not applicable to equity options in basic strategies
- Index options (SPX, RUT) get special treatment: 60/40 LTCG
- Only relevant for index option strategies
- Can be tax efficient but adds complexity

---

## 12. COMPARING STRATEGIES - QUICK REFERENCE

| Strategy | Capital | Max Loss | Max Gain | When Use | Complexity |
|----------|---------|----------|----------|----------|------------|
| Long Call | Premium | Premium | Unlimited | Bullish, limited capital | Low |
| Long Put | Premium | Premium | Strike-Premium | Bearish, limited capital | Low |
| Covered Call | 100×Strike | Premium | Premium | Own stock, income | Low-Med |
| Protective Put | 100×Strike + Put | Put Premium | Unlimited | Hedge long | Medium |
| Cash-Sec Put | 100×Strike | Strike-Premium | Premium | Want to buy stock | Low-Med |
| Married Put | 100×Stock + Put | Put Premium | Unlimited | Entry with protection | Medium |
| Synthetic Long | Call + Short | Unlimited | Unlimited | Capital efficient long | High |
| Wheel | 100×Strike | Strike-Premium | Premium/cycle | Recurring income | Medium |

---

## IMPLEMENTATION CHECKLIST

### Before Entry
- [ ] Defined market view and timeframe
- [ ] Strike selection justified
- [ ] Expiration chosen (avoid earnings)
- [ ] Position size calculated (1-2% risk max)
- [ ] Exit plan established (profit target & stop loss)
- [ ] Checked technical support/resistance
- [ ] Confirmed adequate liquidity (bid-ask spread)

### During Position
- [ ] Monitor daily P&L and Greeks
- [ ] Track days to expiration
- [ ] Prepare for rolling if needed
- [ ] Adjust if underlying moves significantly
- [ ] Avoid holding into expiration week

### At Exit
- [ ] Close or roll before decay accelerates
- [ ] Record all P&L for tax purposes
- [ ] Document assignment if applicable
- [ ] Track holding periods for tax optimization
- [ ] Review trade for lessons learned
