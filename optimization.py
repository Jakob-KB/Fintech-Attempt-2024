def optimize_bounds():
    from simulation import TradingEngine
    from algorithm import Algorithm
    from scipy.optimize import differential_evolution

    def objective(params):
        lower, upper = params
        # Enforce lower < upper; add a penalty if not.
        if lower >= upper:
            return 1e6 + (lower - upper) ** 2

        # Optionally, average over multiple runs to reduce noise:
        pnl_sum = 0
        n_runs = 3
        for _ in range(n_runs):
            engine = TradingEngine()
            # Create a config dictionary that includes both the bounds and indicator parameters.
            config = {
                "lower_bound": lower,
                "upper_bound": upper,
                "sma_window": 20,            # window for simple moving average
                "vol_window": 20,            # window for volatility (standard deviation)
                "volatility_multiplier": 1.0 # multiplier to scale volatility for dynamic thresholds
            }
            algo = Algorithm(positions=engine.positions, config=config)
            engine.run_algorithms(algo, output_daily_to_CLI=False)
            pnl_sum += float(engine.get_total_PnL())
        avg_pnl = pnl_sum / n_runs

        # We want to maximize PnL so we return negative PnL.
        return -avg_pnl

    # Callback to print performance at the end of each iteration.
    def callback(xk, convergence):
        lower, upper = xk
        current_pnl = -objective(xk)
        print(f"Current best: lower = {lower:.4f}, upper = {upper:.4f}, PnL = {current_pnl:.2f}")

    bounds = [(90, 110), (90, 110)]
    result = differential_evolution(
        objective, bounds,
        popsize=20,          # Increased population size
        maxiter=1000,        # Increased maximum iterations
        disp=True,
        polish=True,         # Try toggling this option if needed
        callback=callback
    )

    optimal_lower, optimal_upper = result.x
    max_pnl = -result.fun
    print("Optimal lower bound:", optimal_lower)
    print("Optimal upper bound:", optimal_upper)
    print("Maximum Total PnL:", max_pnl)

if __name__ == '__main__':
    optimize_bounds()
