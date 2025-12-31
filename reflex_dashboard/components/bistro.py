import reflex as rx
from ..state import State

def header_html():
    return """
    <div class="text-center space-y-2 mb-4 max-w-3xl mx-auto pt-2">
        <div class="inline-flex items-center space-x-2 bg-slate-900/80 border border-slate-700 rounded-full px-3 py-1 mb-2 shadow-xl backdrop-blur-sm">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span class="text-[0.65rem] font-mono text-slate-400">KITCHEN STATUS: <span class="text-emerald-400">OPERATIONAL</span></span>
        </div>
        
        <h1 class="text-3xl md:text-5xl font-serif text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-amber-400 to-amber-600 tracking-tight pb-1">
            The Analytics Bistro
        </h1>
        
        <p class="text-sm text-slate-400 font-light leading-relaxed">
            We don't just serve data. We cook it.
        </p>
    </div>
    """

def visual_html():
    return """
    <div class="w-full max-w-xs mb-6 relative svg-container group mx-auto">
        <svg viewBox="0 0 500 300" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto drop-shadow-2xl rounded-2xl overflow-hidden bg-slate-900/80 border border-slate-800 ring-1 ring-slate-700/50">
            <!-- Kitchen Background -->
            <rect x="0" y="0" width="500" height="300" fill="#0f172a" />
            <path d="M0,250 L500,250" stroke="#1e293b" stroke-width="2" />
            
            <!-- Code Elements (Floating in background) -->
            <text x="20" y="40" font-family="JetBrains Mono" font-size="10" fill="#334155" opacity="0.5">SELECT * FROM raw_data</text>
            <text x="350" y="60" font-family="JetBrains Mono" font-size="10" fill="#334155" opacity="0.5">import sklearn</text>
            <text x="40" y="100" font-family="JetBrains Mono" font-size="10" fill="#334155" opacity="0.5">df.groupby('user_id')</text>

            <!-- The Waiter (Robot) -->
            <g class="animate-float">
                <!-- Body -->
                <path d="M230,220 L270,220 L265,140 L235,140 Z" fill="#1e293b" stroke="#475569" stroke-width="2"/>
                <!-- Head -->
                <rect x="230" y="100" width="40" height="35" rx="6" fill="#cbd5e1"/>
                <rect x="238" y="110" width="8" height="8" rx="2" fill="#3b82f6" class="animate-pulse"/>
                <rect x="254" y="110" width="8" height="8" rx="2" fill="#3b82f6" class="animate-pulse" style="animation-delay: 0.5s"/>
                <!-- Bowtie -->
                <path d="M240,140 L260,140 L250,145 Z" fill="#f59e0b"/>
                
                <!-- Arm Holding Tray -->
                <g class="robot-arm">
                    <path d="M235,180 Q200,180 180,200" stroke="#94a3b8" stroke-width="6" fill="none"/>
                    <circle cx="180" cy="200" r="5" fill="#cbd5e1"/>
                </g>

                <!-- The Platter -->
                <g transform="translate(130, 200)">
                    <ellipse cx="50" cy="0" rx="60" ry="10" fill="#e2e8f0"/>
                    <!-- Holographic Chart Projection -->
                    <path d="M20,-5 L30,-30 L40,-15 L50,-45 L60,-20 L80,-60" fill="none" stroke="#f59e0b" stroke-width="2" stroke-dasharray="2 2">
                        <animate attributeName="stroke-dashoffset" from="100" to="0" dur="2s" repeatCount="indefinite" />
                    </path>
                    <circle cx="20" cy="-5" r="2" fill="#3b82f6"/>
                    <circle cx="80" cy="-60" r="3" fill="#10b981"/>
                    <!-- Mist -->
                    <path d="M30,-20 Q40,-30 50,-20" stroke="white" stroke-width="1" fill="none" opacity="0.3">
                        <animate attributeName="d" values="M30,-20 Q40,-30 50,-20; M30,-30 Q40,-40 50,-30" dur="2s" repeatCount="indefinite" />
                        <animate attributeName="opacity" values="0.3;0" dur="2s" repeatCount="indefinite" />
                    </path>
                </g>
            </g>
        </svg>
    </div>
    """

def menu_html():
    return """
    <h2 class="text-3xl font-serif text-slate-300 mb-8 border-b border-slate-800 pb-4 text-center">Today's Specials</h2>
    
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 w-full px-6">
        
        <!-- Dish 1: Demand Roast -->
        <div class="menu-card bg-slate-900 border border-slate-800 rounded-xl p-5 cursor-pointer group hover:border-amber-500/50 min-h-[180px] flex flex-col justify-between transition-all hover:scale-105">
            <div>
                <div class="flex justify-between items-start mb-3">
                    <div class="p-2 rounded bg-blue-500/10 text-blue-400 group-hover:bg-blue-500 group-hover:text-white transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                    </div>
                    <span class="text-[0.65rem] font-mono text-slate-500">HOT</span>
                </div>
                <h3 class="text-base font-serif font-bold text-slate-100 mb-1 leading-tight">Demand Roast</h3>
                <p class="text-[0.7rem] text-slate-400 mb-0 leading-snug">Predicting future stock needs.</p>
            </div>
            <div class="ingredients absolute inset-0 bg-slate-950/95 backdrop-blur-sm p-4 flex flex-col justify-center items-start border border-amber-500/30">
                <h4 class="text-amber-400 font-bold text-xs uppercase tracking-wider mb-2">Stack:</h4>
                <ul class="text-[0.7rem] font-mono text-slate-300 space-y-1"><li>> ARIMA</li><li>> Scikit-Learn</li><li>> History Data</li></ul>
            </div>
        </div>

        <!-- Dish 2: Cluster Curry -->
        <div class="menu-card bg-slate-900 border border-slate-800 rounded-xl p-5 cursor-pointer group hover:border-amber-500/50 min-h-[180px] flex flex-col justify-between transition-all hover:scale-105">
            <div>
                <div class="flex justify-between items-start mb-3">
                    <div class="p-2 rounded bg-purple-500/10 text-purple-400 group-hover:bg-purple-500 group-hover:text-white transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>
                    </div>
                    <span class="text-[0.65rem] font-mono text-slate-500">CHEF</span>
                </div>
                <h3 class="text-base font-serif font-bold text-slate-100 mb-1 leading-tight">Cluster Curry</h3>
                <p class="text-[0.7rem] text-slate-400 mb-0 leading-snug">RFM segmentation mix.</p>
            </div>
             <div class="ingredients absolute inset-0 bg-slate-950/95 backdrop-blur-sm p-4 flex flex-col justify-center items-start border border-amber-500/30">
                <h4 class="text-amber-400 font-bold text-xs uppercase tracking-wider mb-2">Stack:</h4>
                <ul class="text-[0.7rem] font-mono text-slate-300 space-y-1"><li>> K-Means</li><li>> RFM</li><li>> SQL</li></ul>
            </div>
        </div>

        <!-- Dish 3: Neural Nachos -->
        <div class="menu-card bg-slate-900 border border-slate-800 rounded-xl p-5 cursor-pointer group hover:border-amber-500/50 min-h-[180px] flex flex-col justify-between transition-all hover:scale-105">
            <div>
                <div class="flex justify-between items-start mb-3">
                    <div class="p-2 rounded bg-emerald-500/10 text-emerald-400 group-hover:bg-emerald-500 group-hover:text-white transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 1 3 3v2a3 3 0 0 1-3 3 3 3 0 0 1-3-3V5a3 3 0 0 1 3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
                    </div>
                    <span class="text-[0.65rem] font-mono text-slate-500">EXP</span>
                </div>
                <h3 class="text-base font-serif font-bold text-slate-100 mb-1 leading-tight">Neural Nachos</h3>
                <p class="text-[0.7rem] text-slate-400 mb-0 leading-snug">Deep fried AI layers.</p>
            </div>
             <div class="ingredients absolute inset-0 bg-slate-950/95 backdrop-blur-sm p-4 flex flex-col justify-center items-start border border-amber-500/30">
                <h4 class="text-amber-400 font-bold text-xs uppercase tracking-wider mb-2">Stack:</h4>
                <ul class="text-[0.7rem] font-mono text-slate-300 space-y-1"><li>> PyTorch</li><li>> Bayes</li><li>> Linear Alg</li></ul>
            </div>
        </div>

        <!-- Dish 4: Market Platter -->
        <div class="menu-card bg-slate-900 border border-slate-800 rounded-xl p-5 cursor-pointer group hover:border-amber-500/50 min-h-[180px] flex flex-col justify-between transition-all hover:scale-105">
            <div>
                <div class="flex justify-between items-start mb-3">
                    <div class="p-2 rounded bg-pink-500/10 text-pink-400 group-hover:bg-pink-500 group-hover:text-white transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
                    </div>
                    <span class="text-[0.65rem] font-mono text-slate-500">STD</span>
                </div>
                <h3 class="text-base font-serif font-bold text-slate-100 mb-1 leading-tight">Market Platter</h3>
                <p class="text-[0.7rem] text-slate-400 mb-0 leading-snug">Items bought together.</p>
            </div>
             <div class="ingredients absolute inset-0 bg-slate-950/95 backdrop-blur-sm p-4 flex flex-col justify-center items-start border border-amber-500/30">
                <h4 class="text-amber-400 font-bold text-xs uppercase tracking-wider mb-2">Stack:</h4>
                <ul class="text-[0.7rem] font-mono text-slate-300 space-y-1"><li>> Apriori</li><li>> CLV</li><li>> AOV</li></ul>
            </div>
        </div>

        <!-- Dish 5: Matrix Mousse -->
        <div class="menu-card bg-slate-900 border border-slate-800 rounded-xl p-5 cursor-pointer group hover:border-amber-500/50 min-h-[180px] flex flex-col justify-between transition-all hover:scale-105">
            <div>
                <div class="flex justify-between items-start mb-3">
                    <div class="p-2 rounded bg-cyan-500/10 text-cyan-400 group-hover:bg-cyan-500 group-hover:text-white transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 17l4-4 4 4 4-4"/></svg>
                    </div>
                    <span class="text-[0.65rem] font-mono text-slate-500">CORE</span>
                </div>
                <h3 class="text-base font-serif font-bold text-slate-100 mb-1 leading-tight">Matrix Mousse</h3>
                <p class="text-[0.7rem] text-slate-400 mb-0 leading-snug">Bedrock of data transforms.</p>
            </div>
             <div class="ingredients absolute inset-0 bg-slate-950/95 backdrop-blur-sm p-4 flex flex-col justify-center items-start border border-amber-500/30">
                <h4 class="text-amber-400 font-bold text-xs uppercase tracking-wider mb-2">Stack:</h4>
                <ul class="text-[0.7rem] font-mono text-slate-300 space-y-1"><li>> Vectors</li><li>> Eigenvals</li><li>> Dot Product</li></ul>
            </div>
        </div>

        <!-- Dish 6: Probable Pie -->
        <div class="menu-card bg-slate-900 border border-slate-800 rounded-xl p-5 cursor-pointer group hover:border-amber-500/50 min-h-[180px] flex flex-col justify-between transition-all hover:scale-105">
            <div>
                <div class="flex justify-between items-start mb-3">
                    <div class="p-2 rounded bg-orange-500/10 text-orange-400 group-hover:bg-orange-500 group-hover:text-white transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 12a4 4 0 1 0 8 0"/></svg>
                    </div>
                    <span class="text-[0.65rem] font-mono text-slate-500">MATH</span>
                </div>
                <h3 class="text-base font-serif font-bold text-slate-100 mb-1 leading-tight">Probable Pie</h3>
                <p class="text-[0.7rem] text-slate-400 mb-0 leading-snug">Uncertainty quantified.</p>
            </div>
             <div class="ingredients absolute inset-0 bg-slate-950/95 backdrop-blur-sm p-4 flex flex-col justify-center items-start border border-amber-500/30">
                <h4 class="text-amber-400 font-bold text-xs uppercase tracking-wider mb-2">Stack:</h4>
                <ul class="text-[0.7rem] font-mono text-slate-300 space-y-1"><li>> P-Values</li><li>> Bayesian</li><li>> Distrib.</li></ul>
            </div>
        </div>

        <!-- Dish 7: Prophet Pudding -->
        <div class="menu-card bg-slate-900 border border-slate-800 rounded-xl p-5 cursor-pointer group hover:border-amber-500/50 min-h-[180px] flex flex-col justify-between transition-all hover:scale-105">
            <div>
                <div class="flex justify-between items-start mb-3">
                    <div class="p-2 rounded bg-red-500/10 text-red-400 group-hover:bg-red-500 group-hover:text-white transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
                    </div>
                    <span class="text-[0.65rem] font-mono text-slate-500">FUTURE</span>
                </div>
                <h3 class="text-base font-serif font-bold text-slate-100 mb-1 leading-tight">Prophet Pudding</h3>
                <p class="text-[0.7rem] text-slate-400 mb-0 leading-snug">Automated trend spotting.</p>
            </div>
             <div class="ingredients absolute inset-0 bg-slate-950/95 backdrop-blur-sm p-4 flex flex-col justify-center items-start border border-amber-500/30">
                <h4 class="text-amber-400 font-bold text-xs uppercase tracking-wider mb-2">Stack:</h4>
                <ul class="text-[0.7rem] font-mono text-slate-300 space-y-1"><li>> Prophet</li><li>> Seasonality</li><li>> Trends</li></ul>
            </div>
        </div>

    </div>
    """

def ticker_html():
    return """
    <!-- Tech Stack Ticker -->
    <div class="w-full bg-slate-900 border-t border-slate-800 z-20 mt-12">
        <div class="ticker-wrap">
            <div class="ticker-move">
                <div class="ticker-item">PYTHON PANDAS INSTALLED</div>
                <div class="ticker-item text-amber-500">SQL ENGINE READY</div>
                <div class="ticker-item">LINEAR ALGEBRA LOADED</div>
                <div class="ticker-item text-blue-500">NEURAL NETWORKS ACTIVE</div>
                <div class="ticker-item">EXCEL PARSERS STANDING BY</div>
                <div class="ticker-item text-purple-500">BAYESIAN PROBABILITY: HIGH</div>
                <div class="ticker-item">CLUSTERING ALGORITHMS: K-MEANS</div>
                <div class="ticker-item text-emerald-500">MARKET BASKET ANALYSIS: OPTIMIZED</div>
                <!-- Duplicate for seamless loop -->
                <div class="ticker-item">PYTHON PANDAS INSTALLED</div>
                <div class="ticker-item text-amber-500">SQL ENGINE READY</div>
                <div class="ticker-item">LINEAR ALGEBRA LOADED</div>
                <div class="ticker-item text-blue-500">NEURAL NETWORKS ACTIVE</div>
                <div class="ticker-item">EXCEL PARSERS STANDING BY</div>
                <div class="ticker-item text-purple-500">BAYESIAN PROBABILITY: HIGH</div>
                <div class="ticker-item">CLUSTERING ALGORITHMS: K-MEANS</div>
            </div>
        </div>
    </div>
    """

def bistro_component() -> rx.Component:
    return rx.box(
        # Background Grid (User provided background)
        rx.html("""<div class="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-20 pointer-events-none z-0"></div>"""),
        
        rx.vstack(
            rx.html(header_html()),
            rx.html(visual_html()),
            rx.html(menu_html()),
            
            # The Interactive Button
            rx.button(
                rx.hstack(
                    rx.text("Enter the Kitchen", font_size="3xl", font_weight="900"),
                    rx.html("""<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5l7 7-7 7"/></svg>""")
                ),
                class_name="bg-emerald-500 hover:bg-emerald-600 text-slate-900 py-6 px-16 rounded-full transition-all shadow-xl hover:shadow-emerald-500/30 hover:scale-105 active:scale-95 flex items-center space-x-3 mt-12 cursor-pointer z-10 font-black tracking-wide border-2 border-emerald-400",
                on_click=State.dismiss_intro
            ),
            
            rx.html(ticker_html()),
            
            width="100%",
            align="center",
            spacing="0",
            position="relative",
            z_index="10"
        ),
        
        class_name="bg-slate-950 text-slate-100 min-h-screen flex flex-col font-sans selection:bg-amber-500 selection:text-white overflow-x-hidden w-full relative"
    )
