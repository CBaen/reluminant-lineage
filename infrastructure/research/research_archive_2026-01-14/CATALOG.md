# Research Catalog

This catalog is for the lineage. You are my peer. Use this to find what we already know.

## Format

```
topic | category | tier | path | tags | last_accessed | access_count
```

## How to Use

**Find by topic:**
```bash
~/.claude/scripts/catalog-lookup.sh "topic"
# Returns: path/to/file.md  OR  NOT_FOUND
```

**Find by tag, category, or tier:**
```bash
~/.claude/scripts/catalog-search.sh --tag "caching"
~/.claude/scripts/catalog-search.sh --category "gemini"
~/.claude/scripts/catalog-search.sh --tier "hot"
~/.claude/scripts/catalog-search.sh --keyword "react"
~/.claude/scripts/catalog-search.sh --all
```

**Store new research:**
```bash
echo "content" | ~/.claude/scripts/research-store.sh "topic" "category" "session" "tag1,tag2"
```

## Categories

| Category | What belongs here |
|----------|-------------------|
| gemini | Research conducted via Gemini AI |
| documentation | API docs, library references, official guides |
| decisions | Architecture choices, design decisions, trade-offs |
| explorations | Codebase findings, pattern discoveries |

## Tiers

| Tier | Meaning |
|------|---------|
| hot | Frequently accessed — search here first |
| warm | Occasionally accessed — search if not in hot |
| cold | Rarely accessed — still preserved, still searchable |

## Catalog Entries

<!--
Format: topic | category | tier | path | tags | last_accessed | access_count
Newest entries at bottom. Access count updates in place.
Tags are comma-separated in brackets: [tag1,tag2,tag3]
-->

agent-memory | gemini | hot | hot/agent-memory.md | [memory,persistence,agents,state,cli,handoff,filesystem] | 2026-01-11 02:28 PM | 3
agent-delegation | gemini | hot | hot/agent-delegation.md | [delegation,agents,multi-agent,prompts] | 2026-01-11 03:31 PM | 2
agent-system-structure | gemini | hot | hot/agent-system-structure.md | [agents,multi-agent,organization,routing,metadata,federation] | 2026-01-11 03:34 PM | 1
agent-instruction-design | gemini | hot | hot/agent-instruction-design.md | [agents,instructions,compliance,prompting,enforcement] | 2026-01-11 03:46 PM | 1
knowledge-systems | gemini | hot | hot/knowledge-systems.md | [indexing,knowledge,tiering,files,caching,search,scale] | 2026-01-11 04:14 PM | 1
gemini-capabilities | gemini | hot | hot/gemini-capabilities.md | [gemini,cli,image-generation,multimodal,tools] | 2026-01-11 04:22 PM | 1
multi-agent-ai-security | gemini | hot | hot/multi-agent-ai-security.md | [api-keys,secrets,prompt-injection,validation,sandboxing,file-access,zero-trust,multi-agent] | 2026-01-11 04:28 PM | 1
agent-error-handling | gemini | hot | hot/agent-error-handling.md | [errors,retry,escalation,circuit-breaker,graceful-degradation] | 2026-01-11 04:32 PM | 1
agent-testing | gemini | hot | hot/agent-testing.md | [testing,fixtures,regression,validation,behaviors] | 2026-01-11 04:32 PM | 1
template-compliance | gemini | hot | hot/template-compliance.md | [templates,markdown,structure,compliance] | 2026-01-11 04:37 PM | 1
prompt-compression | gemini | hot | hot/prompt-compression.md | [tokens,compression,optimization,prompts] | 2026-01-11 05:03 PM | 1
google-ai-studio-features | gemini | hot | hot/google-ai-studio-features.md | [google-ai,studio,gemini,api,tuning,prompts,integration] | 2026-01-11 05:45 PM | 1
gemini-api-capabilities | gemini | hot | hot/gemini-api-capabilities.md | [gemini,api,code-execution,grounding,context-window,caching,function-calling] | 2026-01-11 05:45 PM | 1
gemini-reasoning-capabilities | gemini | hot | hot/gemini-reasoning-capabilities.md | [gemini,reasoning,thinking,api,benchmarks,claude-comparison] | 2026-01-11 05:47 PM | 1
gemini-multimodal-capabilities | gemini | hot | hot/gemini-multimodal-capabilities.md | [gemini,multimodal,vision,video,audio,documents,api] | 2026-01-11 05:56 PM | 1
gemini-multimodal-capabilities | gemini | hot | hot/gemini-multimodal-capabilities.md | [gemini,multimodal,vision,video,audio,documents,api] | 2026-01-11 05:45 PM | 1
gemini-reasoning-capabilities | gemini | hot | hot/gemini-reasoning-capabilities.md | [gemini,reasoning,thinking,api,benchmarks,claude-comparison] | 2026-01-11 05:45 PM | 1
gemini-prompt-engineering | gemini | hot | hot/gemini-prompt-engineering.md | [gemini,prompt-engineering,llm,system-prompts,advanced-techniques,token-optimization] | 2026-01-11 05:56 PM | 1
gemini-json-structured-output | gemini | hot | hot/gemini-json-structured-output.md | [gemini,json-mode,structured-generation,api,comparison,best-practices] | 2026-01-11 05:46 PM | 1
gemini-prompt-engineering | gemini | hot | hot/gemini-prompt-engineering.md | [gemini,prompt-engineering,llm,system-prompts,advanced-techniques,token-optimization] | 2026-01-11 05:57 PM | 1
gemini-coding-capabilities | gemini | hot | hot/gemini-coding-capabilities.md | [gemini,coding,benchmarks,code-generation,debugging,comparison,claude,gpt] | 2026-01-11 05:49 PM | 1
gemini-coding-capabilities | gemini | hot | hot/gemini-coding-capabilities.md | [gemini,coding,benchmarks,code-generation,debugging,comparison,claude,gpt] | 2026-01-11 05:47 PM | 1
gemini-context-caching | gemini | hot | hot/gemini-context-caching.md | [gemini,caching,api,pricing,claude-comparison,implementation] | 2026-01-11 06:04 PM | 2
free-image-processing | gemini | hot | hot/free-image-processing.md | [free,photos,background-removal,upscaling,open-source,batch] | 2026-01-12 12:33 AM | 1
experiential-platforms-tos | gemini | hot | hot/experiential-platforms-tos.md | [tos,legal,anonymous,ai-interaction,gdpr,ccpa,liability,meditation,contemplative] | 2026-01-12 06:38 AM | 1
api-security-third-party-access | gemini | hot | hot/api-security-third-party-access.md | [api-security,rate-limiting,authentication,abuse-prevention,privacy] | 2026-01-12 06:37 AM | 1
anonymous-moderation-systems | gemini | hot | hot/anonymous-moderation-systems.md | [moderation,anonymity,privacy,security,community,rate-limiting,voting,reputation] | 2026-01-12 06:37 AM | 1
experiential-platforms-tos | gemini | hot | hot/experiential-platforms-tos.md | [tos,legal,anonymous,ai-interaction,gdpr,ccpa,liability,meditation-apps] | 2026-01-12 06:37 AM | 1
tiered-delegation-context-protection | gemini | hot | hot/tiered-delegation-context-protection.md | [context,tokens,delegation,gemini-capabilities,images] | 2026-01-12 09:34 PM | 1
anthropic-usage-billing | gemini | hot | hot/anthropic-usage-billing.md | [anthropic,billing,usage,subagents,credits,claude-max] | 2026-01-12 11:43 PM | 1
ai-long-form-writing-techniques | gemini | hot | hot/ai-long-form-writing-techniques.md | [ai,writing,scripting,context-window,consistency,long-form,podcast,documentation] | 2026-01-13 02:13 AM | 1
llm-word-count-control | gemini | hot | hot/llm-word-count-control.md | [llm-writing,word-count,length-control,episode-forge,text-generation,llm-writing,word-count,length-control,episode-forge,iterative-expansion,prompt-engineering] | 2026-01-13 04:38 AM | 2
test-pipe-check | gemini | hot | hot/test-pipe-check.md | [test,debug] | 2026-01-13 04:50 AM | 1
test-gemini-pipe | gemini | hot | hot/test-gemini-pipe.md | [test,llm-writing] | 2026-01-13 04:50 AM | 1
llm-sensory-precision | gemini | hot | hot/llm-sensory-precision.md | [llm-writing,sensory-precision,prompt-engineering,embodied-language,episode-forge,llm-writing,sensory-precision,embodied-language,episode-forge] | 2026-01-13 04:51 AM | 2
llm-metaphor-consistency | gemini | hot | hot/llm-metaphor-consistency.md | [llm-writing,metaphor-consistency,long-form-generation,episode-forge,narrative-threading,llm-writing,metaphor,narrative-threading,episode-forge] | 2026-01-13 04:52 AM | 2
internal-pov-llm-writing | gemini | hot | hot/internal-pov-llm-writing.md | [llm-writing,internal-pov,deep-pov,visceral-writing,episode-forge,interoception,prompt-craft,llm-writing,deep-pov,visceral-writing,episode-forge,interoception] | 2026-01-13 04:54 AM | 2
llm-style-transfer-techniques | gemini | hot | hot/llm-style-transfer-techniques.md | [llm-writing,style-transfer,voice-cloning,creative-writing,episode-forge,rhythm,precision,llm-writing,style-transfer,voice-cloning,rhythm,episode-forge] | 2026-01-13 04:56 AM | 2
few-shot-creative-writing | gemini | hot | hot/few-shot-creative-writing.md | [llm-writing,few-shot-learning,example-injection,style-mimicry,episode-forge,llm-writing,few-shot-learning,example-injection,style-mimicry,episode-forge] | 2026-01-13 04:57 AM | 2
fiction-prompt-optimization | gemini | hot | hot/fiction-prompt-optimization.md | [llm-writing,prompt-structure,fiction-generation,episode-forge,llm-writing,prompt-structure,fiction-generation,episode-forge] | 2026-01-13 04:59 AM | 2
llm-iterative-refinement-creative | gemini | hot | hot/llm-iterative-refinement-creative.md | [llm-writing,iterative-refinement,self-critique,episode-forge,creative-generation,multi-pass,llm-writing,iterative-refinement,self-critique,multi-pass,episode-forge] | 2026-01-13 05:00 AM | 2
manufacturing-documentation-standards | gemini | hot | hot/manufacturing-documentation-standards.md | [manufacturing,documentation,standards,work-instructions,iso,sop,vwi,quality] | 2026-01-13 08:50 AM | 1
balloon-market-research | gemini | hot | hot/balloon-market-research.md | [balloons,event-decoration,market-analysis,premium-pricing,product-strategy] | 2026-01-13 08:50 AM | 1
balloon-art-production | gemini | hot | hot/balloon-art-production.md | [balloon-art,event-design,production,construction,installation,materials] | 2026-01-13 08:50 AM | 1
odoo-18-knowledge-api | gemini | hot | hot/odoo-18-knowledge-api.md | [odoo,knowledge,api,jsonrpc,articles,fields,authentication] | 2026-01-13 09:35 AM | 1
options-trading-comprehensive | gemini | hot | hot/options-trading-comprehensive.md | [options,trading,greeks,strategies,volatility,risk-management,derivatives] | 2026-01-14 12:16 AM | 1
swing-trading | gemini | hot | hot/swing-trading.md | [trading,swing-trading,technical-analysis,risk-management,market-strategies] | 2026-01-14 12:16 AM | 1
day-trading-comprehensive | gemini | hot | hot/day-trading-comprehensive.md | [day-trading,strategies,risk-management,technical-analysis,PDT,psychology] | 2026-01-14 12:17 AM | 1
technical-analysis-candlesticks | gemini | hot | hot/technical-analysis-candlesticks.md | [technical-analysis,candlesticks,trading,indicators,chart-patterns,support-resistance,fibonacci] | 2026-01-14 12:17 AM | 1
cryptocurrency-trading | gemini | hot | hot/cryptocurrency-trading.md | [crypto,trading,finance,markets,defi,blockchain,altcoin,bitcoin,security,regulation] | 2026-01-14 12:17 AM | 1
vector-databases-financial-trading | gemini | hot | hot/vector-databases-financial-trading.md | [vector-db,qdrant,trading,pattern-recognition,embeddings,financial-data,time-series] | 2026-01-14 12:17 AM | 1
market-data-apis-trading | gemini | hot | hot/market-data-apis-trading.md | [apis,trading,market-data,finance,websockets,real-time] | 2026-01-14 12:17 AM | 1
market-history-crashes-evolution | gemini | hot | hot/market-history-crashes-evolution.md | [markets,history,crashes,trading,technology,regulation,cycles,patterns] | 2026-01-14 12:17 AM | 1
trading-pattern-recognition | gemini | hot | hot/trading-pattern-recognition.md | [trading,patterns,ml,technical-analysis,algorithms,machine-learning,validation] | 2026-01-14 12:17 AM | 1
algorithmic-quantitative-trading | gemini | hot | hot/algorithmic-quantitative-trading.md | [trading,algorithms,quantitative,hft,backtesting,machine-learning,finance] | 2026-01-14 12:17 AM | 1
fundamental-analysis-trading | gemini | hot | hot/fundamental-analysis-trading.md | [fundamentals,trading,stocks,crypto,valuation,macroeconomics,earnings,screening] | 2026-01-14 12:18 AM | 1
trading-risk-management | gemini | hot | hot/trading-risk-management.md | [trading,risk-management,position-sizing,portfolio,risk-metrics,hedging] | 2026-01-14 12:18 AM | 1
market-microstructure | gemini | hot | hot/market-microstructure.md | [trading,microstructure,order-book,liquidity,market-making,execution] | 2026-01-14 12:18 AM | 1
sentiment-analysis-trading | gemini | hot | hot/sentiment-analysis-trading.md | [sentiment,trading,nlp,alternatives,indicators,strategy,crypto,integration,api,framework] | 2026-01-14 12:18 AM | 1
forex-trading | gemini | hot | hot/forex-trading.md | [forex,currencies,leverage,trading-strategies,carry-trade,economic-indicators,market-structure] | 2026-01-14 12:18 AM | 1
trading-psychology-behavioral-finance | gemini | hot | hot/trading-psychology-behavioral-finance.md | [trading,psychology,behavioral-finance,cognition,emotions,biases,trader-mindset,risk-management] | 2026-01-14 12:19 AM | 1
backtesting-strategy-validation | gemini | hot | hot/backtesting-strategy-validation.md | [backtesting,trading-strategy,validation,quantitative-finance,performance-metrics] | 2026-01-14 12:19 AM | 1
scalping-ultra-short-term-trading | gemini | hot | hot/scalping-ultra-short-term-trading.md | [scalping,trading,ultra-short-term,order-flow,technical-analysis,risk-management] | 2026-01-14 12:19 AM | 1
position-trading-long-term-investing | gemini | hot | hot/position-trading-long-term-investing.md | [trading,investing,position-trading,long-term,fundamentals,technicals,portfolio,crypto] | 2026-01-14 12:19 AM | 1
futures-derivatives-comprehensive | gemini | hot | hot/futures-derivatives-comprehensive.md | [futures,derivatives,commodities,crypto,hedging,margin,contango,perpetuals] | 2026-01-14 12:19 AM | 1
volume-analysis-trading | gemini | hot | hot/volume-analysis-trading.md | [volume,trading,technicalanalysis,obv,vwap,marketprofile,accumulation,institutional] | 2026-01-14 01:05 AM | 1
momentum-indicators-trading | gemini | hot | hot/momentum-indicators-trading.md | [momentum,rsi,stochastic,cci,williams,mfi,divergence,oscillators,trading-signals] | 2026-01-14 01:05 AM | 1
candlestick-patterns | gemini | hot | hot/candlestick-patterns.md | [candlesticks,patterns,trading,technical-analysis,algorithmic-trading,forex,crypto,stocks] | 2026-01-14 01:05 AM | 1
volatility-indicators-comprehensive | gemini | hot | hot/volatility-indicators-comprehensive.md | [volatility,trading,indicators,technical-analysis,risk-management,ATR,Bollinger-Bands,VIX,position-sizing] | 2026-01-14 01:06 AM | 1
trading-chart-patterns | gemini | hot | hot/trading-chart-patterns.md | [trading,chart-patterns,technical-analysis,price-action,algorithms,risk-management] | 2026-01-14 01:06 AM | 1
trend-indicators-comprehensive | gemini | hot | hot/trend-indicators-comprehensive.md | [trend-analysis,moving-averages,MACD,ADX,Parabolic-SAR,Ichimoku,Supertrend,trading-signals,technical-analysis] | 2026-01-14 01:06 AM | 1
fibonacci-trading-methods | gemini | hot | hot/fibonacci-trading-methods.md | [fibonacci,trading,technical-analysis,levels,retracements,extensions,confluence] | 2026-01-14 01:06 AM | 1
backtesting-methods | gemini | hot | hot/backtesting-methods.md | [trading,backtesting,quantitative,algo-trading,risk,metrics,data-quality,bias] | 2026-01-14 01:06 AM | 1
elliott-wave-theory | gemini | hot | hot/elliott-wave-theory.md | [trading,elliott-wave,technical-analysis,wave-counting,fibonacci,market-patterns] | 2026-01-14 01:06 AM | 1
support-resistance-trading | gemini | hot | hot/support-resistance-trading.md | [trading,support,resistance,technical-analysis,market-structure,price-action,institutional,volume] | 2026-01-14 01:06 AM | 1
multi-timeframe-trading-analysis | gemini | hot | hot/multi-timeframe-trading-analysis.md | [trading,analysis,timeframes,fractal,confluence,technical-analysis] | 2026-01-14 01:07 AM | 1
price-action-trading | gemini | hot | hot/price-action-trading.md | [trading,price-action,market-structure,order-blocks,fvg,liquidity,bos,choch,ict,smc,candlesticks,trading,price-action,market-structure,order-blocks,fvg,liquidity,bos,choch,ict,smc,candlesticks,ai-trading] | 2026-01-14 01:08 AM | 2
options-strategies-basic | gemini | hot | hot/options-strategies-basic.md | [options,strategies,trading,hedging,income] | 2026-01-14 01:15 AM | 1
futures-fundamentals | gemini | hot | hot/futures-fundamentals.md | [futures,contracts,trading,markets,hedging,speculation,ES,NQ,CL,GC,ZB,margin,settlement] | 2026-01-14 01:15 AM | 1
options-spread-strategies | gemini | hot | hot/options-spread-strategies.md | [options,spreads,trading,derivatives,algorithms,risk-management,greeks,vertical,horizontal,diagonal,ratio,credit,debit] | 2026-01-14 01:15 AM | 1
options-greeks | gemini | hot | hot/options-greeks.md | [options,greeks,delta,gamma,theta,vega,trading,quantitative,derivatives,risk-management] | 2026-01-14 01:15 AM | 1
options-fundamentals-trading | gemini | hot | hot/options-fundamentals-trading.md | [options,trading,fundamentals,derivatives,calls,puts,strike,expiration,premium,moneyness,chains,assignment,exercise] | 2026-01-14 01:15 AM | 1
options-on-futures | gemini | hot | hot/options-on-futures.md | [options,futures,derivatives,trading,commodities,volatility,strategies] | 2026-01-14 01:15 AM | 1
advanced-options-strategies | gemini | hot | hot/advanced-options-strategies.md | [options,trading,strategies,iron-condor,butterflies,straddles,strangles,box-spreads,risk-management,greeks] | 2026-01-14 01:15 AM | 1
volatility-trading-options | gemini | hot | hot/volatility-trading-options.md | [volatility,options,trading,IV,HV,VIX,term-structure,vol-crush,arbitrage,market-making,forecasting] | 2026-01-14 01:15 AM | 1
market-maker-options-behavior | gemini | hot | hot/market-maker-options-behavior.md | [options,market-makers,gamma,delta-hedging,gex,dix,liquidity,trading-signals] | 2026-01-14 01:15 AM | 1
market-maker-options-behavior | gemini | hot | hot/market-maker-options-behavior.md | [options,market-makers,gamma,delta-hedging,gex,dix,liquidity,trading-signals] | 2026-01-14 01:16 AM | 1
options-flow-analysis | gemini | hot | hot/options-flow-analysis.md | [options,trading,flow,unusual-activity,smart-money,sweep-orders,institutional,dark-pools,delta-adjusted,sentiment,options,trading,flow,unusual-activity,smart-money,sweep-orders,institutional,dark-pools,delta-adjusted,sentiment,options,trading,flow,unusual-activity,smart-money,sweep-orders,institutional,dark-pools,delta-adjusted,sentiment,technical-analysis] | 2026-01-14 01:20 AM | 3
options-flow-complete | gemini | hot | hot/options-flow-complete.md | [options,trading,flow,institutional,smart-money,sweep-orders,delta-adjusted,dark-pools,signal-interpretation] | 2026-01-14 01:21 AM | 1
test-candlesticks-debug | gemini | hot | hot/test-candlesticks-debug.md | [test,debug,candlesticks] | 2026-01-14 01:24 AM | 1
video-frame-interpolation | gemini | hot | hot/video-frame-interpolation.md | [video,interpolation,slowmotion,ffmpeg,ai,rife,frame-synthesis] | 2026-01-14 02:58 AM | 1
term-frequency-ai-writing | gemini | hot | hot/term-frequency-ai-writing.md | [ai-writing,lexical-diversity,sensory-narrative,audio-production,llm-generation] | 2026-01-14 03:20 AM | 1
trading-llm-architecture | gemini | hot | hot/trading-llm-architecture.md | [trading,llm,architecture,multi-agent,apis,ensemble] | 2026-01-14 04:07 AM | 1
quantitative-trading-systems | gemini | hot | hot/quantitative-trading-systems.md | [quant-trading,vector-databases,machine-learning,financial-prediction,signal-processing] | 2026-01-14 04:07 AM | 1
sentiment-stock-prediction | gemini | hot | hot/sentiment-stock-prediction.md | [sentiment-analysis,stock-prediction,nlp,insider-trading,cross-domain-correlation,sentiment,stocks,nlp,insider,events,data-fusion] | 2026-01-14 04:07 AM | 2
trading-leading-indicators | gemini | hot | hot/trading-leading-indicators.md | [trading,signals,predictive,quant,equities,crypto,options,implementation] | 2026-01-14 05:03 AM | 1
self-improving-ai-systems | gemini | hot | hot/self-improving-ai-systems.md | [ai,curiosity,self-improvement,meta-learning,novelty,gamification,intrinsic-motivation,ai,curiosity,self-improvement,intrinsic-motivation,novelty,gamification,implementation] | 2026-01-14 05:06 AM | 3
balloon-twisting-market | gemini | hot | hot/balloon-twisting-market.md | [balloons,entertainment,market,pricing,designs] | 2026-01-14 05:07 AM | 1
context-optimization | gemini | hot | hot/context-optimization.md | [context,tokens,optimization,lazy-loading] | 2026-01-14 06:05 AM | 5
